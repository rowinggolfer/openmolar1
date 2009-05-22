# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.customwidgets import Ui_toothProps
from openmolar.qt4gui import colours
from openmolar.qt4gui.dialogs import Ui_crownChoice
from openmolar.settings import allowed

    
class tpWidget(Ui_toothProps.Ui_Form,QtGui.QWidget):
    def __init__(self,parent=None):
        super(tpWidget,self).__init__(parent)
        self.setupUi(self)
        hlayout=QtGui.QHBoxLayout(self.editframe)
        hlayout.setContentsMargins(0,0,0,0)
        self.lineEdit=chartLineEdit()
        self.lineEdit.setMaxLength(34) #as defined in the sql tables for a static entry - may exceed the plan stuff.... but I will validate that anyway.
        hlayout.addWidget(self.lineEdit)
        self.tooth=tooth()  #self.frame)
        self.toothlayout=QtGui.QHBoxLayout(self.frame)
        self.toothlayout.addWidget(self.tooth)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(colours.AMALGAM)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        self.am_pushButton.setPalette(palette)
        brush = QtGui.QBrush(colours.COMP)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        self.co_pushButton.setPalette(palette)
        brush = QtGui.QBrush(colours.GI)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        self.gl_pushButton.setPalette(palette)
        brush = QtGui.QBrush(colours.GOLD)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        self.gold_pushButton.setPalette(palette)
        brush = QtGui.QBrush(colours.PORC)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        self.porc_pushButton.setPalette(palette)
        self.signals()
        self.originalProps=""

    def setExistingProps(self,arg):
        if arg=="":
            self.originalProps=""
            self.lineEdit.setText("")
        else:
            arg=arg.strip()+":"
            arg=arg.replace(" ",":")
            self.originalProps=arg
            self.lineEdit.setText(arg)

    def clear(self):
        t=  str(self.lineEdit.text().toAscii())
        tlist=t.strip(":").split(":")
        print tlist
        t=""
        for props in tlist[:-1]:
            t+=props+":"
        print t
        self.lineEdit.setText(t)
        self.tooth.clear()
        self.tooth.update()
        self.finishedEdit() #doesn';t work!
    def checkEntry(self):
        currentFill=str(self.lineEdit.text().toAscii())
        fillList=currentFill.split(":")
        for f in fillList:
            if not self.checkProp(f):
                return False
        return True
    def checkProp(self,f):
        result=True
        if f!="":
            if self.tooth.isBacktooth and not (f in allowed.backToothCodes):
                result=False
            if not self.tooth.isBacktooth and not (f in allowed.frontToothCodes):
                result=False
            if f in allowed.treatment_only:
                result=True
        if not result:
            message="'%s' is not recognised - do you want to accept anyway?"%f
            input=QtGui.QMessageBox.question(self,"Confirm",message,QtGui.QMessageBox.No,QtGui.QMessageBox.Yes) 
            if input==QtGui.QMessageBox.Yes:
                result=True
            else:
                result=False
        return result
        
    def additional(self):
        existing=str(self.lineEdit.text().toAscii())
        if ":" in existing:
            colonPos=existing.rindex(":")
            keep=existing[:colonPos]
            currentFill=existing[colonPos+1:]
        else:
            currentFill=existing
        if currentFill=="":
            return
        if self.checkProp(currentFill):
            self.lineEdit.setText(existing+":")
            self.tooth.clear()
            self.tooth.update()
            self.finishedEdit()
            
    def updateSurfaces(self):
        existing=str(self.lineEdit.text().toAscii())
        if ":" in existing:                             #we have an existing filling/property in the tooth
            colonPos=existing.rindex(":")
            keep=existing[:colonPos+1]
            currentFill=existing[colonPos:]
        else:                                           #we don't
            keep=""
            currentFill=existing
        if "," in currentFill:                          #we have a material
            split=currentFill.split(",")
            mat=","+split[1]
            currentFill=self.tooth.filledSurfaces+mat
        elif "/" in currentFill:                        #we have a lab item
            split=currentFill.split("/")
            mat=split[0]+"/"
            currentFill=mat+self.tooth.filledSurfaces
        else:                                           #virgin tooth
            currentFill=self.tooth.filledSurfaces
        self.lineEdit.setText(keep+currentFill)
    def changeFillColour(self,arg):
        self.tooth.fillcolour=arg
        self.tooth.update()
    def plasticMaterial(self,arg):
        existing=str(self.lineEdit.text().toAscii())
        if ":" in existing:
            colonPos=existing.rindex(":")
            keep=existing[:colonPos+1]
            currentFill=existing[colonPos+1:]
        else:
            keep=""
            currentFill=existing
        if "," in currentFill: #already a material set! replace it.
            split=currentFill.split(",")
            surfaces=split[0]
            currentFill=surfaces+","+arg
        elif "/" in currentFill: #already has a lab item
            split=currentFill.split("/")
            surfaces=split[1]
            currentFill=surfaces+","+arg
        else:
            currentFill+=","+arg
        self.lineEdit.setText(keep+currentFill)
    def labMaterial(self,arg):
        existing=str(self.lineEdit.text().toAscii())
        if ":" in existing:
            colonPos=existing.rindex(":")
            keep=existing[:colonPos+1]
            currentFill=existing[colonPos+1:]
        else:
            keep=""
            currentFill=existing
        if "," in currentFill: #already a material set! replace it.
            split=currentFill.split(",")
            surfaces=split[0]
            currentFill=arg+"/"+surfaces
        elif "/" in currentFill: #already has a lab item
            split=currentFill.split("/")
            surfaces=split[1]
            currentFill=arg+"/"+surfaces
        else:
            currentFill=arg+"/"+currentFill
        self.lineEdit.setText(keep+currentFill)

    def am(self):
        self.changeFillColour(colours.AMALGAM)
        self.plasticMaterial("AM")
    def co(self):
        self.changeFillColour(colours.COMP)
        self.plasticMaterial("CO")
    def gl(self):
        self.changeFillColour(colours.GI)
        self.plasticMaterial("GL")
    def go(self):
        self.changeFillColour(colours.GOLD)
        self.labMaterial("GI")
    def pi(self):
        self.changeFillColour(colours.PORC)
        self.labMaterial("PI")

    def finishedEdit(self):
        newprops=str(self.lineEdit.text().toAscii())
        if newprops!=self.originalProps:
            newprops=newprops.replace(":"," ")
            if newprops!="" and newprops[-1]!=" ":
                newprops+=" "
            self.emit(QtCore.SIGNAL("Changed_Properties"),newprops)
        
    def keyNav(self,arg):
        if arg=="up":
            self.prevTooth()
        elif arg=="down":
            self.nextTooth()
    def leftTooth(self):
        if self.tooth.isUpper:
            self.prevTooth()
        else:
            self.nextTooth()
    def rightTooth(self):
        if not self.tooth.isUpper:
            self.prevTooth()
        else:
            self.nextTooth()
    def prevTooth(self):
        if self.checkEntry():
            self.finishedEdit()
            self.emit(QtCore.SIGNAL("NextTooth"),("up"))
    def nextTooth(self):
        if self.checkEntry():
            self.finishedEdit()
            self.emit(QtCore.SIGNAL("NextTooth"),("down"))
    def dec_perm(self):
        self.emit(QtCore.SIGNAL("FlipDeciduousState"))
    def at(self):
        self.lineEdit.setText("AT")
        self.nextTooth()
    def tm(self):
        self.lineEdit.setText("TM")
        self.nextTooth()
    def ex(self):
        self.lineEdit.setText("EX")
        self.nextTooth()
    def rt(self):
        existing=self.lineEdit.text()
        self.lineEdit.setText(existing+"RT")
        self.additional()
    def crown(self):
        def gold():
            self.lineEdit.setText(existing+"CR,GO")
            Dialog.accept()
        def pjc():
            self.lineEdit.setText(existing+"CR,PJ")
            Dialog.accept()
        def resin():
            self.lineEdit.setText(existing+"CR,A1")
            Dialog.accept()
        def lava():
            self.lineEdit.setText(existing+"CR,PJ")
            Dialog.accept()
        def fortress():
            self.lineEdit.setText(existing+"CR,PJ")
            Dialog.accept()
        def temp():
            self.lineEdit.setText(existing+"CR,T1")
            Dialog.accept()
        def other():
            self.lineEdit.setText(existing+"CR,OT")
            Dialog.accept()
        def bonded():
            self.lineEdit.setText(existing+"CR,V1")
            Dialog.accept()
            
        existing=self.lineEdit.text()
        Dialog = QtGui.QDialog(self)
        ccwidg = Ui_crownChoice.Ui_Dialog()
        ccwidg.setupUi(Dialog)
        ccwidg.gold.connect(ccwidg.gold,QtCore.SIGNAL("clicked()"), gold)
        ccwidg.gold.connect(ccwidg.pjc,QtCore.SIGNAL("clicked()"), pjc)
        ccwidg.gold.connect(ccwidg.other,QtCore.SIGNAL("clicked()"), other)
        ccwidg.gold.connect(ccwidg.lava,QtCore.SIGNAL("clicked()"), lava)
        ccwidg.gold.connect(ccwidg.fortress,QtCore.SIGNAL("clicked()"), fortress)
        ccwidg.gold.connect(ccwidg.bonded,QtCore.SIGNAL("clicked()"), bonded)
        ccwidg.gold.connect(ccwidg.temp,QtCore.SIGNAL("clicked()"), temp)
        ccwidg.gold.connect(ccwidg.resin,QtCore.SIGNAL("clicked()"), resin)
        
        if Dialog.exec_():
            self.nextTooth()

    def staticButPressed(self):
        self.emit(QtCore.SIGNAL("static"))
    def planButPressed(self):
        self.emit(QtCore.SIGNAL("plan"))
    def compButPressed(self):
        self.emit(QtCore.SIGNAL("completed"))

    def signals(self):
        QtCore.QObject.connect(self.am_pushButton,QtCore.SIGNAL("clicked()"), self.am)
        QtCore.QObject.connect(self.co_pushButton,QtCore.SIGNAL("clicked()"), self.co)
        QtCore.QObject.connect(self.gl_pushButton,QtCore.SIGNAL("clicked()"), self.gl)
        QtCore.QObject.connect(self.gold_pushButton,QtCore.SIGNAL("clicked()"), self.go)
        QtCore.QObject.connect(self.porc_pushButton,QtCore.SIGNAL("clicked()"), self.pi)
        QtCore.QObject.connect(self.tooth,QtCore.SIGNAL("toothSurface"), self.updateSurfaces) #user has clicked a surface
        QtCore.QObject.connect(self.clear_pushButton,QtCore.SIGNAL("clicked()"), self.clear)
        QtCore.QObject.connect(self.pushButton,QtCore.SIGNAL("clicked()"), self.additional)
        QtCore.QObject.connect(self.lineEdit,QtCore.SIGNAL("PySig"),self.keyNav)
        QtCore.QObject.connect(self.rightTooth_pushButton,QtCore.SIGNAL("clicked()"), self.rightTooth)
        QtCore.QObject.connect(self.leftTooth_pushButton,QtCore.SIGNAL("clicked()"), self.leftTooth)
        QtCore.QObject.connect(self.dec_pushButton,QtCore.SIGNAL("clicked()"), self.dec_perm)
        QtCore.QObject.connect(self.at_pushButton,QtCore.SIGNAL("clicked()"), self.at)
        QtCore.QObject.connect(self.tm_pushButton,QtCore.SIGNAL("clicked()"), self.tm)
        QtCore.QObject.connect(self.ex_pushButton,QtCore.SIGNAL("clicked()"), self.ex)
        QtCore.QObject.connect(self.rt_pushButton,QtCore.SIGNAL("clicked()"), self.rt)
        QtCore.QObject.connect(self.defaultCrown_pushButton,QtCore.SIGNAL("clicked()"), self.crown)
        QtCore.QObject.connect(self.static_pushButton,QtCore.SIGNAL("clicked()"), self.staticButPressed)
        QtCore.QObject.connect(self.plan_pushButton,QtCore.SIGNAL("clicked()"), self.planButPressed)
        QtCore.QObject.connect(self.comp_pushButton,QtCore.SIGNAL("clicked()"), self.compButPressed)

        ##fs_comboBox,cr_comboBox,endo_comboBox,ex_comboBox,static_comboBox,comments_comboBox


class tooth(QtGui.QWidget):
    def __init__(self,parent=None):
        super(tooth,self).__init__(parent)
        self.isBacktooth=True
        self.quadrant=1
        self.isUpper=True
        self.isRight=True
        self.setMouseTracking(True)
        self.shapes()
        self.clear()
    def sizeHint(self):
        return self.parent().size()
    def minimumSizeHint(self):
        return QtCore.QSize(80, 80)
    def setBacktooth(self,arg):
        if self.isBacktooth!=arg:
            self.isBacktooth=arg
            self.shapes()
    def setRightSide(self,arg):
        self.isRight=arg
    def setUpper(self,arg):
        self.isUpper=arg
    def clear(self):
        self.filledSurfaces=""
        if self.isBacktooth:
            self.fillcolour=colours.AMALGAM
        else:
            self.fillcolour=colours.COMP
    def sortSurfaces(self,arg):
        '''sort the filling surfaces to fit with conventional notation eg... MOD not DOM etc..'''
        retarg=""
        if "M" in arg:
            retarg+="M"
        if "D" in arg and not "M" in retarg:
            retarg+="D"
        if "O" in arg:
            retarg+="O"
        if "D" in arg and not "D" in retarg:
            retarg+="D"
        if "B" in arg:
            retarg+="B"
        if "P" in arg:
            retarg+="P"
        if "L" in arg:
            retarg+="L"
        if "I" in arg:
            retarg+="I"

        return retarg
    def setFilledSurfaces(self,arg):
        if arg in self.filledSurfaces:
            self.filledSurfaces=self.filledSurfaces.replace(arg,"")
        else:
            self.filledSurfaces+=arg
        self.filledSurfaces=self.sortSurfaces(self.filledSurfaces)
        self.update()
    def leaveEvent(self,event):
        self.mouseOverSurface=None
        self.update()
    def mouseMoveEvent(self,event):
        y=event.y()
        x=event.x()
        if self.mesial.containsPoint(QtCore.QPoint(x,y),QtCore.Qt.OddEvenFill):
            self.mouseOverSurface=self.mesial
            self.update()
        elif self.occlusal.containsPoint(QtCore.QPoint(x,y),QtCore.Qt.OddEvenFill):
            self.mouseOverSurface=self.occlusal
            self.update()
        elif self.distal.containsPoint(QtCore.QPoint(x,y),QtCore.Qt.OddEvenFill):
            self.mouseOverSurface=self.distal
            self.update()
        elif self.buccal.containsPoint(QtCore.QPoint(x,y),QtCore.Qt.OddEvenFill):
            self.mouseOverSurface=self.buccal
            self.update()
        elif self.palatal.containsPoint(QtCore.QPoint(x,y),QtCore.Qt.OddEvenFill):
            self.mouseOverSurface=self.palatal
            self.update()

    def mousePressEvent(self, event):
        y=event.y()
        x=event.x()
        if self.mesial.containsPoint(QtCore.QPoint(x,y),QtCore.Qt.OddEvenFill):
            if self.isRight:
                self.setFilledSurfaces("D")
            else:
                self.setFilledSurfaces("M")
        elif self.occlusal.containsPoint(QtCore.QPoint(x,y),QtCore.Qt.OddEvenFill):
            if self.isBacktooth:
                self.setFilledSurfaces("O")
            else:
                self.setFilledSurfaces("I")
        elif self.distal.containsPoint(QtCore.QPoint(x,y),QtCore.Qt.OddEvenFill):
            if not self.isRight:
                self.setFilledSurfaces("D")
            else:
                self.setFilledSurfaces("M")
        elif self.buccal.containsPoint(QtCore.QPoint(x,y),QtCore.Qt.OddEvenFill):
            if self.isUpper:
                self.setFilledSurfaces("B")
            else:
                self.setFilledSurfaces("L")
        elif self.palatal.containsPoint(QtCore.QPoint(x,y),QtCore.Qt.OddEvenFill):
            if self.isUpper:
                self.setFilledSurfaces("P")
            else:
                self.setFilledSurfaces("B")
        else:
            return #missed!!
        self.emit(QtCore.SIGNAL("toothSurface"))
    def resizeEvent(self,event):
        self.shapes()
    def shapes(self):
        self.toothRect=QtCore.QRectF(0,0,self.width(),self.height())
        irw=self.toothRect.width()*0.25                                                                  #inner rectangle width
        if self.isBacktooth:
            irh=self.toothRect.height()*0.25                                                             #backtooth inner rectangle height
        else:
            irh=self.toothRect.height()*0.40                                                             #fronttooth inner rectangle height
        self.innerRect=self.toothRect.adjusted(irw,irh,-irw,-irh)

        self.mesial=QtGui.QPolygon([0,0,
        self.innerRect.topLeft().x(),self.innerRect.topLeft().y(),
        self.innerRect.bottomLeft().x(),self.innerRect.bottomLeft().y(),
        self.toothRect.bottomLeft().x(),self.toothRect.bottomLeft().y()])

        self.occlusal=QtGui.QPolygon([self.innerRect.topLeft().x(),self.innerRect.topLeft().y(),
        self.innerRect.topRight().x(),self.innerRect.topRight().y(),
        self.innerRect.bottomRight().x(),self.innerRect.bottomRight().y(),
        self.innerRect.bottomLeft().x(),self.innerRect.bottomLeft().y()])

        self.distal=QtGui.QPolygon([self.innerRect.topRight().x(),self.innerRect.topRight().y(),
        self.toothRect.topRight().x(),self.toothRect.topRight().y(),
        self.toothRect.bottomRight().x(),self.toothRect.bottomRight().y(),
        self.innerRect.bottomRight().x(),self.innerRect.bottomRight().y()])

        self.buccal=QtGui.QPolygon([0,0,
        self.toothRect.topRight().x(),self.toothRect.topRight().y(),
        self.innerRect.topRight().x(),self.innerRect.topRight().y(),
        self.innerRect.topLeft().x(),self.innerRect.topLeft().y()])

        self.palatal=QtGui.QPolygon([self.toothRect.bottomLeft().x(),self.toothRect.bottomLeft().y(),
        self.innerRect.bottomLeft().x(),self.innerRect.bottomLeft().y(),
        self.innerRect.bottomRight().x(),self.innerRect.bottomRight().y(),
        self.toothRect.bottomRight().x(),self.toothRect.bottomRight().y()])

        self.mouseOverSurface=None #initiate a value

    def paintEvent(self,event=None):
        '''override the paint event so that we can draw our grid'''
        if self.isBacktooth:
            if self.isUpper:
                if self.isRight:
                    surfs="DBPMO"
                else:
                    surfs="MBPDO"
            else:
                if self.isRight:
                    surfs="DLBMO"
                else:
                    surfs="MLBDO"
        else:
            if self.isUpper:
                if self.isRight:
                    surfs="DBPMI"
                else:
                    surfs="MBPDI"
            else:
                if self.isRight:
                    surfs="DLBMI"
                else:
                    surfs="MLBDI"

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setPen(QtGui.QColor("gray"))
        painter.setBrush(colours.IVORY)
        painter.drawRect(self.toothRect)
        painter.drawRect(self.innerRect)
        painter.drawLine(self.toothRect.topLeft(),self.innerRect.topLeft())
        painter.drawLine(self.toothRect.topRight(),self.innerRect.topRight())
        painter.drawLine(self.toothRect.bottomLeft(),self.innerRect.bottomLeft())
        painter.drawLine(self.toothRect.bottomRight(),self.innerRect.bottomRight())
        option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
        rect=self.toothRect.adjusted(0,0,-self.innerRect.right(),0)
        painter.drawText(QtCore.QRectF(rect),surfs[0],option)
        rect=self.toothRect.adjusted(0,0,0,-self.innerRect.bottom())
        painter.drawText(QtCore.QRectF(rect),surfs[1],option)
        rect=self.toothRect.adjusted(0,self.innerRect.bottom(),0,0)
        painter.drawText(QtCore.QRectF(rect),surfs[2],option)
        rect=self.toothRect.adjusted(self.innerRect.right(),0,0,0)
        painter.drawText(QtCore.QRectF(rect),surfs[3],option)
        painter.drawText(QtCore.QRectF(self.innerRect),surfs[4],option)
        painter.setBrush(self.fillcolour)
        if "M" in self.filledSurfaces:
            if self.isRight:
                painter.drawPolygon(self.distal)
            else:
                painter.drawPolygon(self.mesial)
        if "O" in self.filledSurfaces or "I" in self.filledSurfaces:
            painter.drawPolygon(self.occlusal)
        if "D" in self.filledSurfaces:
            if not self.isRight:
                painter.drawPolygon(self.distal)
            else:
                painter.drawPolygon(self.mesial)
        if "B" in self.filledSurfaces:
            if self.isUpper:
                painter.drawPolygon(self.buccal)
            else:
                painter.drawPolygon(self.palatal)
        if "L" in self.filledSurfaces:
                painter.drawPolygon(self.buccal)
        if "P" in self.filledSurfaces:
                painter.drawPolygon(self.palatal)
        if self.mouseOverSurface!=None:
            painter.setBrush(colours.TRANSPARENT)
            painter.setPen(QtGui.QColor("red"))
            painter.drawPolygon(self.mouseOverSurface)

class chartLineEdit(QtGui.QLineEdit):
    '''override the keypress event for up and down arrow keys.
    '''
    def __init__(self, parent=None):
        super(chartLineEdit,self).__init__(parent)
    def keyPressEvent(self, event):
        '''overrudes QWidget's keypressEvent'''
        if event.key() == QtCore.Qt.Key_Up:
            self.emit(QtCore.SIGNAL("PySig"),("up"))
        elif event.key() == QtCore.Qt.Key_Return:
            self.emit(QtCore.SIGNAL("PySig"),("down"))
        elif event.key() == QtCore.Qt.Key_Down:
            self.emit(QtCore.SIGNAL("PySig"),("down"))
        else:
            QtGui.QLineEdit.keyPressEvent(self,event)

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = tpWidget(Form)
    ui.setExistingProps("MOD ")
    #Form.setEnabled(False)
    Form.show()
    sys.exit(app.exec_())

