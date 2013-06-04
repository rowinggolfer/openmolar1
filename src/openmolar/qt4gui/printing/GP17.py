# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtCore,QtGui
from openmolar.settings import localsettings

textBoxWidth = 16
textBoxHeight = 21

checkBoxWidth = 16
checkBoxHeight = 16

##sname boxes
snameboxLeft = 94
snameboxTop = 28   
snameboxPad = 3.1

##sname boxes
fnameboxLeft = 94
fnameboxTop = 60
fnameboxPad = 3.1

##dob
dobd1boxLeft = 66
dobd2boxLeft = 85
dobm1boxLeft = 123
dobm2boxLeft = 142
doby1boxLeft = 180
doby2boxLeft = 199
doby3boxLeft = 217
doby4boxLeft = 236
dobboxTop = 93

##sex
maleboxLeft = 304
femaleboxLeft = 341
sexTop = 93

##patient identifier
pidboxLeft = 133
pidTop = 124
pidPad = 3
pidBigPad = 8

##previous sname boxes
pnameboxLeft = 133
pnameboxTop = 157
pnameboxPad = 3.1

##dentists stamp box
stampboxLeft = 426
stampboxTop = 42
stampboxWidth = 292
stampboxHeight = 132

##address
addressLeft = 16
addressPad = 3
address1Top = 216
address2Top = 244
address3Top = 272

##postcodePart1
postcode1Left = 92
postcode2Left = 187
postcodeTop = 304
postcodePad = 3

##accept date
accdd1boxLeft = 540
accdd2boxLeft = 560
accdm1boxLeft = 591
accdm2boxLeft = 609
accdy1boxLeft = 640
accdy2boxLeft = 659
accdy3boxLeft = 678
accdy4boxLeft = 697
accdBoxTop = 185

##completiondate
cmpdBoxTop = 219

##treatmentonReferal/specialNeeds/registration
misccbsLeft = 697
misccbs1Top = 260
misccbs2Top = 290
misccbs3Top = 316

class gp17():
    '''
    a class to set up and print a GP17
    '''
    def __init__(self, pt, dentist, parent, testtingMode=False):
        self.printer = QtGui.QPrinter()
        self.printer.setPageSize(QtGui.QPrinter.A4)
        #self.printer.setPaperSource(QtGui.QPrinter.Middle)  #set bin 2
        self.om_gui = parent
        self.pt = pt
        if dentist:
            self.dentist = dentist
        else:
            self.dentist = ""
        self.setStampText()
        self.OFFSETLEFT = localsettings.GP17_LEFT
        self.OFFSETTOP = localsettings.GP17_TOP
        self.sizes()
        self.detailed = False
        #-- if detailed, openmolar includes dates and treatment details, 
        #-- otherwise just the pt's address and the dentists details.
        self.testingMode = testtingMode
        
    def setOffset(self, x, y):
        self.OFFSETLEFT = x
        self.OFFSETTOP = y 
        self.sizes()       

    ###sizes
    def sizes(self):
        paperRect = self.printer.paperRect()  #get the paper size (in pixels)
        self.absWidth = paperRect.width()
        self.absHeight = paperRect.height()
        #print "paperRect width %d height %d"%(self.absWidth,self.absHeight)
        
        self.surnameBoxes = {}
        for i in range(14):
            self.surnameBoxes[i] = QtCore.QRectF(
            snameboxLeft+self.OFFSETLEFT+i*(textBoxWidth+snameboxPad),
            snameboxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)
            
        self.forenameBoxes={}
        for i in range(14):
            self.forenameBoxes[i]=QtCore.QRectF(
            fnameboxLeft+self.OFFSETLEFT+i*(textBoxWidth+fnameboxPad),
            fnameboxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)
        
        self.dobBoxes={}
        self.dobBoxes[0]=QtCore.QRectF(dobd1boxLeft+self.OFFSETLEFT,
        dobboxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)
        
        self.dobBoxes[1]=QtCore.QRectF(dobd2boxLeft+self.OFFSETLEFT,
        dobboxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.dobBoxes[2]=QtCore.QRectF(dobm1boxLeft+self.OFFSETLEFT,
        dobboxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.dobBoxes[3]=QtCore.QRectF(dobm2boxLeft+self.OFFSETLEFT,
        dobboxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.dobBoxes[4]=QtCore.QRectF(doby1boxLeft+self.OFFSETLEFT,
        dobboxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.dobBoxes[5]=QtCore.QRectF(doby2boxLeft+self.OFFSETLEFT,
        dobboxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.dobBoxes[6]=QtCore.QRectF(doby3boxLeft+self.OFFSETLEFT,
        dobboxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.dobBoxes[7]=QtCore.QRectF(doby4boxLeft+self.OFFSETLEFT,
        dobboxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.maleBox=QtCore.QRectF(maleboxLeft+self.OFFSETLEFT,
        sexTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.femaleBox=QtCore.QRectF(femaleboxLeft+self.OFFSETLEFT,
        sexTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)
        
        self.pidBoxes={}
        for i in range(10):
            if i<3:
                self.pidBoxes[i]=QtCore.QRectF(
                pidboxLeft+self.OFFSETLEFT+i*(textBoxWidth+pidPad),
                pidTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)
            else:
                self.pidBoxes[i]=QtCore.QRectF(
                pidboxLeft+self.OFFSETLEFT+pidBigPad+i*(textBoxWidth+pidPad),
                pidTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)
        
        self.pnameBoxes={}

        for i in range(12):
            self.pnameBoxes[i]=QtCore.QRectF(
            pnameboxLeft+self.OFFSETLEFT+i*(textBoxWidth+pnameboxPad),
            pnameboxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)
        
        self.stampBox=QtCore.QRectF(stampboxLeft+self.OFFSETLEFT,
        stampboxTop+self.OFFSETTOP,stampboxWidth,stampboxHeight)
        
        self.address1Boxes={}
        for i in range(18):
            self.address1Boxes[i]=QtCore.QRectF(
            addressLeft+self.OFFSETLEFT+i*(textBoxWidth+addressPad),
            address1Top+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.address2Boxes={}
        for i in range(18):
            self.address2Boxes[i]=QtCore.QRectF(
            addressLeft+self.OFFSETLEFT+i*(textBoxWidth+addressPad),
            address2Top+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.address3Boxes={}
        for i in range(18):
            self.address3Boxes[i]=QtCore.QRectF(
            addressLeft+self.OFFSETLEFT+i*(textBoxWidth+addressPad),
            address3Top+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.postcode1Boxes={}
        for i in range(4):
            self.postcode1Boxes[i]=QtCore.QRectF(
            postcode1Left+self.OFFSETLEFT+i*(textBoxWidth+postcodePad),
            postcodeTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.postcode2Boxes={}
        for i in range(3):
            self.postcode2Boxes[i]=QtCore.QRectF(
            postcode2Left+self.OFFSETLEFT+i*(textBoxWidth+postcodePad),
            postcodeTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.accdBoxes={}
        self.accdBoxes[0]=QtCore.QRectF(
        accdd1boxLeft+self.OFFSETLEFT,accdBoxTop+self.OFFSETTOP,
        textBoxWidth,textBoxHeight)

        self.accdBoxes[1]=QtCore.QRectF(
        accdd2boxLeft+self.OFFSETLEFT,accdBoxTop+self.OFFSETTOP,
        textBoxWidth,textBoxHeight)

        self.accdBoxes[2]=QtCore.QRectF(accdm1boxLeft+self.OFFSETLEFT,
        accdBoxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.accdBoxes[3]=QtCore.QRectF(accdm2boxLeft+self.OFFSETLEFT,
        accdBoxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.accdBoxes[4]=QtCore.QRectF(accdy1boxLeft+self.OFFSETLEFT,
        accdBoxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.accdBoxes[5]=QtCore.QRectF(accdy2boxLeft+self.OFFSETLEFT,
        accdBoxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.accdBoxes[6]=QtCore.QRectF(accdy3boxLeft+self.OFFSETLEFT,
        accdBoxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.accdBoxes[7]=QtCore.QRectF(accdy4boxLeft+self.OFFSETLEFT,
        accdBoxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.cmpdBoxes={}

        self.cmpdBoxes[0]=QtCore.QRectF(accdd1boxLeft+self.OFFSETLEFT,
        cmpdBoxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.cmpdBoxes[1]=QtCore.QRectF(accdd2boxLeft+self.OFFSETLEFT,
        cmpdBoxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.cmpdBoxes[2]=QtCore.QRectF(accdm1boxLeft+self.OFFSETLEFT,
        cmpdBoxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.cmpdBoxes[3]=QtCore.QRectF(accdm2boxLeft+self.OFFSETLEFT,
        cmpdBoxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.cmpdBoxes[4]=QtCore.QRectF(accdy1boxLeft+self.OFFSETLEFT,
        cmpdBoxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.cmpdBoxes[5]=QtCore.QRectF(accdy2boxLeft+self.OFFSETLEFT,
        cmpdBoxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.cmpdBoxes[6]=QtCore.QRectF(accdy3boxLeft+self.OFFSETLEFT,
        cmpdBoxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.cmpdBoxes[7]=QtCore.QRectF(accdy4boxLeft+self.OFFSETLEFT,
        cmpdBoxTop+self.OFFSETTOP,textBoxWidth,textBoxHeight)

        self.miscCBS={}
        self.miscCBS[0]=QtCore.QRectF(misccbsLeft+self.OFFSETLEFT,
        misccbs1Top+self.OFFSETTOP,checkBoxWidth,checkBoxHeight)

        self.miscCBS[1]=QtCore.QRectF(misccbsLeft+self.OFFSETLEFT,
        misccbs2Top+self.OFFSETTOP,checkBoxWidth,checkBoxHeight)

        self.miscCBS[2]=QtCore.QRectF(misccbsLeft+self.OFFSETLEFT,
        misccbs3Top+self.OFFSETTOP,checkBoxWidth,checkBoxHeight)
        
    def print_(self):
        if not localsettings.defaultPrinterforGP17:
            dialog = QtGui.QPrintDialog(self.printer, self.om_gui)
            if not dialog.exec_():
                return False
        print "printing GP17 with offset (%d,%d)"%(
        self.OFFSETLEFT,self.OFFSETTOP)

        print "printer paper source = ",self.printer.paperSource()

        serifFont = QtGui.QFont("Courier", 12)
        serifFont.setBold(True)
        fm=QtGui.QFontMetrics(serifFont)
        serifLineHeight = fm.height()
        painter = QtGui.QPainter(self.printer)
        painter.setPen(QtGui.QPen(QtCore.Qt.black,1))
        painter.setFont(serifFont)

        option = QtGui.QTextOption(
        QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
        
        #if self.testingMode : painter.drawRect(self.outerRect)
        i=0
        for rect in self.surnameBoxes.values():
            if self.testingMode : painter.drawRect(rect)
            if len(self.pt.sname)>i:
                painter.drawText(rect,self.pt.sname[i],option)
            i+=1
        
        i=0
        for rect in self.forenameBoxes.values():
            if self.testingMode : painter.drawRect(rect)
            if len(self.pt.fname)>i:
                painter.drawText(rect,self.pt.fname[i],option)
            i+=1

        i=0
        gpdate=localsettings.GP17formatDate(self.pt.dob)
        for rect in self.dobBoxes.values():
            if self.testingMode : painter.drawRect(rect)
            painter.drawText(rect,gpdate[i],option)
            i+=1

        if self.testingMode : painter.drawRect(self.maleBox)
        if self.pt.sex=="M":painter.drawText(self.maleBox,"M",option)
        
        if self.testingMode : painter.drawRect(self.femaleBox)
        if self.pt.sex=="F":painter.drawText(self.femaleBox,"F",option)

        for rect in self.pidBoxes.values():
           if self.testingMode : painter.drawRect(rect)
        print "patient identifier not implemented"

        i=0
        for rect in self.pnameBoxes.values():
            if self.testingMode : painter.drawRect(rect)
            if len(self.pt.psn)>i:
                painter.drawText(rect,self.pt.psn[i],option)
            i+=1
            
        if self.testingMode : painter.drawRect(self.stampBox) #stampbox
        painter.drawText(self.stampBox,self.stampText)
        
        i=0
        for rect in self.address1Boxes.values():
            if self.testingMode : painter.drawRect(rect)
            if len(self.pt.addr1)>i:
                painter.drawText(rect,self.pt.addr1[i],option)
            i+=1
        i=0
        for rect in self.address2Boxes.values():
            if self.testingMode : painter.drawRect(rect)
            if len(self.pt.addr2)>i:
                painter.drawText(rect,self.pt.addr2[i],option)
            i+=1
        
        line3 = self.pt.addr3
        if line3 == "":
            line3 = self.pt.town
        
        i=0
        for rect in self.address3Boxes.values():
            if self.testingMode : painter.drawRect(rect)
            if len(line3)>i:
                painter.drawText(rect, line3[i],option)
            i+=1
        
        pcde=self.pt.pcde.strip()
        if " " in pcde:
            pcde=pcde.replace(" ","")
        if len(pcde)>6:
            pcde1=pcde[:4]
        else:
            pcde1=pcde[:3]
        pcde=pcde[-3:]
        i=0
        for rect in self.postcode1Boxes.values():
            if self.testingMode : painter.drawRect(rect)
            if len(pcde1)>i:
                painter.drawText(rect,pcde1[i],option)
            i+=1
        i=0
        for rect in self.postcode2Boxes.values():
            if self.testingMode : painter.drawRect(rect)
            if len(pcde)>i:
                painter.drawText(rect,pcde[i],option)
            i+=1
        if self.detailed:
            ##TODO - add all the other fields here, not just accd and cmpd
            i=0
            gpdate=localsettings.GP17formatDate(self.pt.accd)
            for rect in self.accdBoxes.values():
                if self.testingMode : painter.drawRect(rect)
                painter.drawText(rect,gpdate[i],option)
                i+=1
            i=0
            gpdate=localsettings.GP17formatDate(self.pt.cmpd)
            for rect in self.cmpdBoxes.values():
                if self.testingMode : painter.drawRect(rect)
                painter.drawText(rect,gpdate[i],option)
                i+=1
        for rect in self.miscCBS.values():
            if self.testingMode : painter.drawRect(rect)
        
        return True
        
    def setStampText(self):
        '''
        sets the dentist details for the top right of the form
        '''
        try:
            self.stampText = localsettings.dentDict[self.dentist][2]+"\n"
        except KeyError:
            print "Key Error getting dentist",self.dentist
            self.stampText = "\n"
        for line in localsettings.practiceAddress:
            self.stampText += line+"\n"
        try:
            self.stampText += localsettings.dentDict[self.dentist][3]
        except KeyError:
            self.stampText += ""
            
if __name__ == "__main__":
    import sys
    localsettings.initiate()
    from openmolar.dbtools import patient_class
    
    app = QtGui.QApplication(sys.argv)
    form=gp17(patient_class.patient(1), 4, None, True)
    form.print_()
