# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import math
import sys
from PyQt4 import QtCore, QtGui

from openmolar.settings import localsettings

DATE_FORMAT = "MMMM, yyyy"

def populateTree(om_gui, records):
    '''
    load the bulk mailing tree widget
    '''
    om_gui.ui.bulk_mailings_treeWidget.clear()
    headers = "letterno, serialno,title,fname,sname,dnt1,familyno," +\
    "dob,addr1,addr2,addr3,town,county,pcde,recd"
    om_gui.ui.bulk_mailings_treeWidget.setHeaderLabels(headers.split(","))
    om_gui.ui.bulk_mailings_treeWidget.setSortingEnabled(False)
    familyno = -1
    letterno = 0
    addr1 = ""
    highlighted = False
    for row in records:
        col = 0
        group = (familyno and familyno !=0 and row[5] == familyno and 
                    row[7] == addr1)
        
        if not group:
            letterno += 1
            parentItem = om_gui.ui.bulk_mailings_treeWidget 
        else:
            parentItem = previous_parent
            
        colList = [str(letterno)]
        for attr in row:
            if attr == None:
                attr = ""
            if col==4: #dentist no
                colList.append(localsettings.ops.get(attr,"??"))
            else:
                colList.append(str(attr))
            col+=1
    
        item = QtGui.QTreeWidgetItem(parentItem, colList)
                
        if item.parent() == None: #top level letter
            previous_parent = item
            highlighted = not highlighted
            if highlighted:
                bcolour = om_gui.ui.bulk_mailings_treeWidget.palette().base()
            else:
                bcolour = om_gui.ui.bulk_mailings_treeWidget.palette(
                ).alternateBase()
        for i in range(item.columnCount()):
            item.setBackground(i,bcolour)
                
        familyno = row[5]
        addr1 = row[7]
    om_gui.ui.bulk_mailings_treeWidget.setColumnWidth(0,75)
    for i in range(1,om_gui.ui.bulk_mailings_treeWidget.columnCount()):
        om_gui.ui.bulk_mailings_treeWidget.resizeColumnToContents(i)


def printViaQPainter(om_gui):
    dialog = QtGui.QPrintDialog(om_gui.printer, om_gui)
    if not dialog.exec_():
        return
    AddressMargin=80
    LeftMargin = 50
    TopMargin = 120
    sansFont = QtGui.QFont("Helvetica", 9)
    sansLineHeight = QtGui.QFontMetrics(sansFont).height()
    serifFont = QtGui.QFont("Times", 10)
    serifLineHeight = QtGui.QFontMetrics(serifFont).height()
    sigFont = QtGui.QFont("Lucida Handwriting",8)
    fm = QtGui.QFontMetrics(serifFont)
    DateWidth = fm.width(" September 99, 2999 ")
    painter = QtGui.QPainter(om_gui.printer)
    pageRect = om_gui.printer.pageRect()
    page = 1
    for recall in om_gui.recalls:  # <--- clearly this is wrong!!
        painter.save()
        painter.setPen(QtCore.Qt.black)
        x,y = AddressMargin,TopMargin
        painter.setFont(sansFont)
        painter.drawText(x, y, "%s %s %s"%(recall[0].title(),recall[1].title(),recall[2].title()))
        y += sansLineHeight
        for line in recall[6:11]:
            if line:
                painter.drawText(x, y, str(line).title()+",")
                y += serifLineHeight
        if recall[11]:
            painter.drawText(x, y, str(recall[11])+".")  #postcode
        y += serifLineHeight

        x,y=LeftMargin,(pageRect.height()*0.3)
        
        painter.drawText(x+250, y, om_gui.adate.toString(DATE_FORMAT))
        y += sansLineHeight
        painter.setFont(serifFont)
        y += serifLineHeight
        painter.drawText(x, y, _("Dear %s %s,") %(recall[0].title(),recall[2].title()))
        y += serifLineHeight*2
        painter.drawText(x, y, 
        _('We are writing to inform you that your dental examination is now due.'))
        y += serifLineHeight
        painter.drawText(x, y, _('Please contact the surgery to arrange an appointment. *'))
        y += serifLineHeight*1.2
        painter.drawText(x, y, _('We look forward to seeing you in the near future.'))
        painter.setPen(QtCore.Qt.black)
        y += serifLineHeight*2
        painter.drawText(x, y, _("Yours sincerely,"))
        y += serifLineHeight * 1.5
        painter.setFont(sigFont)
        y += serifLineHeight * 2            
        painter.drawText(x, y, "The Academy Dental Practice")
        painter.setFont(serifFont)
        
        y += serifLineHeight * 3
        painter.drawText(x, y, "P.S. we are pleased to announce that Sally Melville, our hygienist,"  )
        y += serifLineHeight 
        painter.drawText(x, y, 'had a baby boy, "Leo", on the 23rd September.')
        y += serifLineHeight 
        painter.drawText(x, y, 'Her maternity leave has reduced the availability of hygienist' )
        y += serifLineHeight 
        painter.drawText(x, y, 'appointments. We apologise for any invonvenience caused, and '   )
        y += serifLineHeight 
        painter.drawText(x, y, 'thankyou for your understanding.')            
        y = pageRect.height() - 120
        painter.drawLine(x, y, pageRect.width() - (2 * AddressMargin), y)
        y += 2
        font = QtGui.QFont("Helvetica", 7)
        font.setItalic(True)
        painter.setFont(font)
        font.setItalic(True)
        painter.setFont(font)
        option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
        option.setWrapMode(QtGui.QTextOption.WordWrap)
        footer = _('''* If you already have a future appointment with us -
please accept our apologies and ignore this letter.''')
        painter.drawText(QtCore.QRectF(x, y,
        pageRect.width() - (2 * AddressMargin), 31), footer, option)
        page += 1
        if page <= len(om_gui.recalls):
            om_gui.printer.newPage()
        painter.restore()

