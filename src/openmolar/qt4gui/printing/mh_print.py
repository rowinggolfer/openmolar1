#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2012-2013,  Neil Wallace <neil@openmolar.com>                  ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################


from __future__ import division
import datetime

from PyQt4 import QtCore,QtGui

from openmolar.settings import localsettings

MARGIN_LEFT = 25
MARGIN_RIGHT = 25
MARGIN_TOP = 20
MARGIN_BOTTOM = 30

#alter this to print rectangles
DEBUG = False

class MHPrint(object):
    '''
    A class to print the MH form for a patient
    '''
    def __init__(self, pt, parent):
        self.pt = pt
        self.parent = parent
        self.printer = QtGui.QPrinter()
        self.printer.setPageSize(QtGui.QPrinter.A4)
        col_width = 1
        
    def print_(self):
        '''
        print the MH form
        '''
        def bold_on(bold=True):
            font = painter.font()
            font.setBold(bold)
            painter.setFont(font)
        
        def bold_off():
            bold_on(False)

        def print_line(y, left=0, colspan=12):
            '''
            print a rectangle
            '''
            bottom_y = y + line_height
            left_point = QtCore.QPointF(MARGIN_LEFT + left*col_width, bottom_y)
            right_point = QtCore.QPointF(
                MARGIN_LEFT + (left +colspan) *col_width, bottom_y)            
            painter.drawLine(left_point, right_point)
            
        def print_text(text, y, left=0, colspan=12, rowspan=1,
        option=QtCore.Qt.AlignLeft):
            '''
            print the text in a box
            '''
            rect = QtCore.QRectF(
                MARGIN_LEFT + left*col_width, y, 
                colspan*col_width-5, line_height * rowspan
                )            
            if DEBUG:
                painter.drawRect(rect)
            text_option = QtGui.QTextOption(option|QtCore.Qt.AlignVCenter)
            text_option.setWrapMode(text_option.NoWrap)
            painter.drawText(rect, text, text_option)
            return line_height*rowspan # so that y can be adjusted accordingly
    
        dialog = QtGui.QPrintDialog(self.printer, self.parent)
        
        if not dialog.exec_():
            return
        
        page_width = self.printer.pageRect().width() - (
            MARGIN_LEFT + MARGIN_RIGHT)
        
        #use a 12 column grid
        col_width = page_width/12
        
        painter = QtGui.QPainter(self.printer)
        pen = QtGui.QPen(QtCore.Qt.black)
        pen.setWidth(2)
        painter.setPen(2)
        
        font = QtGui.QFont("sans", 14)
        font.setBold(True)
        painter.setFont(font)
        
        line_height = QtGui.QFontMetrics(painter.font()).height()
        padding = line_height/6
        
        y = MARGIN_TOP

        for value in localsettings.MH_HEADER:
            if not value:
                continue
            
            y += print_text(value, y, option=QtCore.Qt.AlignCenter)        
        
        print_line(y)
        
        y += 2*line_height
        
        painter.setFont(QtGui.QFont("sans", 9))
        line_height = QtGui.QFontMetrics(painter.font()).height()
        padding = line_height/3
        
        print_text(str(self.pt.serialno), MARGIN_TOP, 11,1)
        
        bold_on()

        y += print_text(_("PLEASE CHECK/COMPLETE THESE DETAILS"), y)
        y += padding
        section_bottom = y
        
        
        print_text(_("Address"), y, 0, colspan=2, option=QtCore.Qt.AlignRight)
        bold_off()
            
        for value in (
            self.pt.name,
            self.pt.addr1,
            self.pt.addr2,
            self.pt.addr3,
            self.pt.town,
            self.pt.county,
            self.pt.pcde):
            if value in (None, ""):
                continue
            
            y += print_text(value, y, 2, colspan=5)
            
        y = section_bottom #move back up to print next rows
        
        for field, value in (
            (_("Date of Birth"), localsettings.formatDate(self.pt.dob)),
            (_("Home tel"), self.pt.tel1),
            (_("Work tel"), self.pt.tel2),
            (_("Mobile"), self.pt.mobile),
            (_("Email"), self.pt.email1),
            (_("Alternate Email"), self.pt.email2),
            ):
            if (value in (None, "") 
            and field in (_("Work tel"),_("Alternate Email"))):
                continue
            
            bold_on()
            print_text(field, y, 7, colspan=2, option=QtCore.Qt.AlignRight)
            bold_off()
            y += print_text(value, y, 9, colspan=3)
        
        if section_bottom > y: 
            y = section_bottom 

        y += line_height
        print_line(y)
        y += 2*line_height

        bold_on()
        print_text(_("Please Circle"), y, 6, colspan=2, 
            option=QtCore.Qt.AlignCenter)
        y += print_text(_("Give Details"), y, 8, colspan=4)
        
        y += print_text(_("ARE YOU CURRENTLY?"), y, 0, colspan=6)
        y += padding
        bold_off()
        
        print_text(_("Taking any prescribed medicines?"), y, 0.5, 5.5)
        print_text(_("Yes"), y, 6, colspan=1, option=QtCore.Qt.AlignRight)
        print_text(_("No"), y, 7, colspan=1, option=QtCore.Qt.AlignLeft)
        
        for i in range(5):
            print_line(y, 8, 4)
            y += line_height + padding

        y += line_height
        print_text(_("Carrying a Medical Warning Card?"), y, 0.5, 5.5)
        print_line(y, 8, 4)
        print_text(_("Yes"), y, 6, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 7, colspan=1, option=QtCore.Qt.AlignLeft)
        y += padding
        
        if self.pt.sex == "F" and 13 < self.pt.ageYears < 55:
            print_text(_("Pregnant or Breast Feeding?"), y, 0.5, 5.5)
            print_line(y, 8, 4)
            print_text(_("Yes"), y, 6, colspan=1, option=QtCore.Qt.AlignRight)
            y += print_text(_("No"), y, 7, colspan=1, option=QtCore.Qt.AlignLeft)
            
        y += line_height
        bold_on()
        y += print_text(_("DO YOU SUFFER FROM?"), y, 0, colspan=6)
        y += padding
        bold_off()
        
        print_text(_("Yes"), y, 6, colspan=1, rowspan=2, option=QtCore.Qt.AlignRight)
        print_text(_("No"), y, 7, colspan=1, rowspan=2, option=QtCore.Qt.AlignLeft)
        y += print_text(_("Allergies to Any Medicines or Substances?"), y, 0.5, 5.5)
        print_line(y, 8, 4)
        y += print_text(_("eg. Penicillin, aspirin or latex."), y, 2, 4)
        
        y += padding
        
        print_text(_("Bronchitis, Asthma, other Chest Conditions?"), y, 0.5, 5.5)
        print_line(y, 8, 4)
        print_text(_("Yes"), y, 6, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 7, colspan=1, option=QtCore.Qt.AlignLeft)
        
        y += padding
        
        print_text(_("Yes"), y, 6, colspan=1, rowspan=2, option=QtCore.Qt.AlignRight)
        print_text(_("No"), y, 7, colspan=1, rowspan=2, option=QtCore.Qt.AlignLeft)
        y += print_text(_("Heart Problems, Angina, Blood pressure"), y, 0.5, 5.5)
        print_line(y, 8, 4)
        y += print_text(_("problems, or a stroke?"), y, 2, 4)

        y += padding
            
        print_text(_("Diabetes?"), y, 0.5, 5.5)
        print_line(y, 8, 4)
        print_text(_("Yes"), y, 6, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 7, colspan=1, option=QtCore.Qt.AlignLeft)
        
        y += padding
        
        print_text(_("Athritis?"), y, 0.5, 5.5)
        print_line(y, 8, 4)
        print_text(_("Yes"), y, 6, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 7, colspan=1, option=QtCore.Qt.AlignLeft)
        
        y += padding
        
        print_text(_("Yes"), y, 6, colspan=1, rowspan=2, option=QtCore.Qt.AlignRight)
        print_text(_("No"), y, 7, colspan=1, rowspan=2, option=QtCore.Qt.AlignLeft)
        y += print_text(_("Bruising or persistant bleeding after"), y, 0.5, 5.5)
        print_line(y, 8, 4)
        y += print_text(_("surgery or tooth extraction?"), y, 2, 4)
        
        y += padding
        
        print_text(_("Yes"), y, 6, colspan=1, rowspan=2, option=QtCore.Qt.AlignRight)
        print_text(_("No"), y, 7, colspan=1, rowspan=2, option=QtCore.Qt.AlignLeft)
        y += print_text(_("Any Infectious Diseases"), y, 0.5, 5.5)
        print_line(y, 8, 4)
        y += print_text(_("(including HIV and Hepatitis)?"), y, 2, 4)
                
        y += line_height
        bold_on()
        y += print_text(_("DID YOU, AS A CHILD OR SINCE HAVE"), y, 0, colspan=6)
        y += padding
        bold_off()
                
        print_text(_("Bacterial Endocarditis?"), y, 0.5, 5.5)
        print_line(y, 8, 4)
        print_text(_("Yes"), y, 6, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 7, colspan=1, option=QtCore.Qt.AlignLeft)
        
        y += padding
        
        print_text(_("Liver Disease (eg. Jaundice or Hepatitis)?"), y, 0.5, 5.5)
        print_line(y, 8, 4)
        print_text(_("Yes"), y, 6, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 7, colspan=1, option=QtCore.Qt.AlignLeft)
        
        y += padding
        
        print_text(_("A bad reaction to a Local or General Anaesthetic?"), y, 0.5, 5.5)
        print_line(y, 8, 4)
        print_text(_("Yes"), y, 6, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 7, colspan=1, option=QtCore.Qt.AlignLeft)
        
        y += padding
        
        print_text(_("A joint replacement or other implant?"), y, 0.5, 5.5)
        print_line(y, 8, 4)
        print_text(_("Yes"), y, 6, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 7, colspan=1, option=QtCore.Qt.AlignLeft)
        
        y += padding
        
        print_text(_("Heart Surgery?"), y, 0.5, 5.5)
        print_line(y, 8, 4)
        print_text(_("Yes"), y, 6, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 7, colspan=1, option=QtCore.Qt.AlignLeft)
        
        y += padding
        
        print_text(_("Brain Surgery?"), y, 0.5, 5.5)
        print_line(y, 8, 4)
        print_text(_("Yes"), y, 6, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 7, colspan=1, option=QtCore.Qt.AlignLeft)
        
        y += padding
        
        print_text(_("Yes"), y, 6, colspan=1, rowspan=2, option=QtCore.Qt.AlignRight)
        print_text(_("No"), y, 7, colspan=1, rowspan=2, option=QtCore.Qt.AlignLeft)
        y += print_text(_("Treatment that required you to be"), y, 0.5, 5.5)
        print_line(y, 8, 4)
        y += print_text(_("in Hospital?"), y, 2, 4)
        y += padding
        
        print_text(_("A close relative with Creutzfeldt Jacob Disease?"), y, 0.5, 5.5)
        print_line(y, 8, 4)
        print_text(_("Yes"), y, 6, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 7, colspan=1, option=QtCore.Qt.AlignLeft)


        y += line_height
        print_line(y)
        y += line_height*2
        bold_on()
        print_text(
_("PLEASE GIVE ANY OTHER DETAILS WHICH YOU THINK MAY BE RELEVANT TO YOUR DENTIST")
        , y)
        
        y = self.printer.pageRect().height() - MARGIN_BOTTOM
        
        print_text(_("Patient's Signature"), y, 0, 3)
        print_line(y, 3, 6)
        
        date_ = localsettings.formatDate(localsettings.currentDay())
        print_text(date_, y, 10, 2)
        
        
if __name__ == "__main__":
    #DEBUG = True
    localsettings.initiate()
    app = QtGui.QApplication([])    
    from openmolar.dbtools.patient_class import patient
    
    mw = QtGui.QWidget()
    pt = patient(19342)
    
    mh_print = MHPrint(pt, mw)
    mh_print.print_()
    
    