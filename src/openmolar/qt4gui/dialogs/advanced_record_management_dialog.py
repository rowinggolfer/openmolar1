#! /usr/bin/python

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2016 Neil Wallace <neil@openmolar.com>               # #
# #                                                                         # #
# # This file is part of OpenMolar.                                         # #
# #                                                                         # #
# # OpenMolar is free software: you can redistribute it and/or modify       # #
# # it under the terms of the GNU General Public License as published by    # #
# # the Free Software Foundation, either version 3 of the License, or       # #
# # (at your option) any later version.                                     # #
# #                                                                         # #
# # OpenMolar is distributed in the hope that it will be useful,            # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of          # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           # #
# # GNU General Public License for more details.                            # #
# #                                                                         # #
# # You should have received a copy of the GNU General Public License       # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.      # #
# #                                                                         # #
# ########################################################################### #

import logging

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar.settings import localsettings
from openmolar.qt4gui.compiled_uis import Ui_record_tools

from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

LOGGER = logging.getLogger("openmolar")


class AdvancedRecordManagementDialog(BaseDialog):

    def __init__(self, pt, parent):
        BaseDialog.__init__(self, parent, remove_stretch=True)
        self.pt = pt
        self.om_gui = parent
        widget = QtWidgets.QWidget(self)
        self.ui = Ui_record_tools.Ui_Form()
        self.ui.setupUi(widget)

        self.insertWidget(widget)

        self.ui.tabWidget.setCurrentIndex(0)
        self.initialMoney()
        self.initialDates()
        self.initialHidden_notes()
        self.signals()

        self.setMinimumSize(self.sizeHint())

        self.DATE_ATTRIBUTES = (
            self.pt.pd5,
            self.pt.pd6,
            self.pt.pd7,
            self.pt.pd8,
            self.pt.pd9,
            self.pt.pd10,
            self.pt.billdate)

        self.ui.money0_spinBox.setEnabled(False)
        self.ui.money1_spinBox.setEnabled(False)
        self.check_before_reject_if_dirty = True

    def sizeHint(self):
        return QtCore.QSize(600, 600)

    def initialMoney(self):
        '''
        loads the money at startup
        '''
        self.ui.total_label.setText(
            localsettings.formatMoney(self.pt.fees))
        self.ui.money1_spinBox.setValue(self.pt.money1)
        self.ui.money2_spinBox.setValue(self.pt.money2)
        self.ui.money3_spinBox.setValue(self.pt.money3)
        self.ui.money4_spinBox.setValue(self.pt.money4)
        self.ui.money5_spinBox.setValue(self.pt.money5)
        self.ui.money6_spinBox.setValue(self.pt.money6)
        self.ui.money7_spinBox.setValue(self.pt.money7)
        self.ui.money8_spinBox.setValue(self.pt.money8)
        self.ui.money9_spinBox.setValue(self.pt.money9)
        self.ui.money10_spinBox.setValue(self.pt.money10)
        self.ui.money11_spinBox.setValue(self.pt.money11)

    def updateMoneyTotal(self, arg=0):
        '''
        updates the money label
        '''
        fees = (self.ui.money0_spinBox.value() +
                self.ui.money1_spinBox.value() +
                self.ui.money9_spinBox.value() +
                self.ui.money10_spinBox.value() +
                self.ui.money11_spinBox.value() -
                self.ui.money2_spinBox.value() -
                self.ui.money3_spinBox.value() -
                self.ui.money8_spinBox.value()
                )

        self.ui.total_label.setText(localsettings.formatMoney(fees))
        self._check_enable()

    def changeMoney(self):
        '''
        modify the money fields on a patient record
        '''
        self.pt.money0 = self.ui.money0_spinBox.value()
        self.pt.money1 = self.ui.money1_spinBox.value()
        self.pt.money2 = self.ui.money2_spinBox.value()
        self.pt.money3 = self.ui.money3_spinBox.value()
        self.pt.money4 = self.ui.money4_spinBox.value()
        self.pt.money5 = self.ui.money5_spinBox.value()
        self.pt.money6 = self.ui.money6_spinBox.value()
        self.pt.money7 = self.ui.money7_spinBox.value()
        self.pt.money8 = self.ui.money8_spinBox.value()
        self.pt.money9 = self.ui.money9_spinBox.value()
        self.pt.money10 = self.ui.money10_spinBox.value()
        self.pt.money11 = self.ui.money11_spinBox.value()

    @property
    def has_money_changes(self):
        return (
            self.pt.money0 != self.ui.money0_spinBox.value() or
            self.pt.money1 != self.ui.money1_spinBox.value() or
            self.pt.money2 != self.ui.money2_spinBox.value() or
            self.pt.money3 != self.ui.money3_spinBox.value() or
            self.pt.money4 != self.ui.money4_spinBox.value() or
            self.pt.money5 != self.ui.money5_spinBox.value() or
            self.pt.money6 != self.ui.money6_spinBox.value() or
            self.pt.money7 != self.ui.money7_spinBox.value() or
            self.pt.money8 != self.ui.money8_spinBox.value() or
            self.pt.money9 != self.ui.money9_spinBox.value() or
            self.pt.money10 != self.ui.money10_spinBox.value() or
            self.pt.money11 != self.ui.money11_spinBox.value()
        )

    def initialDates(self):
        '''
        modify Date fields
        '''
        def initialise(date_, de, but):
            try:
                de.setDate(date_)
                but.hide()
            except TypeError:
                de.hide()
                but.clicked.connect(de.show)
                but.clicked.connect(but.hide)
            finally:
                but.clicked.connect(self._check_enable)
                de.dateChanged.connect(self._check_enable)

        initialise(self.pt.pd5, self.ui.pd5_dateEdit, self.ui.pd5_pushButton)
        initialise(self.pt.pd6, self.ui.pd6_dateEdit, self.ui.pd6_pushButton)
        initialise(self.pt.pd7, self.ui.pd7_dateEdit, self.ui.pd7_pushButton)
        initialise(self.pt.pd8, self.ui.pd8_dateEdit, self.ui.pd8_pushButton)
        initialise(self.pt.pd9, self.ui.pd9_dateEdit, self.ui.pd9_pushButton)
        initialise(self.pt.pd10, self.ui.pd10_dateEdit,
                   self.ui.pd10_pushButton)
        initialise(self.pt.billdate, self.ui.billdate_dateEdit,
                   self.ui.billdate_pushButton)

    @property
    def new_dates(self):
        for de in (self.ui.pd5_dateEdit,
                   self.ui.pd6_dateEdit,
                   self.ui.pd7_dateEdit,
                   self.ui.pd8_dateEdit,
                   self.ui.pd9_dateEdit,
                   self.ui.pd10_dateEdit,
                   self.ui.billdate_dateEdit
                   ):
            yield de.date().toPyDate() if de.isVisible() else None

    def changeDates(self):
        '''
        apply date changes
        '''
        for i, date_ in enumerate(self.new_dates):
            if date_:
                self.DATE_ATTRIBUTES[i] = date_
        self._check_enable()

    @property
    def has_date_changes(self):
        changed = False
        for i, date_ in enumerate(self.new_dates):
            if date_ and self.DATE_ATTRIBUTES[i] != date_:
                LOGGER.debug("user has changed date from %s to %s",
                             self.DATE_ATTRIBUTES[i], date_)
                changed = True
        return changed

    def initialHidden_notes(self):
        '''
        load the patients hidden notes
        '''
        self.ui.hidden_notes_tableWidget.clear()
        self.ui.hidden_notes_tableWidget.setColumnCount(2)
        self.ui.hidden_notes_tableWidget.setRowCount(
            len(self.pt.HIDDENNOTES))
        header = self.ui.hidden_notes_tableWidget.horizontalHeader()
        self.ui.hidden_notes_tableWidget.setHorizontalHeaderLabels(
            [_("type"), _("note")])
        header.setStretchLastSection(True)
        for row_no, (ntype, note) in enumerate(self.pt.HIDDENNOTES):
            ntype_item = QtWidgets.QTableWidgetItem(ntype)
            self.ui.hidden_notes_tableWidget.setItem(row_no, 0, ntype_item)

            note_item = QtWidgets.QTableWidgetItem(note)
            self.ui.hidden_notes_tableWidget.setItem(row_no, 1, note_item)

        self.ui.hidden_notes_tableWidget.itemChanged.connect(
            self._check_enable)

    @property
    def new_hidden_notes(self):
        '''
        apply new notes
        '''
        HN = []
        for row_no in range(self.ui.hidden_notes_tableWidget.rowCount()):
            ntype = self.ui.hidden_notes_tableWidget.item(row_no, 0).text()
            note = self.ui.hidden_notes_tableWidget.item(row_no, 1).text()

            HN.append((ntype, note))
        return HN

    def changeHidden_notes(self):
        '''
        apply new notes
        '''
        self.pt.HIDDENNOTES = self.new_hidden_notes
        self._check_enable()

    @property
    def has_hidden_note_changes(self):
        return self.new_hidden_notes != self.pt.HIDDENNOTES

    def signals(self):
        '''
        connect signals
        '''
        for widg in self.ui.money_scrollAreaWidgetContents.children():
            if isinstance(widg, QtWidgets.QSpinBox):
                widg.valueChanged.connect(self.updateMoneyTotal)

    def reject(self):
        self.dirty = self.has_changes
        BaseDialog.reject(self)

    @property
    def has_changes(self):
        LOGGER.debug("checking for changes")
        return (self.has_money_changes or
                self.has_date_changes or
                self.has_hidden_note_changes)

    def _check_enable(self):
        self.enableApply(self.has_changes)

    def apply(self):
        LOGGER.warning("advanced record management dialog applying changes")
        self.changeMoney()
        self.changeDates()
        self.changeHidden_notes()
