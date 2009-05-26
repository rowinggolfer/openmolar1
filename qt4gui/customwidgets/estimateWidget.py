# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

from __future__ import division

import re
from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.customwidgets import Ui_estimateItemWidget,\
Ui_estHeaderWidget,Ui_estFooterWidget


class estItemWidget(Ui_estimateItemWidget.Ui_Form):
    def __init__(self,parent=None):
        self.parent=parent
        self.setupUi(self.parent)
        self.signals()
        self.validators
        
    def setItem(self,item):
        self.item=item
        self.code_label.setToolTip(str(item.type))
        
    def loadValues(self):
        if self.item.number!=None:
            self.setNumber(self.item.number)
        self.setFee(self.item.fee)
        self.setPtFee(self.item.ptfee)
        self.setDescription(self.item.description)
        self.setType(self.item.type)
        self.setCompleted(self.item.completed)
        self.setCset(self.item.csetype)
        
    def validators(self):
        self.fee_lineEdit.setValidator(QtGui.\
        QDoubleValidator(0.0, 3000.0, 2, self.fee_lineEdit) )
        self.ptFee_lineEdit.setValidator(QtGui.\
        QDoubleValidator(0.0, 3000.0, 2, self.ptFee_lineEdit) )

        #self.fee_lineEdit.setInputMask('000.00')
        #self.ptFee_lineEdit.setInputMask("000.00")

    def signals(self):
        QtCore.QObject.connect(self.delete_pushButton,
        QtCore.SIGNAL("clicked()"),self.deleteItem)

        QtCore.QObject.connect(self.completed_checkBox,
        QtCore.SIGNAL("stateChanged(int)"),self.completeItem)

        self.cset_lineEdit.connect(self.cset_lineEdit,QtCore.SIGNAL(
        "textEdited (const QString&)"),self.update_cset)

        self.number_lineEdit.connect(self.number_lineEdit,QtCore.SIGNAL(
        "textEdited (const QString&)"),self.update_number)

        self.description_lineEdit.connect(self.description_lineEdit,QtCore.SIGNAL(
        "textEdited (const QString&)"),self.update_descr)

        self.fee_lineEdit.connect(self.fee_lineEdit,QtCore.SIGNAL(
        "textEdited (const QString&)"),self.update_Fee)

        self.ptFee_lineEdit.connect(self.ptFee_lineEdit,QtCore.SIGNAL(
        "textEdited (const QString&)"),self.update_ptFee)

    def update_cset(self,arg):
        self.item.csetype=str(arg)
    def update_number(self,arg):
        try:
            newVal=int(arg)
        except ValueError:
            newVal=0
        self.item.number=newVal
    def update_descr(self,arg):
        self.item.description=str(arg).replace('"', '\"')
    def update_Fee(self,arg):
        try:
            newVal=int(float(arg)*100)
        except ValueError:
            newVal=0
        self.item.fee=newVal
        self.userInput()
    def update_ptFee(self,arg):
        try:
            newVal=int(float(arg)*100)
        except ValueError:
            newVal=0
        self.item.ptfee=newVal
        self.userInput()
    def setNumber(self,arg):
        self.number_lineEdit.setText(str(arg))

    def setDescription(self,arg):
        self.description_lineEdit.setText(arg)

    def setType(self,arg):
        if arg in (None,""):
            arg="-"
        self.code_label.setText(arg.split(" ")[0])
    def setCset(self,arg):
        if arg in (None,""):
            arg="-"        
        self.cset_lineEdit.setText(str(arg))
    def setFee(self,arg):
        self.fee_lineEdit.setText("%.02f"%(arg/100))
    def setPtFee(self,arg):
        self.ptFee_lineEdit.setText("%.02f"%(arg/100))
    def setCompleted(self,arg):
        self.completed_checkBox.setChecked(bool(arg))

    def deleteItem(self):
        '''
        a slot for the delete button press
        '''
        self.parent.emit(QtCore.SIGNAL("deleteMe"),(self))

    def completeItem(self,arg):
        '''
        a slot for the checkbox state change
        should only happen when this is altered by user (not prgramatically)
        '''
        result=(arg==2)
        self.delete_pushButton.setEnabled(not result)
        self.fee_lineEdit.setEnabled(not result)
        self.ptFee_lineEdit.setEnabled(not result)

        self.item.completed=result
        self.userInput()
        self.parent.emit(QtCore.SIGNAL("completedItem"), (self.item))

    def userInput(self):
        self.parent.emit(QtCore.SIGNAL("user_interaction"))



class estWidget(QtGui.QFrame):
    def __init__(self,parent=None):
        super(estWidget,self).__init__(parent)
        self.setSizePolicy(QtGui.QSizePolicy(
        QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding))

        self.estimate_layout=QtGui.QVBoxLayout(self)
        self.estimate_layout.setSpacing(0)

        header=QtGui.QWidget()
        estHeader=Ui_estHeaderWidget.Ui_Form()
        estHeader.setupUi(header)
        self.estimate_layout.addWidget(header)

        footer=QtGui.QWidget()
        self.estFooter=Ui_estFooterWidget.Ui_Form()
        self.estFooter.setupUi(footer)
        self.estimate_layout.addWidget(footer)

        self.estimate_layout.addStretch(-1)
        self.estItemWidgets=[]
        self.ests=()

        self.bareMinimumHeight=header.height()+footer.height()

        self.setMinimumSize(self.minimumSizeHint())

    def minimumSizeHint(self):
        height=self.bareMinimumHeight
        height+=len(self.estItemWidgets)*30
        return QtCore.QSize(600,height)

    def updateTotals(self):
        self.total=0
        self.ptTotal=0
        for item in self.ests:
            self.total+=item.fee
            self.ptTotal+=item.ptfee

        self.estFooter.fee_lineEdit.setText("%.02f"%(self.total/100))
        self.estFooter.ptfee_lineEdit.setText("%.02f"%(self.ptTotal/100))

    def setEstimate(self,ests):
        self.ests=ests
        self.clear()
        for item in self.ests:
            iw=QtGui.QWidget()
            i=estItemWidget(iw)
            i.setItem(item)
            i.loadValues()
            iw.connect(iw,QtCore.SIGNAL("user_interaction"),
            self.updateTotals)

            iw.connect(iw,QtCore.SIGNAL("deleteMe"),self.deleteItemWidget)

            iw.connect(iw,QtCore.SIGNAL("completedItem"),
            self.itemCompletionState)
            self.estItemWidgets.append(i)
            self.estimate_layout.insertWidget(1,iw)

        self.setMinimumSize(self.minimumSizeHint())
        self.updateTotals()

    def itemCompletionState(self, item):
        if item.completed:
            amountToRaise=item.ptfee
            self.emit(QtCore.SIGNAL("completedItem"),item.type)
        else:
            amountToRaise=item.ptfee*-1
            self.emit(QtCore.SIGNAL("unCompletedItem"),item.type)

        self.emit(QtCore.SIGNAL("applyFeeNow"), (amountToRaise))
        
    def clear(self):
        '''
        clears all est widget in anticipation of a new estimate
        '''
        while self.estItemWidgets!=[]:
            widg = self.estItemWidgets.pop()
            self.estimate_layout.removeWidget(widg.parent)
            widg.parent.setParent(None)

        self.updateTotals()

    def deleteItemWidget(self,arg):
        '''
        deletes a widget when delet button pressed.
        '''
        message="Delete %s %s from estimate?"%(
        arg.number_lineEdit.text(),arg.description_lineEdit.text())
        input=QtGui.QMessageBox.question(self,"confirm",
        message,QtGui.QMessageBox.No,QtGui.QMessageBox.Yes)

        if input==QtGui.QMessageBox.Yes:
            self.estimate_layout.removeWidget(arg.parent)
            arg.parent.setParent(None)
            for est in self.ests:
                if est.ix==arg.item.ix:
                    self.ests.remove(est)
                    self.emit(QtCore.SIGNAL("deleteItem"),est.type)


            self.updateTotals()


if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)

    from openmolar.dbtools import patient_class
    pt=patient_class.patient(11956)
    form=estWidget()
    form.setEstimate(pt.estimates)
    print "loaded once"
    form.setEstimate(pt.estimates)
    form.show()


    sys.exit(app.exec_())
