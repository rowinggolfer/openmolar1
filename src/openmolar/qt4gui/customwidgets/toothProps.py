# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore
import re
from openmolar.settings import localsettings
from openmolar.settings import allowed
from openmolar.qt4gui.compiled_uis import Ui_toothProps
from openmolar.qt4gui import colours
from openmolar.qt4gui.compiled_uis import Ui_crownChoice

from openmolar.qt4gui.dialogs import toothprop_fulledit

FS_OPTIONS = {
"--"        : "--"+_("Fissure Sealants"),
"FS"        : _( u"Fissure Sealant"),
"FS,CO"     : _( u"Fissure Sealant/Composite")
}

BR_OPTIONS = {
"--"        : "--"+_("Bridge Elements"),
"BR/CR,V1"  : _( u"Bonded Retainer"),
"BR/P,V1"   : _( u"Bonded Pontic"),
"BR,AE"     : _( u"Adhesive Wing"),
"BR/CR,LAVA": _( u"Lava Retainer"),
"BR/P,LAVA" : _( u"Lava Pontic"),
"BR/CR,GO"  : _( u"Gold Retainer"),
"BR/P,GO"   : _( u"Gold Pontic"),
"BR/CR,OT"  : _( u"Other Retainer"),
"BR/P,OT"   : _( u"Other Pontic")
}

ENDO_OPTIONS = {
"--"        : "--"+_("Endodontics"),
"PX"        : _( u"Pulp Extirpation - 1 canal"),
"PX+"       : _( u"Pulp Extirpation - multiple canals"),
"RT"        : _( u"Root Canal")
}

SURGICAL_OPTIONS = {
"--"        : "--"+_("Surgical"),
"EX"        : _( u"Extraction"),
"EX/S1"     : _( u"Surgical Extraction"),
"AP"        : _( u"Apicectomy")
}

STATIC_OPTIONS = {
"--"        : "--"+_("Static Only"),
"TM"        : _( u"Tooth Missing"),
"AT"        : _( u"Denture Tooth"),
"RP"        : _( u"Root Present"),
"+P"        : _( u"Permanent Tooth Present")
}

COMBOBOXES = (FS_OPTIONS,BR_OPTIONS,ENDO_OPTIONS,SURGICAL_OPTIONS, 
STATIC_OPTIONS)


class chartLineEdit(QtGui.QLineEdit):
    ''' 
    A custom line edit that accepts only BLOCK LETTERS
    and is self aware when verification is needed
    override the keypress event for up and down arrow keys.
    '''
    def __init__(self, parent=None):
        super(chartLineEdit,self).__init__(parent)
        self.parent = parent
        self.originalPropList = []
    
    def unsavedChanges(self):
        '''
        checks for unsaved changes
        '''
        result = not (self.originalPropList == self.propListFromText())
        return result

    def finishedEdit(self):
        '''
        we have finished editing the text.. let the main gui know by 
        means of a signal
        '''        
        props = str(self.text().toAscii())
        if props != "" or (props == "" and self.originalPropList != []):
            if not re.match ("..* $", props):
                if props != "":
                    props = props + " "
            self.emit(QtCore.SIGNAL("Changed_Properties"), props)

    def additional(self, checkedAlready = False):
        '''
        we have finished editing, and moving on
        '''
        if checkedAlready or self.verifyProps():
            self.updateFromPropList(self.propListFromText())
            self.parent.tooth.clear()
            self.parent.tooth.update()
            self.finishedEdit()
        
    def propListFromText(self):
        '''
        returns the current property list
        '''
        text = str(self.text().toAscii())
        propList = text.strip(" ").split(" ")
        return propList

    def updateFromPropList(self, propList):
        text = ""
        for prop in propList:
            if not prop in (""," "):
                text += "%s "% prop
        self.setKnownProps(text)
        ##not sure these are needed??
        self.parent.tooth.clear()
        self.parent.tooth.update()
        self.finishedEdit()

    def setKnownProps(self, arg):
        '''
        put a string of props into the text, and set the known list of
        properties
        '''
        self.setText(arg)
        self.originalPropList = self.propListFromText()

    def verifyProps(self):
        '''
        verify that the current text is valid
        '''
        snapshotPropList = self.propListFromText()
        if snapshotPropList == self.originalPropList:
            return True
        for prop in self.originalPropList:
            if not prop in snapshotPropList:
                self.originalPropList.remove(prop)
        verified = True
        for prop in snapshotPropList:
            if not self.propAllowed(prop):
                verified = False
            else:
                self.originalPropList.append(prop)
        return verified

    def deleteComments(self):
        snapshotPropList = self.propListFromText()
        deleted = False
        for prop in snapshotPropList:
            if prop[:1] == "!":
                snapshotPropList.remove(prop)
                deleted = True
        if deleted:
            self.updateFromPropList(snapshotPropList)
            self.emit(QtCore.SIGNAL("DeletedComments"))

    def addItem(self, item):
        if not item in ("", " "):
            snapshotPropList = self.propListFromText()
            snapshotPropList.append(item)
            self.updateFromPropList(snapshotPropList)

    def removeItem(self, item):
        if item == "":
            return
        snapshotPropList = self.propListFromText()
        snapshotPropList.remove(item)
        self.updateFromPropList(snapshotPropList)

    def removeEndItem(self):
        '''
        user has pressed the delete button
        remove the last item
        '''
        snapshotPropList = self.propListFromText()
        self.updateFromPropList(snapshotPropList[:-1])

    def propAllowed(self, prop):
        '''
        check to see if the user has entered garbage
        '''
        #print "checking Prop '%s' origs ='%s'"% (prop, self.originalPropList),
        if prop[:1] == "!": #comment
            return True
        if prop in self.originalPropList:
        #    print "already present, ignoring"
            return True

        allowedCode = True
        if prop!= "":
            if self.parent.tooth.isBacktooth and not (prop in allowed.backToothCodes):
                allowedCode = False
            if not self.parent.tooth.isBacktooth and \
            not (prop in allowed.frontToothCodes):
                allowedCode = False
            if (not self.parent.is_Static) and (prop in allowed.treatment_only):
                allowedCode = True
        if not allowedCode:
            message = '''"%s" is not recognised <br />
            do you want to accept anyway?'''% prop
            input = QtGui.QMessageBox.question(self, "Confirm", message,
            QtGui.QMessageBox.No,QtGui.QMessageBox.Yes)

            if input == QtGui.QMessageBox.Yes:
                allowedCode = True
            else:
                allowedCode = False
        if allowedCode:
            print "accepting new entry", prop
        return allowedCode
    
    def specialKeyPressed(self, arg):
        '''
        handles the events when a user hits space, up, down or return
        '''
        if arg in ("up", "down"):
            self.emit(QtCore.SIGNAL("ArrowKeyPressed"),(arg))
        else:
            self.additional()
            
    def keyPressEvent(self, event):
        '''overrudes QWidget's keypressEvent'''
        if event.key() == QtCore.Qt.Key_Up:
            self.specialKeyPressed("up")
        elif event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Down):
            self.specialKeyPressed("down")
        elif event.key() == QtCore.Qt.Key_Space:
            QtGui.QLineEdit.keyPressEvent(self,event)            
            self.specialKeyPressed("space")            
        else:
            inputT = event.text().toAscii()
            if re.match("[a-z]", inputT):
                #-- catch and overwrite any lower case
                event = QtGui.QKeyEvent(event.type(), event.key(),
                event.modifiers(), event.text().toUpper())
            if not (inputT == "!" and not self.parent.is_Static):
                #don't allow comments if not in static
                QtGui.QLineEdit.keyPressEvent(self,event)

class tpWidget(Ui_toothProps.Ui_Form, QtGui.QWidget):
    def __init__(self, parent=None):
        super(tpWidget, self).__init__(parent)
        self.parent = parent
        self.setupUi(self)
        hlayout=QtGui.QHBoxLayout(self.editframe)
        hlayout.setContentsMargins(0,0,0,0)
        self.lineEdit=chartLineEdit(self)
        self.lineEdit.setMaxLength(34) #as defined in the sql tables for a static entry - may exceed the plan stuff.... but I will validate that anyway.
        hlayout.addWidget(self.lineEdit)
        self.tooth=tooth()  #self.frame)
        self.toothlayout=QtGui.QHBoxLayout(self.frame)
        self.toothlayout.setContentsMargins(0,0,0,0)
        self.toothlayout.addWidget(self.tooth)
        self.am_pushButton.setStyleSheet(
        "background-color: %s"% colours.AMALGAM_ )

        self.co_pushButton.setStyleSheet(
        "background-color: %s"% colours.COMP_ )
        
        self.gl_pushButton.setStyleSheet(
        "background-color: %s"% colours.GI_ )
        
        self.gold_pushButton.setStyleSheet(
        "background-color: %s"% colours.GOLD_ )

        self.porc_pushButton.setStyleSheet(
        "background-color: %s"% colours.PORC_ )
        
        self.is_Static = False
        self.selectedChart = ""
        self.selectedTooth = ""
        self.comboboxes = []
        self.populateComboBoxes()
        self.signals()
        
    def populateComboBoxes(self):
        vlayout = QtGui.QVBoxLayout(self.cb_scrollArea)
        vlayout.setMargin(0)
        for combobox_dict in COMBOBOXES:
            cb = QtGui.QComboBox(self)
            vals = combobox_dict.values()
            vals.sort()
            for val in vals:
                cb.addItem(val)
            vlayout.addWidget(cb)
            self.comboboxes.append(cb)

    def setTooth(self, selectedTooth, selectedChart):
        '''
        make the widget aware of exactly what it is editing
        selectedTooth will be 'ur8' etc..
        selectedChart will be 'st' or 'pl' or 'cmp'
        '''
        self.selectedChart = selectedChart
        self.selectedTooth = selectedTooth

        self.tooth.setBacktooth(int(selectedTooth[2])>3)
        self.tooth.setRightSide(selectedTooth[1] == "r")
        self.tooth.setUpper(selectedTooth[0] == "u")

        self.tooth.clear()
        self.tooth.update()

        self.tooth_label.setText(self.parent.pt.chartgrid[selectedTooth].upper())
        #--ALLOWS for deciduos teeth

        self.isStatic(selectedChart == "st")
        self.setExistingProps(self.parent.pt.__dict__[selectedTooth+selectedChart])


    def isStatic(self,arg):
        '''
        if the editing is of the static chart, then different buttons are enabled
        '''
        self.is_Static = arg
        self.comments_comboBox.setEnabled(arg)

    def comments(self,arg):
        '''
        comments combobox has been nav'd
        '''
        if arg ==_("ADD COMMENTS"):
            return
        elif arg ==_("DELETE COMMENTS"):
            self.lineEdit.deleteComments()
        else:
            #result=QtGui.QMessageBox.question(self, "Confirm",
            #'Add comment "%s"'% arg,
            #QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

            #if result == QtGui.QMessageBox.Yes:
            newComment = "%s"% arg.replace(" ","_")
            self.lineEdit.addItem(newComment)

        self.comments_comboBox.setCurrentIndex(0)

    def fulledit(self):
        '''
        user has clicked the edit button
        allow the user to edit the full contents of a tootget\ h
        '''
        Dialog = QtGui.QDialog()
        lineEdit = chartLineEdit()
        if self.isStatic:
            lineEdit.setMaxLength(34)
        lineEdit.setText(self.lineEdit.text())

        dl = toothprop_fulledit.editor(self.selectedTooth, self.selectedChart,
        lineEdit, Dialog)

        if dl.exec_():
            self.lineEdit.setText(dl.result)
            self.lineEdit.additional()
        else:
            self.lineEdit.updateFromPropList(self.lineEdit.originalPropList)
        #self.emit(QtCore.SIGNAL("full_edit"))

    def setExistingProps(self, arg):
        self.lineEdit.setKnownProps(arg)

    def updateSurfaces(self):
        existing = str(self.lineEdit.text().toAscii())
        if " " in existing: #we have an existing filling/property in the tooth
            colonPos = existing.rindex(" ")
            keep = existing[:colonPos+1]
            currentFill = existing[colonPos:]
        else:                                           #we don't
            keep = ""
            currentFill = existing
        if "," in currentFill:                          #we have a material
            split = currentFill.split(",")
            mat = "," + split[1]
            currentFill = self.tooth.filledSurfaces+mat
        elif "/" in currentFill:                        #we have a lab item
            split = currentFill.split("/")
            mat = split[0]+"/"
            currentFill = mat+self.tooth.filledSurfaces
        else:                                           #virgin tooth
            currentFill = self.tooth.filledSurfaces
        self.lineEdit.setText(keep+currentFill)

    def changeFillColour(self,arg):
        self.tooth.fillcolour=arg
        self.tooth.update()

    def plasticMaterial(self,arg):
        existing=str(self.lineEdit.text().toAscii())
        if " " in existing:
            colonPos=existing.rindex(" ")
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
        if " " in existing:
            colonPos=existing.rindex(" ")
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

    def keyNav(self, arg):
        if arg == "up":
            self.prevTooth()
        elif arg == "down":
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
        print "prevTooth"
        if self.lineEdit.verifyProps():
            self.lineEdit.finishedEdit()
            self.emit(QtCore.SIGNAL("NextTooth"),("up"))

    def nextTooth(self):
        print "nextTooth"
        if self.lineEdit.verifyProps():
            self.lineEdit.finishedEdit()
            self.emit(QtCore.SIGNAL("NextTooth"),("down"))

    def dec_perm(self):
        self.emit(QtCore.SIGNAL("FlipDeciduousState"))
        #self.nextTooth()

    def at(self):
        self.lineEdit.addItem("AT")
        self.nextTooth()

    def tm(self):
        self.lineEdit.addItem("TM")
        self.nextTooth()

    def ex(self):
        self.lineEdit.addItem("EX")
        self.nextTooth()

    def rt(self):
        self.lineEdit.addItem("RT")
        self.lineEdit.additional()
        
    def crown(self):
        def gold():
            self.lineEdit.addItem("CR,GO")
            Dialog.accept()
        def pjc():
            self.lineEdit.addItem("CR,PJ")
            Dialog.accept()
        def resin():
            self.lineEdit.addItem("CR,OT")
            Dialog.accept()
        def lava():
            self.lineEdit.addItem("CR,PJ")
            Dialog.accept()
        def fortress():
            self.lineEdit.addItem("CR,PJ")
            Dialog.accept()
        def temp():
            self.lineEdit.addItem("CR,T1")
            Dialog.accept()
        def other():
            self.lineEdit.addItem("CR,OT")
            Dialog.accept()
        def bonded():
            self.lineEdit.addItem("CR,V1")
            Dialog.accept()
        def recem():
            self.lineEdit.addItem("CR,RC")
            Dialog.accept()

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
        ccwidg.gold.connect(ccwidg.recement,QtCore.SIGNAL("clicked()"), recem)

        if Dialog.exec_():
            self.nextTooth()

    def cb_treat(self, arg):
        if not re.match("--.*", arg.toAscii()):
            print arg
            for cb in self.comboboxes:
                cb.setCurrentIndex(0)
            for combobox_dict in COMBOBOXES:
                for key in combobox_dict.keys():
                    if combobox_dict[key] == arg:
                        self.lineEdit.addItem(key)
                
    def staticButPressed(self):
        self.emit(QtCore.SIGNAL("static"))
    def planButPressed(self):
        self.emit(QtCore.SIGNAL("plan"))
    def compButPressed(self):
        self.emit(QtCore.SIGNAL("completed"))

    def signals(self):
        QtCore.QObject.connect(self.am_pushButton,
        QtCore.SIGNAL("clicked()"), self.am)

        QtCore.QObject.connect(self.co_pushButton,
        QtCore.SIGNAL("clicked()"), self.co)

        QtCore.QObject.connect(self.gl_pushButton,
        QtCore.SIGNAL("clicked()"), self.gl)

        QtCore.QObject.connect(self.gold_pushButton,
        QtCore.SIGNAL("clicked()"), self.go)

        QtCore.QObject.connect(self.porc_pushButton,
        QtCore.SIGNAL("clicked()"), self.pi)

        #user has clicked a surface
        QtCore.QObject.connect(self.tooth,QtCore.
        SIGNAL("toothSurface"), self.updateSurfaces)

        QtCore.QObject.connect(self.clear_pushButton,
        QtCore.SIGNAL("clicked()"), self.lineEdit.removeEndItem)

        QtCore.QObject.connect(self.edit_pushButton,
        QtCore.SIGNAL("clicked()"), self.fulledit)

        QtCore.QObject.connect(self.pushButton,
        QtCore.SIGNAL("clicked()"), self.lineEdit.additional)

        QtCore.QObject.connect(self.lineEdit,
        QtCore.SIGNAL("ArrowKeyPressed"),self.keyNav)

        QtCore.QObject.connect(self.rightTooth_pushButton,
        QtCore.SIGNAL("clicked()"), self.rightTooth)

        QtCore.QObject.connect(self.leftTooth_pushButton,
        QtCore.SIGNAL("clicked()"), self.leftTooth)

        QtCore.QObject.connect(self.dec_pushButton,
        QtCore.SIGNAL("clicked()"), self.dec_perm)

        QtCore.QObject.connect(self.at_pushButton,
        QtCore.SIGNAL("clicked()"), self.at)

        QtCore.QObject.connect(self.tm_pushButton,
        QtCore.SIGNAL("clicked()"), self.tm)

        QtCore.QObject.connect(self.ex_pushButton,
        QtCore.SIGNAL("clicked()"), self.ex)

        QtCore.QObject.connect(self.rt_pushButton,
        QtCore.SIGNAL("clicked()"), self.rt)

        QtCore.QObject.connect(self.defaultCrown_pushButton,
        QtCore.SIGNAL("clicked()"), self.crown)

        QtCore.QObject.connect(self.static_pushButton,
        QtCore.SIGNAL("clicked()"), self.staticButPressed)

        QtCore.QObject.connect(self.plan_pushButton,
        QtCore.SIGNAL("clicked()"), self.planButPressed)

        QtCore.QObject.connect(self.comp_pushButton,
        QtCore.SIGNAL("clicked()"), self.compButPressed)

        QtCore.QObject.connect(self.comments_comboBox,
        QtCore.SIGNAL("currentIndexChanged (const QString&)"), self.comments)

        for cb in self.comboboxes:
            QtCore.QObject.connect(cb,
            QtCore.SIGNAL("currentIndexChanged (const QString&)"), 
            self.cb_treat)

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


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = tpWidget(Form)
    ui.setExistingProps("MOD B,GL !COMMENT_TWO")
    #Form.setEnabled(False)
    #Form = chartLineEdit()
    Form.show()
    sys.exit(app.exec_())

