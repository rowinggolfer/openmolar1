# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtCore,QtGui
from openmolar.settings import localsettings

######################use for global changes##########
offsetLeft=15
offsetTop=15

##############################################

textBoxWidth=16
textBoxHeight=21

checkBoxWidth=16
checkBoxHeight=16

##sname boxes
snameboxLeft = offsetLeft + 94
snameboxTop = offsetTop + 28   #28
snameboxPad=3.1

##sname boxes
fnameboxLeft = offsetLeft + 94
fnameboxTop = offsetTop + 60
fnameboxPad=3.1

##dob
dobd1boxLeft = offsetLeft + 66
dobd2boxLeft = offsetLeft + 85
dobm1boxLeft = offsetLeft + 123
dobm2boxLeft = offsetLeft + 142
doby1boxLeft = offsetLeft + 180
doby2boxLeft = offsetLeft + 199
doby3boxLeft = offsetLeft + 217
doby4boxLeft = offsetLeft + 236
dobboxTop = offsetTop + 93

##sex
maleboxLeft = offsetLeft + 304
femaleboxLeft = offsetLeft + 341
sexTop = offsetTop + 93

##patient identifier
pidboxLeft = offsetLeft + 133
pidTop = offsetTop + 124
pidPad=3
pidBigPad=8

##previous sname boxes
pnameboxLeft = offsetLeft + 133
pnameboxTop = offsetTop + 157
pnameboxPad=3.1

##dentists stamp box
stampboxLeft = offsetLeft + 426
stampboxTop = offsetTop + 42
stampboxWidth=292
stampboxHeight=132

##address
addressLeft = offsetLeft + 16
addressPad=3
address1Top = offsetTop + 216
address2Top = offsetTop + 244
address3Top = offsetTop + 272

##postcodePart1
postcode1Left = offsetLeft + 92
postcode2Left = offsetLeft + 187
postcodeTop = offsetTop + 304
postcodePad=3

##accept date
accdd1boxLeft = offsetLeft + 540
accdd2boxLeft = offsetLeft + 560
accdm1boxLeft = offsetLeft + 591
accdm2boxLeft = offsetLeft + 609
accdy1boxLeft = offsetLeft + 640
accdy2boxLeft = offsetLeft + 659
accdy3boxLeft = offsetLeft + 678
accdy4boxLeft = offsetLeft + 697
accdBoxTop = offsetTop + 185

##completiondate
cmpdBoxTop = offsetTop + 219

##treatmentonReferal/specialNeeds/registration
misccbsLeft = offsetLeft + 697
misccbs1Top = offsetTop + 260
misccbs2Top = offsetTop + 290
misccbs3Top = offsetTop + 316

class gp17():
    def __init__(self, pt, dentist, testtingMode=False, parent=None):
        self.printer = QtGui.QPrinter()
        self.printer.setPageSize(QtGui.QPrinter.A4)
        self.printer.setPaperSource(QtGui.QPrinter.Middle)  #set bin 2
        self.pt  =pt
        self.dentist = dentist
        self.setStampText()
        self.sizes()
        self.detailed = False
        #-- if detailed, openmolar includes dates and treatment details, 
        #-- otherwise just the pt's address and the dentists details.
        self.testingMode = testtingMode
    ###sizes
    def sizes(self):
        paperRect = self.printer.paperRect()  #get the paper size (in pixels)
        self.absWidth = paperRect.width()
        self.absHeight = paperRect.height()
        #print "paperRect width %d height %d"%(self.absWidth,self.absHeight)
        
        self.surnameBoxes = {}
        for i in range(14):
            self.surnameBoxes[i] = QtCore.QRectF(snameboxLeft+i*(textBoxWidth+snameboxPad),snameboxTop,textBoxWidth,textBoxHeight)
            
        self.forenameBoxes={}
        for i in range(14):
            self.forenameBoxes[i]=QtCore.QRectF(fnameboxLeft+i*(textBoxWidth+fnameboxPad),fnameboxTop,textBoxWidth,textBoxHeight)
        
        self.dobBoxes={}
        self.dobBoxes[0]=QtCore.QRectF(dobd1boxLeft,dobboxTop,textBoxWidth,textBoxHeight)
        self.dobBoxes[1]=QtCore.QRectF(dobd2boxLeft,dobboxTop,textBoxWidth,textBoxHeight)
        self.dobBoxes[2]=QtCore.QRectF(dobm1boxLeft,dobboxTop,textBoxWidth,textBoxHeight)
        self.dobBoxes[3]=QtCore.QRectF(dobm2boxLeft,dobboxTop,textBoxWidth,textBoxHeight)
        self.dobBoxes[4]=QtCore.QRectF(doby1boxLeft,dobboxTop,textBoxWidth,textBoxHeight)
        self.dobBoxes[5]=QtCore.QRectF(doby2boxLeft,dobboxTop,textBoxWidth,textBoxHeight)
        self.dobBoxes[6]=QtCore.QRectF(doby3boxLeft,dobboxTop,textBoxWidth,textBoxHeight)
        self.dobBoxes[7]=QtCore.QRectF(doby4boxLeft,dobboxTop,textBoxWidth,textBoxHeight)

        self.maleBox=QtCore.QRectF(maleboxLeft,sexTop,textBoxWidth,textBoxHeight)
        self.femaleBox=QtCore.QRectF(femaleboxLeft,sexTop,textBoxWidth,textBoxHeight)
        
        self.pidBoxes={}
        for i in range(10):
            if i<3:
                self.pidBoxes[i]=QtCore.QRectF(pidboxLeft+i*(textBoxWidth+pidPad),pidTop,textBoxWidth,textBoxHeight)
            else:
                self.pidBoxes[i]=QtCore.QRectF(pidboxLeft+pidBigPad+i*(textBoxWidth+pidPad),pidTop,textBoxWidth,textBoxHeight)
        self.pnameBoxes={}
        for i in range(12):
            self.pnameBoxes[i]=QtCore.QRectF(pnameboxLeft+i*(textBoxWidth+pnameboxPad),pnameboxTop,textBoxWidth,textBoxHeight)
        
        self.stampBox=QtCore.QRectF(stampboxLeft,stampboxTop,stampboxWidth,stampboxHeight)
        
        self.address1Boxes={}
        for i in range(18):
            self.address1Boxes[i]=QtCore.QRectF(addressLeft+i*(textBoxWidth+addressPad),address1Top,textBoxWidth,textBoxHeight)
        self.address2Boxes={}
        for i in range(18):
            self.address2Boxes[i]=QtCore.QRectF(addressLeft+i*(textBoxWidth+addressPad),address2Top,textBoxWidth,textBoxHeight)
        self.address3Boxes={}
        for i in range(18):
            self.address3Boxes[i]=QtCore.QRectF(addressLeft+i*(textBoxWidth+addressPad),address3Top,textBoxWidth,textBoxHeight)
        self.postcode1Boxes={}
        for i in range(4):
            self.postcode1Boxes[i]=QtCore.QRectF(postcode1Left+i*(textBoxWidth+postcodePad),postcodeTop,textBoxWidth,textBoxHeight)
        self.postcode2Boxes={}
        for i in range(3):
            self.postcode2Boxes[i]=QtCore.QRectF(postcode2Left+i*(textBoxWidth+postcodePad),postcodeTop,textBoxWidth,textBoxHeight)

        self.accdBoxes={}
        self.accdBoxes[0]=QtCore.QRectF(accdd1boxLeft,accdBoxTop,textBoxWidth,textBoxHeight)
        self.accdBoxes[1]=QtCore.QRectF(accdd2boxLeft,accdBoxTop,textBoxWidth,textBoxHeight)
        self.accdBoxes[2]=QtCore.QRectF(accdm1boxLeft,accdBoxTop,textBoxWidth,textBoxHeight)
        self.accdBoxes[3]=QtCore.QRectF(accdm2boxLeft,accdBoxTop,textBoxWidth,textBoxHeight)
        self.accdBoxes[4]=QtCore.QRectF(accdy1boxLeft,accdBoxTop,textBoxWidth,textBoxHeight)
        self.accdBoxes[5]=QtCore.QRectF(accdy2boxLeft,accdBoxTop,textBoxWidth,textBoxHeight)
        self.accdBoxes[6]=QtCore.QRectF(accdy3boxLeft,accdBoxTop,textBoxWidth,textBoxHeight)
        self.accdBoxes[7]=QtCore.QRectF(accdy4boxLeft,accdBoxTop,textBoxWidth,textBoxHeight)
        self.cmpdBoxes={}
        self.cmpdBoxes[0]=QtCore.QRectF(accdd1boxLeft,cmpdBoxTop,textBoxWidth,textBoxHeight)
        self.cmpdBoxes[1]=QtCore.QRectF(accdd2boxLeft,cmpdBoxTop,textBoxWidth,textBoxHeight)
        self.cmpdBoxes[2]=QtCore.QRectF(accdm1boxLeft,cmpdBoxTop,textBoxWidth,textBoxHeight)
        self.cmpdBoxes[3]=QtCore.QRectF(accdm2boxLeft,cmpdBoxTop,textBoxWidth,textBoxHeight)
        self.cmpdBoxes[4]=QtCore.QRectF(accdy1boxLeft,cmpdBoxTop,textBoxWidth,textBoxHeight)
        self.cmpdBoxes[5]=QtCore.QRectF(accdy2boxLeft,cmpdBoxTop,textBoxWidth,textBoxHeight)
        self.cmpdBoxes[6]=QtCore.QRectF(accdy3boxLeft,cmpdBoxTop,textBoxWidth,textBoxHeight)
        self.cmpdBoxes[7]=QtCore.QRectF(accdy4boxLeft,cmpdBoxTop,textBoxWidth,textBoxHeight)

        self.miscCBS={}
        self.miscCBS[0]=QtCore.QRectF(misccbsLeft,misccbs1Top,checkBoxWidth,checkBoxHeight)
        self.miscCBS[1]=QtCore.QRectF(misccbsLeft,misccbs2Top,checkBoxWidth,checkBoxHeight)
        self.miscCBS[2]=QtCore.QRectF(misccbsLeft,misccbs3Top,checkBoxWidth,checkBoxHeight)
        
    def print_(self):
        if not localsettings.defaultPrinterforGP17:
            dialog = QtGui.QPrintDialog(self.printer)
            if not dialog.exec_():
                return
        print "printing GP17 with offset (%d,%d)"%(offsetLeft,offsetTop)
        print "printer paper source = ",self.printer.paperSource()
        serifFont = QtGui.QFont("Courier", 12)
        serifFont.setBold(True)
        fm=QtGui.QFontMetrics(serifFont)
        serifLineHeight = fm.height()
        painter = QtGui.QPainter(self.printer)
        painter.setPen(QtGui.QPen(QtCore.Qt.black,1))
        painter.setFont(serifFont)
        option = QtGui.QTextOption(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)
        
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
            
        if self.testingMode : painter.drawRect(self.stampBox)                                           #stampbox
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
        i=0
        for rect in self.address3Boxes.values():
            if self.testingMode : painter.drawRect(rect)
            if len(self.pt.addr3)>i:
                painter.drawText(rect,self.pt.addr3[i],option)
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
        print "treatment on referral,special needs, cancel registration not implemented"
    def setStampText(self):
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
    localsettings.initiate(False)
    from openmolar.dbtools import patient_class
    
    app = QtGui.QApplication(sys.argv)
    form=gp17(patient_class.patient(29833),True)
    form.print_()
