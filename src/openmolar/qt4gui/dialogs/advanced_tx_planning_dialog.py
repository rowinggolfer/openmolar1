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

from gettext import gettext as _
import re

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from openmolar.dbtools.treatment_course import CURRTRT_ROOT_ATTS
from openmolar.qt4gui.customwidgets.upper_case_line_edit \
    import UpperCaseLineEdit
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog


class TxDisplayWidget(QtWidgets.QWidget):
    text_edited = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.pl_lineedit = UpperCaseLineEdit()
        self.cmp_lineedit = UpperCaseLineEdit()

        icon = QtGui.QIcon(":forward.png")
        but = QtWidgets.QPushButton()
        but.setIcon(icon)
        but.setMaximumWidth(30)
        but.clicked.connect(self._complete_treatments)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setSpacing(1)
        layout.addWidget(self.pl_lineedit)
        layout.addWidget(but)
        layout.addWidget(self.cmp_lineedit)

    def set_plan_text(self, text):
        self._initial_pl_text = text
        self.pl_lineedit.setText(text)
        self.pl_lineedit.textChanged.connect(self.text_edited.emit)

    def set_completed_text(self, text):
        self._initial_cmp_text = text
        self.cmp_lineedit.setText(text)
        self.cmp_lineedit.textChanged.connect(self.text_edited.emit)

    def _complete_treatments(self):
        self.cmp_lineedit.setText("%s %s" % (self.cmp_text, self.plan_text))
        self.pl_lineedit.setText("")

    @property
    def plan_text(self):
        txt = str(self.pl_lineedit.text())
        # denture codes are dumb!
        return re.sub("SR\ ", "SR_", txt)

    @property
    def cmp_text(self):
        txt = str(self.cmp_lineedit.text())
        # denture codes are dumb!
        return re.sub("SR\ ", "SR_", txt)

    @property
    def plan_edited(self):
        return self.plan_text != self._initial_pl_text

    @property
    def cmp_edited(self):
        return self.cmp_text != self._initial_cmp_text

    @property
    def has_been_edited(self):
        return not (self.plan_edited or self.cmp_edited)


class AdvancedTxPlanningDialog(ExtendableDialog):
    SHOW_CHART_ITEMS = False

    def __init__(self, parent=None):
        ExtendableDialog.__init__(self, parent, remove_stretch=True)
        self.setWindowTitle(_("Advanced Treatment Planning"))

        self.om_gui = parent
        self.pt = self.om_gui.pt
        self.widgets = {}
        frame = QtWidgets.QFrame()
        form_layout = QtWidgets.QFormLayout(frame)
        form_layout.setSpacing(0)

        plan_header_label = QtWidgets.QLabel(_("Planned Text"))
        plan_header_label.setAlignment(QtCore.Qt.AlignCenter)

        cmp_header_label = QtWidgets.QLabel(_("Completed Text"))
        cmp_header_label.setAlignment(QtCore.Qt.AlignCenter)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(plan_header_label)
        layout.addWidget(cmp_header_label)
        form_layout.addRow(_("Field"), layout)

        tooth_atts = []

        for att in CURRTRT_ROOT_ATTS:
            if re.match("[ul][lr][1-8]", att):
                tooth_atts.append(att)
            else:
                widg = TxDisplayWidget()
                self.widgets[att] = widg
                form_layout.addRow(att, widg)

        chart_frame = QtWidgets.QFrame()
        form_layout2 = QtWidgets.QFormLayout(chart_frame)
        form_layout2.setSpacing(0)

        plan_header_label = QtWidgets.QLabel(_("Planned Text"))
        plan_header_label.setAlignment(QtCore.Qt.AlignCenter)

        cmp_header_label = QtWidgets.QLabel(_("Completed Text"))
        cmp_header_label.setAlignment(QtCore.Qt.AlignCenter)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(plan_header_label)
        layout.addWidget(cmp_header_label)
        form_layout2.addRow(_("Field"), layout)

        for att in tooth_atts:
            widg = TxDisplayWidget()
            self.widgets[att] = widg
            form_layout2.addRow(att, widg)

        left_scroll_area = QtWidgets.QScrollArea()
        left_scroll_area.setWidget(frame)
        left_scroll_area.setWidgetResizable(True)

        self.chart_scroll_area = QtWidgets.QScrollArea()
        self.chart_scroll_area.setWidget(chart_frame)
        self.chart_scroll_area.setWidgetResizable(True)

        upper_frame = QtWidgets.QFrame()
        layout = QtWidgets.QHBoxLayout(upper_frame)
        layout.addWidget(left_scroll_area)
        layout.addWidget(self.chart_scroll_area)

        self.insertWidget(upper_frame)

        self.deleted_plan_items = []
        self.new_cmp_items = []
        self.deleted_cmp_items = []
        self.new_plan_items = []

        self.load_values()

        self.chart_but = QtWidgets.QPushButton(_("Show Chart Items"))
        self.chart_but.clicked.connect(self._show_chart)
        self.add_advanced_widget(self.chart_but)
        self.chart_scroll_area.setVisible(self.SHOW_CHART_ITEMS)

    def load_values(self):
        if self.pt is None:
            return
        for att in CURRTRT_ROOT_ATTS:
            pl = self.pt.treatment_course.__dict__["%spl" % att]
            cmp = self.pt.treatment_course.__dict__["%scmp" % att]
            widg = self.widgets[att]
            widg.set_plan_text(pl)
            widg.set_completed_text(cmp)

            widg.text_edited.connect(self.check_appliable)

    def _show_chart(self):
        self.SHOW_CHART_ITEMS = not self.SHOW_CHART_ITEMS
        self.chart_scroll_area.setVisible(self.SHOW_CHART_ITEMS)
        self.show_extension(False)
        self.resize(self.sizeHint())
        if self.SHOW_CHART_ITEMS:
            self.chart_but.setText(_("Hide Chart Items"))
        else:
            self.chart_but.setText(_("Show Chart Items"))

    def check_appliable(self):
        for widg in list(self.widgets.values()):
            if widg.has_been_edited:
                self.enableApply()
                return
        self.enableApply(False)

    def sizeHint(self):
        if self.SHOW_CHART_ITEMS:
            return QtCore.QSize(800, 600)
        return QtCore.QSize(500, 500)

    @property
    def _new_plan_items(self):
        for att in CURRTRT_ROOT_ATTS:
            att_widg = self.widgets[att]
            if att_widg.plan_edited:
                exist_items = \
                    self.pt.treatment_course.__dict__["%spl" % att].split(" ")
                new_list = att_widg.plan_text.split(" ")
                for item in set(new_list):
                    if item == "":
                        continue
                    n_adds = new_list.count(item) - exist_items.count(item)
                    for i in range(n_adds):
                        yield att, item

    @property
    def _new_cmp_items(self):
        for att in CURRTRT_ROOT_ATTS:
            att_widg = self.widgets[att]
            if att_widg.cmp_edited:
                exist_items = \
                    self.pt.treatment_course.__dict__["%scmp" % att].split(" ")
                new_list = att_widg.cmp_text.split(" ")
                for item in set(new_list):
                    if item == "":
                        continue
                    n_adds = new_list.count(item) - exist_items.count(item)
                    for i in range(n_adds):
                        yield att, item

    @property
    def _deleted_plan_items(self):
        for att in CURRTRT_ROOT_ATTS:
            att_widg = self.widgets[att]
            if att_widg.plan_edited:
                new_items = att_widg.plan_text.split(" ")
                exist_items = \
                    self.pt.treatment_course.__dict__["%spl" % att].split(" ")
                for item in set(exist_items):
                    if item == "":
                        continue
                    n_adds = exist_items.count(item) - new_items.count(item)
                    for i in range(n_adds):
                        yield att, item

    @property
    def _deleted_cmp_items(self):
        for att in CURRTRT_ROOT_ATTS:
            att_widg = self.widgets[att]
            if att_widg.cmp_edited:
                new_items = att_widg.cmp_text.split(" ")
                exist_items = \
                    self.pt.treatment_course.__dict__["%scmp" % att].split(" ")
                for item in set(exist_items):
                    if item == "":
                        continue
                    n_adds = exist_items.count(item) - new_items.count(item)
                    for i in range(n_adds):
                        yield att, item

    @property
    def completed_items(self):
        planned = list(self._deleted_plan_items)
        for item in self._new_cmp_items:
            if item in planned:
                yield item

    @property
    def reversed_items(self):
        completed = list(self._deleted_cmp_items)
        for item in self._new_plan_items:
            if item in completed:
                yield item

    def exec_(self):
        if ExtendableDialog.exec_(self):

            self.deleted_plan_items = list(self._deleted_plan_items)
            self.new_cmp_items = list(self._new_cmp_items)
            for item in self.completed_items:
                try:
                    self.deleted_plan_items.remove(item)
                except ValueError:
                    pass
                try:
                    self.new_cmp_items.remove(item)
                except ValueError:
                    pass

            self.deleted_cmp_items = list(self._deleted_cmp_items)
            self.new_plan_items = list(self._new_plan_items)
            for item in self.reversed_items:
                try:
                    self.deleted_cmp_items.remove(item)
                except ValueError:
                    pass
                try:
                    self.new_plan_items.remove(item)
                except ValueError:
                    pass

            return True

        return False
