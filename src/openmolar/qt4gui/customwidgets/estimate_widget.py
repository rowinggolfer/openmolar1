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
from estimate_item_widget import decimalise, EstimateItemWidget
from openmolar.qt4gui.compiled_uis import Ui_estSplitItemsDialog

import logging
LOGGER = logging.getLogger("openmolar")

class EstimateWidget(QtGui.QWidget):
    '''
    provides a custom widget to view/edit the patient's estimate
    '''
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        size_policy = QtGui.QSizePolicy(
            QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        
        self.setSizePolicy(size_policy)

        self.expandAll = False
        
        #header labels
        self.number_label = QtGui.QLabel(_("No."))
        self.code_label = QtGui.QLabel(_("Code"))
        self.description_label = QtGui.QLabel(_("Description"))
        self.description_label.setMinimumWidth(120)
        self.cset_label = QtGui.QLabel(_("CSET"))
        self.fee_label = QtGui.QLabel(_("Fee"))
        self.charge_label = QtGui.QLabel(_("Charge"))
        self.expand_all_button = QtGui.QPushButton(_("Expand All"))
        
        self.g_layout = QtGui.QGridLayout(self)
        self.g_layout.setSpacing(0)
        
        self.g_layout.addWidget(self.number_label, 0, 0)
        self.g_layout.addWidget(self.code_label, 0, 1)
        self.g_layout.addWidget(self.description_label, 0, 2)
        self.g_layout.addWidget(self.cset_label, 0, 3)
        self.g_layout.addWidget(self.fee_label, 0, 4)
        self.g_layout.addWidget(self.charge_label, 0, 6)
        
        self.g_layout.addWidget(self.expand_all_button, 0,7,1,2)

        self.planned_fees_total_le = QtGui.QLineEdit()
        self.planned_charges_total_le = QtGui.QLineEdit()
        
        self.completed_fees_total_le = QtGui.QLineEdit()
        self.completed_charges_total_le = QtGui.QLineEdit()
        
        self.fees_total_le = QtGui.QLineEdit()
        self.charges_total_le = QtGui.QLineEdit()
        
        for le in (
            self.planned_fees_total_le, 
            self.completed_fees_total_le,
            self.fees_total_le,
            self.charges_total_le,
            self.planned_charges_total_le,
            self.completed_charges_total_le):
            le.setFixedWidth(EstimateItemWidget.MONEY_WIDTH)
            le.setAlignment(QtCore.Qt.AlignRight)
            
        self.planned_total_label = QtGui.QLabel(_("Planned Items Total"))
        self.completed_total_label = QtGui.QLabel(_("Completed Items Total"))
        self.total_label = QtGui.QLabel(_("TOTAL"))
        
        alignment = QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter
        self.planned_total_label.setAlignment(alignment)
        self.completed_total_label.setAlignment(alignment)
        self.total_label.setAlignment(alignment)
       
        self.estItemWidgets = []
        self.ests = ()

        self.setMinimumSize(self.minimumSizeHint())
        self.expand_all_button.clicked.connect(self.expandItems)
        
    def add_footer(self):
        row = len(self.estItemWidgets)
        
        spacer_item = QtGui.QSpacerItem(0, 100)
        self.g_layout.addItem(spacer_item, row+1, 0, 1, 9)
        self.g_layout.setRowStretch(row+1, 2)
        
        row += 2
        for i, label in enumerate(
            (self.planned_total_label,
            self.completed_total_label,
            self.total_label)
            ):
            self.g_layout.addWidget(label, row + 3 + i, 2, 1, 2)
        
        self.g_layout.addWidget(self.planned_fees_total_le, 3+row,4)
        self.g_layout.addWidget(self.planned_charges_total_le, 3+row,6)
        
        self.g_layout.addWidget(self.completed_fees_total_le, 4+row,4)
        self.g_layout.addWidget(self.completed_charges_total_le, 4+row,6)

        self.g_layout.addWidget(self.fees_total_le, 5+row,4)
        self.g_layout.addWidget(self.charges_total_le, 5+row,6)
        
    def minimumSizeHint(self):
        min_height = 120 + len(self.estItemWidgets) * 28
        return QtCore.QSize(720, min_height)
        
    def updateTotals(self):
        self.total = 0
        self.ptTotal = 0
        plan_total = 0
        planpt_total = 0
        comp_total = 0
        compt_total = 0

        for est in self.ests:
            if est.completed:
                comp_total += est.fee
                compt_total += est.ptfee
            else:
                plan_total += est.fee
                planpt_total += est.ptfee
            self.total += est.fee
            self.ptTotal += est.ptfee

        self.fees_total_le.setText(decimalise(self.total))
        self.charges_total_le.setText(decimalise(self.ptTotal))
        self.planned_fees_total_le.setText(decimalise(plan_total))
        self.planned_charges_total_le.setText(decimalise(planpt_total))
        self.completed_fees_total_le.setText(decimalise(comp_total))
        self.completed_charges_total_le.setText(decimalise(compt_total))

    def findExistingItemWidget(self, item):
            
        otherTypes =  item.itemcode in ("4001", "4002")
        for widg in self.estItemWidgets:
            if widg.itemCode == item.itemcode :
                if otherTypes:
                    for exist_item in widg.est_items:
                        if item.description == exist_item.description:                
                            widg.addItem(item)
                            return True
                else:
                    widg.addItem(item)
                    return True

    def setEstimate(self, ests, SPLIT_ALL=None):
        '''
        adds all estimate items to the gui
        '''
        if SPLIT_ALL is not None:
            self.expandAll = SPLIT_ALL
        self.ests = ests
        self.clear()
        if self.expandAll:
            self.expand_all_button.setText("Compress All")
        else:
            self.expand_all_button.setText("Expand All")
        
        row = 1
        for item in self.ests:
            #- check to see if similar items exist already, if not, add a
            #- widget
            
            if self.expandAll or not self.findExistingItemWidget(item):
                #--creates a widget
                widg = EstimateItemWidget(self)
                widg.addItem(item)
                
                widg.edited_signal.connect(self.updateTotals)
                widg.completed_signal.connect(self.itemCompletionState)
                widg.delete_signal.connect(self.deleteItemWidget)
                widg.separate_signal.connect(self.splitMultiItemDialog)

                self.estItemWidgets.append(widg)
                
                self.g_layout.addWidget(widg.number_label, row, 0)
                self.g_layout.addWidget(widg.itemCode_label, row, 1)
                self.g_layout.addWidget(widg.description_lineEdit, row, 2)
                self.g_layout.addWidget(widg.cset_lineEdit, row, 3)
                self.g_layout.addWidget(widg.fee_lineEdit, row, 4)
                self.g_layout.addWidget(widg.chain, row, 5)
                self.g_layout.addWidget(widg.ptFee_lineEdit, row, 6)
                self.g_layout.addWidget(widg.completed_checkBox, row, 7)
                self.g_layout.addWidget(widg.delete_pushButton, row, 8)
                self.g_layout.setRowStretch(row, 0)
                row += 1
                
        self.add_footer()
        
        self.setMinimumSize(self.minimumSizeHint())
        self.updateTotals()

    def itemCompletionState(self, item):
        LOGGER.debug("itemCompletionState - emmitting signal")
        #self.setEstimate(self.ests)
        if item.completed:
            self.emit(QtCore.SIGNAL("completedItem"), item)
        else:
            self.emit(QtCore.SIGNAL("unCompletedItem"), item)

    def clear(self):
        '''
        clears all est widget in anticipation of a new estimate
        '''
        while self.estItemWidgets != []:
            widg = self.estItemWidgets.pop()
            widg.completed_checkBox.check_first = None
            for child in widg.components():
                self.g_layout.removeWidget(child)
                child.setParent(None)
            widg.setParent(None)
        self.updateTotals()

    def deleteItemWidget(self, item_widget, confirm_first=True):
        '''
        deletes a widget when delete button pressed.
        '''
        message = u"<p>%s %s %s<br />%s?</p>"%(
            _("Delete"),
            item_widget.number_label.text(), 
            item_widget.description_lineEdit.text(),
            _("from treatment plan and estimate")
            )

        if not confirm_first or QtGui.QMessageBox.question(self, "confirm",
        message, QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
        QtGui.QMessageBox.Yes ) == QtGui.QMessageBox.Yes:
            est = item_widget.est_items[0]
            self.ests.remove(est)
            self.emit(QtCore.SIGNAL("deleteItem"), est)

            item_widget.setParent(None)

            self.setEstimate(self.ests, self.expandAll)
            return True
        
    def expandItems(self):
        '''
        user has clicked the expand button in the header
        '''
        self.setEstimate(self.ests, not self.expandAll)

    def splitMultiItemDialog(self, est_item_widget):
        '''
        a scissors button has been clicked
        call up a dialog to split the items
        '''
        def delete_item(item_widget):
            print "delete item", item_widget
            if EstimateWidget.deleteItemWidget(ew, item_widget):
                self.deleteItemWidget(item_widget, confirm_first = False)
            
            # if the mini dialog has only one item.. it is no longer needed!
            if len(est_item_widget.est_items) <= 1:
                dialog.accept()
            
        dialog = QtGui.QDialog(self)
        dl = Ui_estSplitItemsDialog.Ui_Dialog()
        dl.setupUi(dialog)
        ew = EstimateWidget()
        ew.expandAll = True
        ew.deleteItemWidget = delete_item
        ew.setEstimate(est_item_widget.est_items, True)
        dl.scrollArea.setWidget(ew)

        #-- this miniDialog emits signals that go uncaught
    
        if dialog.exec_():
            self.setEstimate(self.ests)
        
    @property
    def allPlanned(self):
        for est in self.ests:
            if est.completed:
                return False
        return True
    
    @property
    def allCompleted(self):
        for est in self.ests:
            if not est.completed:
                return False
        return True

    
    def allow_check(self, est_item_widget):
        '''
        check to see if est_widget can be checked by the user
        (in the case of multiple identical treatment items, there is a 
        specific allowable order)
        '''
        check_first = False
        affected_est = est_item_widget.est_items[0]
        for est in self.ests:
            if (est.itemcode == affected_est.itemcode and 
            est.tx_hashes != affected_est.tx_hashes):
                check_first = True
                break
        
        if check_first:
            LOGGER.debug("estimate_widget.allow_check %s"% est_item_widget)
            result = QtGui.QMessageBox.information(self, "info",
            "just checking before (un)checking!",
            QtGui.QMessageBox.Ok|QtGui.QMessageBox.Cancel
            )== QtGui.QMessageBox.Ok
            
            return result
        
        return True

    
if __name__ == "__main__":
    def CatchAllSignals(arg=None):
        '''test procedure'''
        print "signal caught argument=", arg
    
    LOGGER.setLevel(logging.DEBUG)
    
    from gettext import gettext as _
    from openmolar.dbtools import patient_class
    pt = patient_class.patient(11956)

    app = QtGui.QApplication([])

    form = QtGui.QMainWindow()
    widg = EstimateWidget()
    form.setCentralWidget(widg)
    form.show()
    
    widg.setEstimate(pt.estimates)
    
    form.connect(widg, QtCore.SIGNAL("completedItem"), CatchAllSignals)
    form.connect(widg, QtCore.SIGNAL("unCompletedItem"), CatchAllSignals)
    form.connect(widg, QtCore.SIGNAL("deleteItem"), CatchAllSignals)

    form.show()
    #QtCore.QTimer.singleShot(2000, widg.clear)
    app.exec_()
