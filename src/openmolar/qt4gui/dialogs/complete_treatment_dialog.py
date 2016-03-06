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

from functools import partial
from gettext import gettext as _
import logging

from PyQt4 import QtCore, QtGui

from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog

LOGGER = logging.getLogger("openmolar")


class CompleteTreatmentDialog(ExtendableDialog):

    def __init__(self, treatments, parent=None):
        ExtendableDialog.__init__(self, parent, remove_stretch=True)
        self.om_gui = parent

        LOGGER.debug("CompleteTreatmentDialog %s" % treatments)
        self.setWindowTitle(_("Complete Multiple Treatments"))

        label = QtGui.QLabel(
            "%s<br />%s" % (
                _("You have selected multiple treatments."),
                _("Please complete, reverse or delete then apply changes.")))
        self.insertWidget(label)

        self.treatments = treatments

        scroll_area = QtGui.QScrollArea()
        frame = QtGui.QFrame()
        scroll_area.setWidget(frame)
        scroll_area.setWidgetResizable(True)

        self.but_layout = QtGui.QGridLayout(frame)
        row = 0

        col = 1
        for header in (_("Planned"), _("Completed")):
            label = QtGui.QLabel("<b>%s</b>" % header)
            label.setAlignment(QtCore.Qt.AlignCenter)
            self.but_layout.addWidget(label, row, col)
            col += 1

        delete_icon = icon = QtGui.QIcon(":/eraser.png")
        self.uncomplete_icon = QtGui.QIcon(":back.png")
        self.complete_icon = QtGui.QIcon(":forward.png")

        for i, (att, treatment, completed) in enumerate(treatments):
            row = i + 1
            label = QtGui.QLabel(
                "%s - <b>%s</b>" % (att.upper(), treatment.upper()))
            label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self.but_layout.addWidget(label, row, 0)

            if completed:
                icon = self.uncomplete_icon
                col = 1
            else:
                icon = self.complete_icon
                col = 0
            but = QtGui.QPushButton(icon, "")
            but.setIconSize(QtCore.QSize(10, 10))
            but.setMaximumWidth(50)
            self.but_layout.addWidget(but, row, col + 1)

            but.clicked.connect(partial(self._but_clicked, row))

            but = QtGui.QPushButton(delete_icon, "")
            but.setIconSize(QtCore.QSize(20, 20))
            but.setMaximumWidth(50)

            self.but_layout.addWidget(but, row, 3)

            but.clicked.connect(partial(self._del_but_clicked, row))

        self.but_layout.addItem(QtGui.QSpacerItem(0, 10))
        self.but_layout.setRowStretch(row + 1, 2)

        but_frame = QtGui.QFrame()
        layout = QtGui.QHBoxLayout(but_frame)
        layout.setMargin(0)
        complete_all_but = QtGui.QPushButton(
            self.complete_icon, _("Complete All"))

        self.reverse_all_but = QtGui.QPushButton(
            self.uncomplete_icon, _("Reverse All"))

        complete_all_but.clicked.connect(self._complete_all)
        self.reverse_all_but.clicked.connect(self._reverse_all)

        layout.addWidget(complete_all_but)
        layout.addWidget(self.reverse_all_but)

        self.insertWidget(scroll_area)
        self.insertWidget(but_frame)

        # no advanced options yet
        self.more_but.hide()

    def sizeHint(self):
        height = 200 + 50 * len(self.treatments)
        if height > 500:
            height = 500
        return QtCore.QSize(300, height)

    def hide_reverse_all_but(self):
        self.reverse_all_but.hide()

    def _del_but_clicked(self, row):
        but = self.sender()
        label = self.but_layout.itemAtPosition(row, 0).widget()
        label.setStyleSheet("")
        label.setEnabled(False)
        for col in range(1, 3):
            item = self.but_layout.itemAtPosition(row, col)
            if item is not None:
                item.widget().hide()

        but.setEnabled(False)

        self._enable()

    def _but_clicked(self, row):
        but = self.sender()

        label = self.but_layout.itemAtPosition(row, 0).widget()
        if "red" in label.styleSheet():
            label.setStyleSheet("")
        else:
            label.setStyleSheet("color:red;")

        if self.but_layout.itemAtPosition(row, 1) is None:
            icon = self.complete_icon
            col = 1
        else:
            icon = self.uncomplete_icon
            col = 2

        but.setIcon(icon)
        self.but_layout.addWidget(but, row, col)

        self._enable()

    def _complete_all(self):
        for button in self.plan_buttons:
            button.click()

    def _reverse_all(self):
        for button in self.cmp_buttons:
            button.click()

    def _enable(self):
        for val in self.completed_treatments:
            self.enableApply()
            return
        for val in self.uncompleted_treatments:
            self.enableApply()
            return
        for val in self.deleted_treatments:
            self.enableApply()
            return
        self.enableApply(False)

    @property
    def all_completed(self):
        return list(self.plan_buttons) == []

    @property
    def all_planned(self):
        return list(self.cmp_buttons) == []

    @property
    def plan_buttons(self):
        '''
        iterate and return all buttons in the left column
        '''
        for i in range(len(self.treatments)):
            row = i + 1
            item = self.but_layout.itemAtPosition(row, 1)
            if item is not None:
                yield item.widget()

    @property
    def cmp_buttons(self):
        '''
        iterate and return all buttons in the right column
        '''
        for i in range(len(self.treatments)):
            row = i + 1
            item = self.but_layout.itemAtPosition(row, 2)
            if item is not None:
                yield item.widget()

    @property
    def uncompleted_treatments(self):
        for i, (att, treat, prev_completed) in enumerate(self.treatments):
            row = i + 1
            now_planned = self.but_layout.itemAtPosition(row, 2) is None
            if now_planned and prev_completed:
                yield (att, treat)

    @property
    def completed_treatments(self):
        for i, (att, treat, prev_completed) in enumerate(self.treatments):
            row = i + 1
            now_completed = self.but_layout.itemAtPosition(row, 1) is None
            if now_completed and not prev_completed:
                yield (att, treat)

    @property
    def deleted_treatments(self):
        for i, (att, treat, prev_completed) in enumerate(self.treatments):
            row = i + 1
            if not self.but_layout.itemAtPosition(row, 0).widget().isEnabled():
                yield (att, treat, prev_completed)


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtGui.QApplication([])
    mw = QtGui.QWidget()

    dl = CompleteTreatmentDialog([("perio", "SP", False),
                                  ("perio", "SP", True),
                                  ("ur5", "MOD", False),
                                  ("ur5", "RT", False),
                                  ("ur4", "DR", True)], mw)
    if dl.exec_():
        for att, treat in dl.completed_treatments:
            print("%s %s was completed" % (att, treat))
        for att, treat in dl.uncompleted_treatments:
            print("%s %s was reversed" % (att, treat))
        for att, treat, completed in dl.deleted_treatments:
            print("%s %s %s was deleted" % (att, treat, completed))
