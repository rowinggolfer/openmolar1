#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011, Neil Wallace <rowinggolfer@googlemail.com>               ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your OPTION) any later version.                                      ##
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

'''
Provides a Class for printing the GP17-1(Scotland) NHS form (front side)
'''
import os

from PyQt4 import QtCore, QtGui

from openmolar.backports.printed_form import PrintedForm
from openmolar.qt4gui.printing.gp17.gp17_config import gp17config

TEXTBOX_WIDTH = 15
PADDING = 2.5

RECTS = {}

# size of a box for a text field (ie character)
T_BOX = QtCore.QRectF(0,0, TEXTBOX_WIDTH, 16)
# size of a box for an X (ie check box)
C_BOX =  QtCore.QRectF(0,0, 14, 14)
# box for charting
CHART_BOX =  QtCore.QRectF(0,0, 13, 8)
# box for shading in
S_BOX =  QtCore.QRectF(0,0, 8, 10)


##sname boxes
pcde_box = 0
for i in range(14):
    x = 96 + i * (TEXTBOX_WIDTH + PADDING)
    
    RECTS["surname_%02d"% i] = T_BOX.translated(x,69)
    RECTS["forename_%02d"% i] = T_BOX.translated(x,95)
    RECTS["addr1_%02d"% i] = T_BOX.translated(x, 198)
    RECTS["addr2_%02d"% i] = T_BOX.translated(x, 224)
    RECTS["addr3_%02d"% i] = T_BOX.translated(x, 248)

    if i < 10:
        RECTS["chi_%02d"% i] = T_BOX.translated(x, 148)
    if 1 < i < 14:
        RECTS["prev_sno_%02d"% (i-2)] = T_BOX.translated(x, 175)        
    if i in (0,1,2,3,5,6,7):
        RECTS["pcde_%d"% pcde_box] = T_BOX.translated(x, 270)
        pcde_box += 1

##dob
for i, x in enumerate([66,84, 118,136,174,192,208,224]):
    y = 121
    RECTS["dob_%d"% i] = T_BOX.translated(x, y )

##sex
RECTS["male"] = T_BOX.translated(291, y)
RECTS["female"] = T_BOX.translated(324, y)

##dentists stamp box
RECTS["stampbox"] = QtCore.QRectF(440, 72, 272, 124)

for i, x in enumerate([544,562, 594,612, 643,661,679,697]):
    RECTS["accd_%02d"% i] = T_BOX.translated(x, 202)
    RECTS["cmpd_%02d"% i] = T_BOX.translated(x, 232)
    
for i, x in enumerate([552,570,588, 656,674,692]):
    RECTS["bpe_%02d"% i] = T_BOX.translated(x, 268)


left_x, right_x = 548, 696
for i, y in enumerate([302,340,360,380,408,432,452]):
    field = (
        "special_needs", "0111", "1011", "2772",
        "advice", "models", "trauma")[i]
        
    RECTS[field] = C_BOX.translated(right_x, y)

    if i == 0:
        pass
    elif i == 4:
        RECTS["rad_01"] = C_BOX.translated(left_x-18, y)
        RECTS["rad_02"] = C_BOX.translated(left_x, y)
    elif i == 6:
        RECTS["ref_01"] = C_BOX.translated(left_x-18, y)
        RECTS["ref_02"] = C_BOX.translated(left_x, y)
    else:
        field = (
            None, "0101", "1001", "2771",
            None, "rads_available", None )[i]

        RECTS[field] = C_BOX.translated(left_x, y)


#chart
for quadrant in range(1, 5):
    y = 356 if  quadrant < 3 else 370
    if quadrant in (2,3):
        x_offset = 206
        t_range = range(1,9) #Left teeth are in left to right order
    else:
        x_offset = 58
        t_range = range(8,0, -1) #reverse for the right side
    for i, toothno in enumerate(t_range):
        tooth = "chart_%s%s"% (quadrant, toothno)
        x = i * 17.5 + x_offset
        RECTS[tooth] = CHART_BOX.translated(x, y)
    
for quadrant in range(5, 9):
    y = 344 if  quadrant < 7 else 382
    if quadrant in (6,7):
        x_offset = 206
        t_range = range(1,6) #Left teeth are in left to right order
    else:
        x_offset = 112
        t_range = range(5,0, -1) #reverse for the right side
    for i, toothno in enumerate(t_range):
        tooth = "chart_%s%s"% (quadrant, toothno)
        x = i * 17.5 + x_offset
        RECTS[tooth] = CHART_BOX.translated(x, y)
        

RECTS["refused"] = C_BOX.translated(696, 902)
RECTS["pftr"] = C_BOX.translated(696, 930)

for row in range(9):
    y = 544 + row*25
    for i, x in enumerate([554,572,590,608,634,652]):
        RECTS["other%s_%02d"% (row, i)] = T_BOX.translated(x, y)
    RECTS["other_replacement_%02d"% row] = T_BOX.translated(696, y)

for i, x in enumerate([442, 460, 494, 512, 543, 561, 579, 597]):
    RECTS["dentist_sigdate_%02d"% i] = T_BOX.translated(x, 1014)

for i, x in enumerate([600,618,636,654,680,698]):
    RECTS["claim_total_%02d"% i] = T_BOX.translated(x, 772)


# tooth specific item section
for row in range(10):
    y = 446 + row*61.5
    for i, x in enumerate([22,40,58,76]):
        RECTS["item%s_code%02d"% (row+1, i)] = T_BOX.translated(x, y)

    RECTS["item%s_void"% (row+1)] = S_BOX.translated(82, y+24)

    #item chart
    for quadrant in range(1, 5):
        ty = y+1 if  quadrant < 3 else y+23
        if quadrant in (2,3):
            x_offset = 226
            t_range = range(1,9) #Left teeth are in left to right order
        else:
            x_offset = 98
            t_range = range(8,0, -1) #reverse for the right side
        for i, toothno in enumerate(t_range):
            tooth = "item%s_chart_%s%s"% (row+1, quadrant, toothno)
            x = i * 15 + x_offset
            RECTS[tooth] = S_BOX.translated(x, ty)
        
OPTION = QtGui.QTextOption(QtCore.Qt.AlignCenter)
        
class GP17iFront(PrintedForm):
    '''
    a class to set up and print a GP17 (tooth specific version)
    '''
    NAME = "GP17(1) Front"
    data = None
    unhandled_ts_codes = []
    unhandled_codes = []
    
    def __init__(self):
        PrintedForm.__init__(self)
        self.row = 1
        self.rects = RECTS
    
    @classmethod
    def is_active(self):
        return "neil" in os.path.expanduser("~") or \
            QtCore.QDate.currentDate() >= QtCore.QDate(2013,7,1)
    
    def set_data(self, data):
        self.data = data
        self.unhandled_ts_codes = []
        self.unhandled_codes = []
            
    def print_(self):
        self.set_offset(
            gp17config.GP17i_OFFSET_LEFT, gp17config.GP17i_OFFSET_TOP)
        self.set_scaling(gp17config.GP17i_SCALE_X, gp17config.GP17i_SCALE_Y) 
            
        painter = PrintedForm.print_(self)
        self._fill(painter)
        
    def _fill(self, painter):
        if self.data is None:
            return
            
        serifFont = QtGui.QFont("Courier", 12)
        serifFont.setBold(True)
        fm=QtGui.QFontMetrics(serifFont)
        serifLineHeight = fm.height()
        
        painter.setPen(QtGui.QPen(QtCore.Qt.black,1))
        painter.setFont(serifFont)

        for func_ in (
            self._fill_surname,
            self._fill_forename,
            self._fill_dob,
            self._fill_sex,
            self._fill_pid,
            self._fill_accd,
            self._fill_cmpd,
            self._fill_stampbox,
            self._fill_previous_surname,
            self._fill_address,            
            self._fill_charting,
            self._fill_bpe,            
            #self._fill_misc_cbs,
            self._fill_common_codes,
            self._fill_tooth_specific_codes,
            #self._fill_complex_codes
            self._fill_unhandled_codes,
            ):
            
            painter.save()
            #painter.translate(self.off_set)
            func_(painter)
            
            painter.restore()
        
    def _fill_surname(self, painter):
        for i in range(14):
            rect = self.rects["surname_%02d"% i]
            try:
                painter.drawText(rect, self.data.pt.sname[i], OPTION)
            except IndexError:
                break
        
    def _fill_forename(self, painter):
        for i in range(14):
            rect = self.rects["forename_%02d"% i]
            try:
                painter.drawText(rect, self.data.pt.fname[i], OPTION)
            except IndexError:
                break
    
    def _fill_dob(self, painter):
        for i in range(8):
            rect = self.rects["dob_%d"% i]
            try:
                painter.drawText(rect, self.data.dob[i], OPTION)
            except IndexError:
                break

    def _fill_sex(self, painter):
        sex = self.data.pt.sex 
        if sex=="M":
            painter.drawText(self.rects["male"], "M", OPTION)
        elif sex=="F":
            painter.drawText(self.rects["female"],"F", OPTION)
        else:
            print "UNKNOWN SEX for GP17!"
    
    def _fill_pid(self, painter):
        for i in range(10):
            rect = self.rects["chi_%02d"% i]
            try:
                painter.drawText(rect, self.data.identifier[i], OPTION)
            except IndexError:
                break

    def _fill_previous_surname(self, painter):
        for i in range(10):
            rect = self.rects["prev_sno_%02d"% i]
            try:
                painter.drawText(rect, self.data.previous_sname[i], OPTION)
            except IndexError:
                break

    def _fill_stampbox(self, painter):        
        painter.drawText(self.rects["stampbox"], self.data.stamp_text)
    
    def _fill_address(self, painter):
        for i in range(14):
            rect = self.rects["addr1_%02d"% i]
            try:
                painter.drawText(rect, self.data.addr1[i], OPTION)
            except IndexError:
                break

        for i in range(14):
            rect = self.rects["addr2_%02d"% i]
            try:
                painter.drawText(rect, self.data.addr2[i], OPTION)
            except IndexError:
                break

        for i in range(14):
            rect = self.rects["addr3_%02d"% i]
            try:
                painter.drawText(rect, self.data.addr3[i], OPTION)
            except IndexError:
                break

        for i in range(7):
            rect = self.rects["pcde_%d"% i]
            try:
                painter.drawText(rect, self.data.pcde[i], OPTION)
            except IndexError:
                break

    def _fill_accd(self, painter):
        for i in range(8):
            rect = self.rects["accd_%02d"% i]
            try:
                painter.drawText(rect, self.data.accd[i], OPTION)
            except IndexError:
                break
                
    def _fill_cmpd(self, painter):
        for i in range(8):
            rect = self.rects["cmpd_%02d"% i]
            try:
                painter.drawText(rect, self.data.cmpd[i], OPTION)
            except IndexError:
                break
            
    def _fill_charting(self, painter):
        if not self.data.show_chart:
            return
        painter.save()
        painter.setBrush(QtGui.QBrush(QtCore.Qt.black))
        for quadrant in range(1,9):
            for tooth in range(1,9):
                if quadrant > 4 and tooth > 5:
                    continue
                if not self.data.tooth_present(quadrant, tooth):
                    tooth_id = "%s%s"% (quadrant, tooth)
                    rect = self.rects["chart_%s"% tooth_id]
                    painter.drawRect(rect.adjusted(0,2,0,-2))
        painter.restore()
    
    def _fill_bpe(self, painter):
        for i in range(6):
            rect = self.rects["bpe_%02d"% i]
            try:
                painter.drawText(rect, self.data.bpe[i], OPTION)
            except IndexError:
                break

    
    def _fill_misc_cbs(self, painter):
        for key in ["on_referral", "not_extending", "special_needs","on_referral",
                    "radiographs","models","trauma"]:
            if self.data.misc_dict.get(key, False):
                rect = self.rects[key]
                painter.drawText(rect, "X", OPTION)
            
    def _fill_common_codes(self, painter):
        '''
        exams, perio, small xrays, special trays
        '''
        for code, number in self.data.common_codes.iteritems():
            if code == "0201":
                #small xrays could be multiple
                n_string = "%02d"% number
                try:
                    painter.drawText(
                        self.rects["rad_01"], n_string[0], OPTION) 
                    painter.drawText(
                        self.rects["rad_02"], n_string[1], OPTION)                 
                except KeyError:
                    print "unable to claim code %s"% code
            else:
                try:
                    painter.drawText(self.rects[code], "X", OPTION) 
                except KeyError:
                    print "unable to claim code %s"% code
                    
                    
    def _fill_tooth_specific_codes(self, painter):
        row = 1
        for code, teeth in self.data.tooth_specific_codes.iteritems():
            if row > 9:
                self.unhandled_ts_codes.appen(code)
                continue
            
            for i in range(4):                
                painter.drawText(
                    self.rects["item%s_code%02d"% (row,i)], code[i], OPTION) 
            
            painter.save()
            for tooth in teeth:
                painter.setBrush(QtGui.QBrush(QtCore.Qt.black))
                painter.drawRect(self.rects["item%s_chart_%s"% (row,tooth)])
            painter.restore()
            
            row += 1
            
    def _fill_complex_codes(self, painter):
         
        for code in self.data.complex_codes:
            if code.free_replace:
                other_treatment()
                continue
            try:
                n = "%02d"% code.number
                painter.drawText(self.rects["%sa"% code.code], n[0], OPTION) 
                painter.drawText(self.rects["%sb"% code.code], n[1], OPTION) 
            except KeyError:
                other_treatment()
        
        
    def _fill_unhandled_codes(self, painter):
        for item in self.unhandled_ts_codes:
            print "unhandled tooth specific code", item            
        for item in self.unhandled_codes:
            print "unhandled item code", item            
            
if __name__ == "__main__":
    os.chdir(os.path.expanduser("~")) # for print to file

    from openmolar.settings import localsettings
    from openmolar.dbtools.gp17_data import Gp17Data

    data = Gp17Data(testing_mode=True)

    app = QtGui.QApplication([])
    form = GP17iFront()
   
    form.set_data(data)
    
    form.testing_mode = True

    TEST_IMAGE = os.path.join(localsettings.resources_location,
        "gp17-1", "front.png")
    
    form.print_background = True
    form.BACKGROUND_IMAGE = TEST_IMAGE
   
    form.controlled_print()
    
    for key in sorted(form.rects.keys()):
        #print key, form.rects[key]
        pass
