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

from __future__ import division

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.customwidgets import Ui_estimateItemWidget, \
Ui_estHeaderWidget, Ui_estFooterWidget, chainLabel

from openmolar.qt4gui.dialogs import Ui_estSplitItemsDialog

class estItemWidget(Ui_estimateItemWidget.Ui_Form):
    '''
    a class to show one specific item of treatment
    '''
    def __init__(self, parent=None):
        #super(estItemWidget, self).__init__(parent)
        self.parent = parent
        self.setupUi(self.parent)
        self.addchain()
        self.validators()
        self.feesLinked = True
        self.items = []
        self.itemCode = ""
        self.allCompleted = True
        self.allPlanned = True
        self.signals()

    def addchain(self):
        '''
        called at init - adds a chain icon showing if the fee/pt fee
        are identical
        '''
        self.chain = chainLabel.chainLabel(self.chain_frame)
        QtCore.QObject.connect(self.chain,
        QtCore.SIGNAL("chained"), self.linkfees)

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

    def setItem(self, item):
        '''
        sets the item being displayed
        '''
        self.items.append(item)
        self.code_label.setToolTip(self.toolTip())
        self.loadValues()

    def separateIcon(self, separate=True):
        '''
        this is our little chain icon
        '''
        icon = QtGui.QIcon()
        if separate:
            icon.addPixmap(QtGui.QPixmap(":icons/separate.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        else:
            icon.addPixmap(QtGui.QPixmap(":/eraser.png"),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)

        self.delete_pushButton.setIcon(icon)

    def addItem(self, item):
        '''
        when we have 2 of the same item...
        we add it using this procedure, rather than creating a new widget
        '''
        self.items.append(item)
        self.code_label.setToolTip(self.toolTip())
        self.loadValues()

    def toolTip(self):
        '''
        calculates a string to be added as a tool tip for the widget
        '''
        retarg = '<center>'
        for item in self.items:
            retarg += '''Type - '%s'<br />ItemCode - '%s'<br />Feescale - %s
            <br />CSEtype - %s<br />Dent - %s<br />DBindex - %s<hr />'''% (
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
            self.setType(item.type)
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

        if len(self.items)>1:
            self.separateIcon()
            self.code_label.setText("multi")
        else:
            self.separateIcon(False)
            self.setType(self.items[0].type)

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
            item.description = str(arg).replace('"', '\"')

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
            self.userInput()

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
            self.userInput()

    def setNumber(self, arg):
        '''
        update number label
        '''
        self.number_label.setText(str(arg))

    def setDescription(self, arg):
        '''
        update description label
        '''
        self.description_lineEdit.setText(arg)

    def setType(self, arg):
        '''
        update the important type label
        '''
        if arg in (None, ""):
            self.code_label.setText("?")
        elif arg[:2] in ("ur", "ul", "ll", "lr"):
            arg = "(%s)"%arg.split(" ")[0].upper()
            self.code_label.setText(arg)
        else:
            self.code_label.setText(arg.split(" ")[0])

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

    def setFee(self, arg):
        '''
        update the fee lineedit
        '''
        self.fee_lineEdit.setText("%.02f"%(arg/100))

    def setPtFee(self, arg):
        '''
        update the fee lineedit
        '''
        self.ptFee_lineEdit.setText("%.02f"%(arg/100))

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
            self.splitMultiItemDialog()
        else:
            self.parent.emit(QtCore.SIGNAL("deleteMe"), (self))

    def checked(self):
        '''
        this is a slot called when the completed checkbox changes
        '''
        state = not self.completed_checkBox.checkState()
        self.fee_lineEdit.setEnabled(state)
        self.ptFee_lineEdit.setEnabled(state)
        self.chain.setEnabled(state)

    def completeItem(self):
        '''
        a slot for the checkbox state change
        should only happen when this is altered by user (not programatically)
        '''
        number = len(self.items)
        arg = self.completed_checkBox.checkState()
        print arg
        if arg == 0:
            action = "reverse"
            complete = False
        elif arg == 1:
            #-- it is _partially_ checked... so perform logic.
            #-- the user is "completing"
            action = "complete"
            complete = True
        else:
            self.splitMultiItemDialog()
            return

        if number > 1:
            number_of_relevant_items = 0
            for item in self.items:
                if item.completed != complete:
                    number_of_relevant_items += 1
            if number_of_relevant_items == 1:
                mystr = "this treatment"
            else:
                mystr = "these treatments"
            result = QtGui.QMessageBox.question(self.parent,
            "Multiple items",
            '''There are %d items associated with this Widget.<br />
            of these, %d would be affected<br />
            %s %s?'''% (number, number_of_relevant_items, action, mystr),
            QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if result == QtGui.QMessageBox.Yes:
                self.completed_checkBox.setChecked(complete)
                self.checked()
                for item in self.items:
                    if item.completed  !=  complete:
                        item.completed = complete
                        self.parent.emit(QtCore.SIGNAL("completedItem"), (item))
                return
            else:
                finalState = (not complete)
        else:
            self.checked()
            self.items[0].completed = complete
            finalState = complete
            self.parent.emit(QtCore.SIGNAL("completedItem"), (self.items[0]))

        if finalState:
            self.completed_checkBox.setCheckState(
            QtCore.Qt.CheckState(QtCore.Qt.Checked))
        else:
            self.completed_checkBox.setChecked(finalState)
        self.checked() #changes the enabled state of buttons etc...
        self.userInput()

    def userInput(self):
        '''
        call this when the parent needs to be informed that the widget
        has been edited
        '''
        self.parent.emit(QtCore.SIGNAL("user_interaction"))

    def splitMultiItemDialog(self):
        '''
        a scissors button has been clicked
        call up a dialog to split the items
        '''
        Dialog = QtGui.QDialog(self.parent)
        dl = Ui_estSplitItemsDialog.Ui_Dialog()
        dl.setupUi(Dialog)
        ew = estWidget()
        ew.setEstimate(self.items, True)
        dl.scrollArea.setWidget(ew)

        #-- this miniDialog emits signals that go uncaught
        ew.connect(ew, QtCore.SIGNAL("applyFeeNow"),
        self.passOnApplyFeeNowSignal)

        ew.connect(ew, QtCore.SIGNAL("completedItem"),
        self.passOnCompletedSignal)

        ew.connect(ew, QtCore.SIGNAL("unCompletedItem"),
        self.passOnUncompletedSignal)

        ew.connect(ew, QtCore.SIGNAL("deleteItem"),
        self.passOnDeleteItemSignal)

        Dialog.exec_()
        if ew.allPlanned:
            self.completed_checkBox.setChecked(False)
        elif ew.allCompleted:
            self.completed_checkBox.setCheckState(
            QtCore.Qt.CheckState(QtCore.Qt.Checked))
        else:
            self.completed_checkBox.setCheckState(
            QtCore.Qt.CheckState(QtCore.Qt.PartiallyChecked))

        self.loadValues()
        self.userInput()

    def passOnCompletedSignal(self, arg):
        '''
        the child dialog has emitted a signal... pass it on
        '''
        self.parent.parent().emit(QtCore.SIGNAL("completedItem"), arg)

    def passOnUncompletedSignal(self, arg):
        '''
        the child dialog has emitted a signal... pass it on
        '''
        self.parent.parent().emit(QtCore.SIGNAL("unCompletedItem"), arg)

    def passOnApplyFeeNowSignal(self, arg):
        '''
        the child dialog has emitted a signal... pass it on
        '''
        self.parent.parent().emit(QtCore.SIGNAL("applyFeeNow"), arg)

    def passOnDeleteItemSignal(self, arg):
        '''
        the child dialog has emitted a signal... pass it on
        '''
        print "passing on delete message"
        self.parent.parent().ests.remove(arg)
        self.parent.parent().emit(QtCore.SIGNAL("deleteItem"), arg)

class estWidget(QtGui.QFrame):
    '''
    provides a custom widget to view/edit the patient's estimate
    currently 4 view choices.
    0 = standard
    1 = expanded
    2 = seperate plan/completed
    3 = seperate plan/completed expanded
    '''
    def __init__(self, parent=None):
        super(estWidget, self).__init__(parent)
        self.setSizePolicy(QtGui.QSizePolicy(
        QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding))

        self.estimate_layout = QtGui.QVBoxLayout(self)
        self.estimate_layout.setSpacing(0)

        header = QtGui.QWidget()
        estHeader = Ui_estHeaderWidget.Ui_Form()
        estHeader.setupUi(header)
        self.estimate_layout.addWidget(header)

        footer = QtGui.QWidget()
        self.planFooter = Ui_estFooterWidget.Ui_Form()
        self.planFooter.setupUi(footer)
        self.planFooter.label.setText("Planned Items Total")
        self.estimate_layout.addWidget(footer)

        footer = QtGui.QWidget()
        self.compFooter = Ui_estFooterWidget.Ui_Form()
        self.compFooter.setupUi(footer)
        self.compFooter.label.setText("Completed Items Total")
        self.estimate_layout.addWidget(footer)

        footer = QtGui.QWidget()
        self.estFooter = Ui_estFooterWidget.Ui_Form()
        self.estFooter.setupUi(footer)
        self.estimate_layout.addWidget(footer)

        self.estimate_layout.addStretch(-1)
        self.estItemWidgets = []
        self.ests = ()

        #-- a couple of booleans to help set a tri-state checkbox
        self.allCompleted = True
        self.allPlanned = True

        self.bareMinimumHeight = header.height() + footer.height()

        self.setMinimumSize(self.minimumSizeHint())

    def minimumSizeHint(self):
        height = self.bareMinimumHeight
        height += len(self.estItemWidgets) * 28
        return QtCore.QSize(720, height)

    def updateTotals(self):
        self.total = 0
        self.ptTotal = 0
        plan_total = 0
        planpt_total = 0
        comp_total = 0
        compt_total = 0

        self.allCompleted = True
        self.allPlanned = True
        for est in self.ests:
            if est.completed:
                self.allPlanned = False
                comp_total += est.fee
                compt_total += est.ptfee
            else:
                self.allCompleted = False
                plan_total += est.fee
                planpt_total += est.ptfee
            self.total += est.fee
            self.ptTotal += est.ptfee

        self.estFooter.fee_lineEdit.setText("%.02f"% (self.total/100))
        self.estFooter.ptfee_lineEdit.setText("%.02f"% (self.ptTotal/100))
        self.planFooter.fee_lineEdit.setText("%.02f"% (plan_total/100))
        self.planFooter.ptfee_lineEdit.setText("%.02f"% (planpt_total/100))
        self.compFooter.fee_lineEdit.setText("%.02f"% (comp_total/100))
        self.compFooter.ptfee_lineEdit.setText("%.02f"% (compt_total/100))

    def findExistingItemWidget(self, item):
        for widg in self.estItemWidgets:
            if widg.itemCode == item.itemcode and \
            widg.items[0].description == item.description:
                widg.addItem(item)
                return True

    def setEstimate(self, ests, SPLIT_ALL=False):
        self.ests = ests
        self.clear()
        for item in self.ests:
            if not SPLIT_ALL and self.findExistingItemWidget(item):
                #-- try and match with existing items
                print "added est to an existing widget item"
            else:
                #--creates a widget
                iw = QtGui.QWidget(self)
                i = estItemWidget(iw)
                i.setItem(item)
                iw.connect(iw, QtCore.SIGNAL("user_interaction"),
                self.updateTotals)

                iw.connect(iw, QtCore.SIGNAL("deleteMe"), self.deleteItemWidget)

                iw.connect(iw, QtCore.SIGNAL("completedItem"),
                self.itemCompletionState)

                self.estItemWidgets.append(i)
                self.estimate_layout.insertWidget(1, iw)
        self.setMinimumSize(self.minimumSizeHint())
        self.updateTotals()

    def itemCompletionState(self, item):
        if item.completed:
            amountToRaise = item.ptfee
            self.emit(QtCore.SIGNAL("completedItem"), item.type)
        else:
            amountToRaise = item.ptfee * -1
            self.emit(QtCore.SIGNAL("unCompletedItem"), item.type)

        ##TODO this signal should include the coursetype!!
        self.emit(QtCore.SIGNAL("applyFeeNow"), (amountToRaise))

    def clear(self):
        '''
        clears all est widget in anticipation of a new estimate
        '''
        while self.estItemWidgets != []:
            widg = self.estItemWidgets.pop()
            self.estimate_layout.removeWidget(widg.parent)
            widg.parent.setParent(None)

        self.updateTotals()

    def deleteItemWidget(self, arg):
        '''
        deletes a widget when delete button pressed.
        '''
        print arg.items
        message = "Delete %s %s from estimate?"%(
        arg.number_label.text(), arg.description_lineEdit.text())
        input = QtGui.QMessageBox.question(self, "confirm",
        message, QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)

        if input == QtGui.QMessageBox.Yes:
            est = arg.items[0]
            self.ests.remove(est)
            self.emit(QtCore.SIGNAL("deleteItem"), est)

            self.estimate_layout.removeWidget(arg.parent)
            arg.parent.setParent(None)
            #for est in self.ests:
            #    if est.ix == arg.items[0].ix and est.type == arg.items[0].type:
            #        self.ests.remove(est)
            #        self.emit(QtCore.SIGNAL("deleteItem"), est)

            self.updateTotals()

if __name__ == "__main__":
    def CatchAllSignals(arg=None):
        '''test procedure'''
        print "signal caught argument=", arg
        print "estimates",  form.ests
    import sys

    app = QtGui.QApplication(sys.argv)

    from openmolar.dbtools import patient_class
    pt = patient_class.patient(3)
    form = estWidget()
    form.setEstimate(pt.estimates)
    form.connect(form, QtCore.SIGNAL("completedItem"), CatchAllSignals)
    form.connect(form, QtCore.SIGNAL("unCompletedItem"), CatchAllSignals)
    form.connect(form, QtCore.SIGNAL("applyFeeNow"), CatchAllSignals)
    form.connect(form, QtCore.SIGNAL("deleteItem"), CatchAllSignals)

    form.show()

    sys.exit(app.exec_())
