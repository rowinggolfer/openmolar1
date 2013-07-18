# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

'''
this module provides two classes.
a parent "estimate widget", and a custom item widget for displaying
and editing treatment costs
'''

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.customwidgets.chainLabel import ChainLabel

def decimalise(pence):
    return "%d.%02d"% (pence // 100, pence % 100)

class EstimateItemWidget(QtGui.QWidget):
    '''
    a class to show one specific item of treatment
    '''
    MONEY_WIDTH = 80
    
    separate_signal = QtCore.pyqtSignal(object)
    completed_signal =  QtCore.pyqtSignal(object)
    delete_signal =  QtCore.pyqtSignal(object)
    edited_signal = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.number_label = QtGui.QLabel()
        self.number_label.setFixedWidth(40)
        self.itemCode_label = QtGui.QLabel()
        self.description_lineEdit = QtGui.QLineEdit()
        self.cset_lineEdit = QtGui.QLineEdit()
        self.cset_lineEdit.setFixedWidth(40)
        self.fee_lineEdit = QtGui.QLineEdit()
        self.fee_lineEdit.setFixedWidth(self.MONEY_WIDTH)
        self.chain = ChainLabel()
        self.ptFee_lineEdit = QtGui.QLineEdit()
        self.ptFee_lineEdit.setFixedWidth(self.MONEY_WIDTH)
        self.completed_checkBox = QtGui.QCheckBox()
        self.delete_pushButton = QtGui.QPushButton()
        
        self.validators()
        self.feesLinked = True
        self.items = []
        self.itemCode = ""
        self.signals()

    def components(self):
        '''
        returns all the sub widgets.
        '''
        return (
        self.number_label,
        self.itemCode_label,
        self.description_lineEdit, 
        self.cset_lineEdit,
        self.fee_lineEdit,
        self.chain,
        self.ptFee_lineEdit,
        self.completed_checkBox,
        self.delete_pushButton)

    def linkfees(self, arg):
        '''
        toggles a boolean which determines if the pt fee and fee are the same
        '''
        self.feesLinked = arg

    def setChain(self, cset):
        '''
        break the chain if the course type is not P
        '''
        if cset != "P":
            self.chain.mousePressEvent(None)
    
    def separateIcon(self, separate=True):
        '''
        this is our little chain icon
        '''
        icon = QtGui.QIcon()
        if separate:
            icon.addPixmap(QtGui.QPixmap(":icons/expand.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        else:
            icon.addPixmap(QtGui.QPixmap(":/eraser.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.delete_pushButton.setIcon(icon)

    def addItem(self, item):
        self.items.append(item)
        self.itemCode_label.setToolTip(self.toolTip())
        self.loadValues()

    def toolTip(self):
        '''
        calculates a string to be added as a tool tip for the widget
        '''
        retarg = '<center>'
        for item in self.items:
            retarg += '''Category - '%s'<br /> Type - '%s'<br />
            ItemCode - '%s'<br />Feescale - %s
            <br />CSEtype - %s<br />Dent - %s<br />
            DBindex - %s<hr />'''% (
            item.category,
            item.type,
            item.itemcode,
            item.feescale,
            item.csetype,
            item.dent,
            item.ix)
        return retarg + "</center>"

    def loadValues(self):
        '''
        loads the values stored in self.items into the graphical widgets
        '''
        fee, ptfee, number = 0, 0, 0
        treatmentPlanned = True
        treatmentCompleted = True
        for item in self.items:
            if item.number:
                number += item.number
            fee += item.fee
            ptfee += item.ptfee
            self.setDescription(item.description)
            self.setItemCode(item.itemcode)
            self.setCompleted(item.completed)
            self.setCset(item.csetype)
            self.setChain(item.csetype)
            if item.completed:
                treatmentPlanned=False
            else:
                treatmentCompleted=False

        #-- set partially checked if any doubt
        if treatmentPlanned:
            self.completed_checkBox.setChecked(False)
        elif treatmentCompleted:
            self.completed_checkBox.setCheckState(
            QtCore.Qt.CheckState(QtCore.Qt.Checked))
        else:
            self.completed_checkBox.setCheckState(
            QtCore.Qt.CheckState(QtCore.Qt.PartiallyChecked))

        self.setNumber(number)
        self.setFee(fee)
        self.setPtFee(ptfee)

        self.separateIcon(len(self.items)>1)
            
    def validators(self):
        '''
        set validators to prevent junk data being entered by user
        '''
        self.fee_lineEdit.setValidator(QtGui.QDoubleValidator(
        0.0, 3000.0, 2, self.fee_lineEdit) )

        self.ptFee_lineEdit.setValidator(QtGui.QDoubleValidator(
        0.0, 3000.0, 2, self.ptFee_lineEdit) )

        #self.fee_lineEdit.setInputMask('000.00')
        #self.ptFee_lineEdit.setInputMask("000.00")

    def signals(self):
        '''
        connects signals
        '''
        QtCore.QObject.connect(self.chain,
        QtCore.SIGNAL("chained"), self.linkfees)

        QtCore.QObject.connect(self.delete_pushButton,
        QtCore.SIGNAL("clicked()"), self.deleteItem)

        QtCore.QObject.connect(self.completed_checkBox,
        QtCore.SIGNAL("clicked()"), self.completeItem)

        self.cset_lineEdit.connect(self.cset_lineEdit, QtCore.SIGNAL(
        "textEdited (const QString&)"), self.update_cset)

        self.description_lineEdit.connect(self.description_lineEdit,
        QtCore.SIGNAL("textEdited (const QString&)"), self.update_descr)

        self.fee_lineEdit.connect(self.fee_lineEdit, QtCore.SIGNAL(
        "textEdited (const QString&)"), self.update_Fee)

        self.ptFee_lineEdit.connect(self.ptFee_lineEdit, QtCore.SIGNAL(
        "textEdited (const QString&)"), self.update_ptFee)

    def update_cset(self, arg):
        '''
        csetype has been altered, alter ALL underying data
        (for multiple items)
        '''
        for item in self.items:
            item.csetype = str(arg)

    def update_descr(self, arg):
        '''
        description has been altered, alter ALL underying data
        (for multiple items)
        '''
        for item in self.items:
            item.description = str(arg.toAscii()).replace('"', '\"')

    def update_Fee(self, arg, userPerforming=True):
        '''
        fee has been altered, alter ALL underying data
        for multiple items - the new fee is what has been inputted / number
        of items.
        '''
        try:
            newVal = int(float(arg)*100)
            if self.feesLinked and userPerforming:
                self.ptFee_lineEdit.setText(arg)
                self.update_ptFee(arg, False)
        except ValueError:
            newVal = 0
        for item in self.items:
            item.fee = newVal / len(self.items)
        if userPerforming:
            self.edited_signal.emit()

    def update_ptFee(self, arg, userPerforming=True):
        '''
        ptfee has been altered, alter ALL underying data
        for multiple items - the new fee is what has been inputted / number
        of items.
        '''
        try:
            newVal = int(float(arg)*100)
            if self.feesLinked and userPerforming:
                self.fee_lineEdit.setText(arg)
                self.update_Fee(arg, False)
        except ValueError:
            newVal = 0
        for item in self.items:
            item.ptfee = newVal / len(self.items)
        if userPerforming:
            self.edited_signal.emit()
        print self.items

    def setNumber(self, arg):
        '''
        update number label
        '''
        self.number_label.setText(str(arg))

    def setDescription(self, arg):
        '''
        update description label
        '''
        if len(self.items) > 1:
            arg += " etc"
        
        self.description_lineEdit.setText(arg)

    def setItemCode(self, arg):
        '''
        update the item code
        '''
        self.itemCode = arg
        if arg in (None, ""):
            arg = "-"
        self.itemCode_label.setText(arg)

    def setCset(self, arg):
        '''
        update the course type
        '''
        if arg in (None, ""):
            arg = "-"
        self.cset_lineEdit.setText(str(arg))

    def setFee(self, fee):
        '''
        update the fee lineedit
        '''
        self.fee_lineEdit.setText(decimalise(fee))

    def setPtFee(self, fee):
        '''
        update the fee lineedit
        '''
        self.ptFee_lineEdit.setText(decimalise(fee))

    def setCompleted(self, arg):
        '''
        function so that external calls can alter this widget
        '''
        self.completed_checkBox.setChecked(bool(arg))
        self.checked()

    def deleteItem(self):
        '''
        a slot for the delete button press
        '''
        if len(self.items)>1:
            #self.splitMultiItemDialog()
            self.separate_signal.emit(self)
        else:
            self.delete_signal.emit(self)

    def checked(self):
        '''
        this is a slot called when the completed checkbox changes
        '''
        state = not self.completed_checkBox.checkState()
        self.fee_lineEdit.setEnabled(state)
        self.ptFee_lineEdit.setEnabled(state)
        self.chain.setEnabled(state)
        #allow_delete = (len(self.items) == 1 and not
        #    self.completed_checkBox.isChecked())
        self.delete_pushButton.setEnabled(state or len(self.items)>1)

    def completeItem(self):
        '''
        a slot for the checkbox state change
        should only happen when this is altered by user (not programatically)
        '''
        
        if self.completed_checkBox.checkState() == 0:
            action = "reverse"
            complete = False
        else:
            #-- the user is "completing"
            action = "complete"
            complete = True
        
        number = len(self.items)            
        if number > 1:
            number_of_relevant_items = 0
            for item in self.items:
                if item.completed != complete:
                    number_of_relevant_items += 1
            if number_of_relevant_items == 1:
                mystr = "this treatment"
            else:
                mystr = "these treatments"
            result = QtGui.QMessageBox.question(self,
            "Multiple items",
            '''There are %d items associated with this Widget.<br />
            of these, %d would be affected<br />
            %s %s?'''% (number, number_of_relevant_items, action, mystr),
            QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
            QtGui.QMessageBox.Yes )
            if result == QtGui.QMessageBox.Yes:
                self.completed_checkBox.setChecked(complete)
                self.checked()
                for item in self.items:
                    if item.completed  !=  complete:
                        item.completed = complete
                        self.completed_signal.emit(item)
            self.completed_checkBox.setCheckState(
                QtCore.Qt.CheckState(QtCore.Qt.Checked))
        
        else:
            self.checked()
            self.items[0].completed = complete
            self.completed_signal.emit(self.items[0])
            self.completed_checkBox.setChecked(complete)
            
        self.checked() #changes the enabled state of buttons etc...
        self.edited_signal.emit()

class _TestParent(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        layout = QtGui.QHBoxLayout(self) 
        layout.setMargin(0)
        
        widg = EstimateItemWidget(self)
        layout.addWidget(widg.number_label)
        layout.addWidget(widg.itemCode_label)
        layout.addWidget(widg.description_lineEdit)
        layout.addWidget(widg.cset_lineEdit)
        layout.addWidget(widg.fee_lineEdit)
        layout.addWidget(widg.chain)
        layout.addWidget(widg.ptFee_lineEdit)
        layout.addWidget(widg.completed_checkBox)
        layout.addWidget(widg.delete_pushButton)
        
        self.edited_signal = widg.edited_signal
        
if __name__ == "__main__":
    def sig_catcher(*args):
        '''test procedure'''
        print "signal caught argument=", args
        
    import sys

    app = QtGui.QApplication(sys.argv)

    form = QtGui.QMainWindow()
    
    widg = _TestParent()
    widg.edited_signal.connect(sig_catcher)
    
    form.setCentralWidget(widg)
    form.show()
    
    sys.exit(app.exec_())
