#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ############################################################################ #
# #                                                                          # #
# # Copyright (c) 2009-2014 Neil Wallace <neil@openmolar.com>                # #
# #                                                                          # #
# # This file is part of OpenMolar.                                          # #
# #                                                                          # #
# # OpenMolar is free software: you can redistribute it and/or modify        # #
# # it under the terms of the GNU General Public License as published by     # #
# # the Free Software Foundation, either version 3 of the License, or        # #
# # (at your option) any later version.                                      # #
# #                                                                          # #
# # OpenMolar is distributed in the hope that it will be useful,             # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of           # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # #
# # GNU General Public License for more details.                             # #
# #                                                                          # #
# # You should have received a copy of the GNU General Public License        # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.       # #
# #                                                                          # #
# ############################################################################ #

from collections import namedtuple
from functools import partial

from PyQt4 import QtCore, QtGui

from openmolar.settings import localsettings
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog

# these lists are shortcut, description, tooltip

FS_ITEMS = (
    ("FS", _("Fissure Sealant"), ""),
    ("FS,CO", _("PRR restoration with composite"), ""),
)

ENDO_ITEMS = (
    ("PX", _("Pulp Extirpation - 1 canal"), ""),
    ("PX+", _("Pulp Extirpation - multiple canals"), ""),
    ("RT", _("Root Canal"), ""),
    ("IE", _("Incomplete Endodontics"), ""),
)

SURGICAL_ITEMS = (
    ("EX", _("Extraction"), ""),
    ("EX/S1", _("Surgical Extraction"), ""),
    ("AP", _("Apicectomy"), ""),
)


class ChartTxChoiceDialog(ExtendableDialog):
    FS_ITEMS = FS_ITEMS
    ENDO_ITEMS = ENDO_ITEMS
    SURGICAL_ITEMS = SURGICAL_ITEMS

    def __init__(self, static, parent=None):
        ExtendableDialog.__init__(self, parent, remove_stretch=True)
        self.setWindowTitle(_("Chart Treatment Choice Dialog"))
        self.om_gui = parent
        self.chosen_shortcut = None

        scroll_area = QtGui.QScrollArea()
        frame = QtGui.QFrame()
        scroll_area.setWidget(frame)
        scroll_area.setWidgetResizable(True)
        self.but_layout = QtGui.QVBoxLayout(frame)
        self.insertWidget(scroll_area)

        self.apply_but.hide()
        self.all_tx_buttons = []
        if static:
            self.more_but.hide()
        else:
            all_tx_but = QtGui.QPushButton(
                _("Show Treatments from all feescales"))
            all_tx_but.clicked.connect(self._show_all_txs)
            self.add_advanced_widget(all_tx_but)

    def sizeHint(self):
        return QtCore.QSize(300, 300)

    def set_items(self, items):
        but_list = []
        for shortcut, description, tooltip in items:
            button = namedtuple('Button',
                               ("shortcut", "description", "tooltip"))
            button.description = description
            button.tooltip = ""
            button.shortcut = shortcut
            but_list.append(button)
        self.add_buttons(but_list)

    def add_buttons(self, chart_buttons, all_tx_buttons=[]):
        self.all_tx_buttons = all_tx_buttons
        while self.but_layout.count():
            widget_item = self.but_layout.takeAt(0)
            try:
                widget_item.widget().setParent(None)
            except AttributeError:  # stretch item has no attribute "widget"
                pass

        if chart_buttons == []:
            label = QtGui.QLabel(_(
                                 "No Matching items to show. "
                                 "Perhaps this is due to the feescale for this patient?"))
            label.setWordWrap(True)
            self.but_layout.addWidget(label)
        for button in chart_buttons:
            but = QtGui.QPushButton(button.description)
            but.setToolTip(button.tooltip)
            but.clicked.connect(
                partial(self.but_clicked, button.shortcut))
            self.but_layout.addWidget(but)
        self.but_layout.addStretch(100)

    def but_clicked(self, shortcut):
        self.chosen_shortcut = shortcut
        self.accept()

    def _show_all_txs(self):
        if self.all_tx_buttons == []:
            QtGui.QMessageBox.information(self, _("Error"),
                                          _("No items of this type have found in any feescale"))
        self.add_buttons(self.all_tx_buttons)
        self.hide_extension()


if __name__ == "__main__":
    from gettext import gettext as _
    from openmolar.dbtools.patient_class import patient

    app = QtGui.QApplication([])
    mw = QtGui.QWidget()
    mw.pt = patient(11956)
    dl = ChartTxChoiceDialog(True, mw)
    dl.set_items(dl.FS_ITEMS)
    if dl.exec_():
        print dl.chosen_shortcut
    dl.set_items(dl.ENDO_ITEMS)
    if dl.exec_():
        print dl.chosen_shortcut
    dl.set_items(dl.SURGICAL_ITEMS)
    if dl.exec_():
        print dl.chosen_shortcut

    dl = ChartTxChoiceDialog(False, mw)
    dl.add_buttons([])
    if dl.exec_():
        print dl.chosen_shortcut
