# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

from __future__ import division

from PyQt4 import QtGui, QtCore
import re

from openmolar.qt4gui.compiled_uis import Ui_addTreatment
from openmolar.qt4gui.compiled_uis import Ui_toothtreatmentItemWidget

from openmolar.settings import localsettings,fee_keys
from openmolar.ptModules import estimates

class itemWidget(Ui_toothtreatmentItemWidget.Ui_Form):
    '''
    a custom gui widget with a description and a double spin box
    '''
    def __init__(self,parent,widget):
        self.parent=parent
        self.setupUi(widget)
        #QtCore.QObject.connect(self.spinBox,QtCore.\
        #SIGNAL("valueChanged(int)"), self.feeCalc)
        self.itemcode=""
        self.itemfee=0
        self.tooth=""
        QtCore.QObject.connect(self.doubleSpinBox,
            QtCore.SIGNAL("valueChanged(double)"), self.parent.updateTotal)
        QtCore.QObject.connect(self.pt_doubleSpinBox,
            QtCore.SIGNAL("valueChanged(double)"), self.parent.updateTotal)


    def setItem(self,tooth, usercode):
        self.tooth=tooth
        self.usercode=usercode
        self.tooth_label.setText("%s %s"%(tooth.upper(), usercode))
        self.itemcode=fee_keys.getCode(tooth,usercode)
        self.description = localsettings.descriptions.get(self.itemcode)
        self.description_label.setText("%s\t(%s)"%(self.description,
                                                    self.itemcode))
        self.feeCalc()
        
    def feeCalc(self):
        '''
        puts the fee into widget's double spinbox
       '''
        #-- here is why we need to import the division from the future...
        #-- no rounding errors please!
        fee, ptfee = fee_keys.getFee(self.parent.pt, self.itemcode)
        self.doubleSpinBox.setValue(fee/100)
        self.pt_doubleSpinBox.setValue(ptfee/100)
        self.parent.updateTotal()

class treatment(Ui_addTreatment.Ui_Dialog,):
    '''
    A custom class with a scrollArea, a dentist comboBox,
    and a total double spin box
    '''
    def __init__(self, dialog, pt):
        self.setupUi(dialog)
        self.dialog=dialog
        self.items=[]
        self.pt = pt


    def itemsPerTooth(self, tooth, props):
        '''
        this is called when treatment is added to a single tooth
        usage itemsPerTooth("ul7","MOD,CO,PR ")
        returns (("ul7","MOD,CO"),("ul7","PR"))
        '''
        treats=[]
        items=props.strip("() ").split(" ")
        for item in items:
            #--look for pins and posts
            if re.match(".*,PR.*",item):
                #print "removing .pr"
                treats.append((tooth,",PR"),)
                item=item.replace(",PR","")
            if re.match("CR.*,C[1-4].*",item):
                posts=re.findall(",C[1-4]",item)
                #print "making Post a separate item"
                for post in posts:
                    treats.append((tooth,"CR%s"%post),)
                item=item.replace(post,"")

            treats.append((tooth, item), )
        
        self.setItems(treats)

    def setItems(self, items):
        '''
        useage setItems((("ul6", "MO"), ("ul6","RT")),)
        '''
        for item in items:
            tooth=item[0]
            fill=item[1]
            self.items.append((tooth, fill),)

    def showItems(self):
        self.itemWidgets=[]
        vlayout = QtGui.QVBoxLayout(self.frame)
        vlayout.setSpacing(2)
        for item in self.items:
            #-- item will be ("UL6","CO")
            #-- initiate a QWidget
            iw=QtGui.QWidget()
            #-- initiate an itemWidget with this class as parent,
            #-- and inheriting from iw
            i=itemWidget(self,iw)
            i.setItem(item[0], item[1])
            self.itemWidgets.append(i)
            vlayout.addWidget(iw)

    def updateTotal(self):
        total, pt_total = 0, 0
        for widg in self.itemWidgets:
            total+=widg.doubleSpinBox.value()
            pt_total += widg.pt_doubleSpinBox.value()
        self.fee_doubleSpinBox.setValue(total)
        self.pt_fee_doubleSpinBox.setValue(pt_total)


    def getInput(self):
        if self.dialog.exec_():
            retarg=()
            for i in self.itemWidgets:
                fee=int(i.doubleSpinBox.value()*100)
                ptfee=int(i.pt_doubleSpinBox.value()*100)
                retarg+=(
                ("%s %s"%(i.tooth,i.usercode) ,
                i.itemcode,i.description, fee, ptfee),
                )
            print "addTreat.getInput() returning", retarg
            return retarg

if __name__ == "__main__":
    import sys
    localsettings.initiate()
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()

    from openmolar.dbtools import patient_class
    pt=patient_class.patient(1)

    #print "PLAN for ", toothPlan[0],toothPlan[1]

    ui = treatment(Dialog,"P")
    treatmentDict=estimates.toothTreatDict(pt)
    ui.setItems(treatmentDict["pl"],)
    ui.setItems(treatmentDict["cmp"],)
    ui.showItems()

    chosen = ui.getInput()
    if chosen:
        print chosen
    else:
        print "rejected"
