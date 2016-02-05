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


STATIC_LIST = []
for shortcut, description in (
    ("IM/TIT", _("Titanium Implant")),
    ("IM/ABUT", _("Implant Abutment")),
    ("CR,IC", _("Implant Crown")),
    ("BR/CR,IC", _("Implant Bridge Retainer")),
    ("BR/P,IC", _("Implant Bridge Pontic")),
):
    implant_chart_button = namedtuple('ImplantType',
                                     ("shortcut", "description", "tooltip"))
    implant_chart_button.description = description
    implant_chart_button.tooltip = ""
    implant_chart_button.shortcut = shortcut
    STATIC_LIST.append(implant_chart_button)


class ImplantChoiceDialog(ExtendableDialog):

    def __init__(self, static, parent=None):
        ExtendableDialog.__init__(self, parent, remove_stretch=True)
        self.setWindowTitle(_("Implant Choice Dialog"))
        self.om_gui = parent
        self.chosen_shortcut = None

        scroll_area = QtGui.QScrollArea()
        frame = QtGui.QFrame()
        scroll_area.setWidget(frame)
        scroll_area.setWidgetResizable(True)
        self.but_layout = QtGui.QVBoxLayout(frame)
        self.insertWidget(scroll_area)

        self.apply_but.hide()
        self.more_but.hide()
        if static:
            self.add_buttons(STATIC_LIST)
        else:
            self.add_buttons(localsettings.FEETABLES.ui_implant_chart_buttons)

    def sizeHint(self):
        return QtCore.QSize(300, 300)

    def add_buttons(self, implant_chart_buttons):
        while self.but_layout.count():
            widget_item = self.but_layout.takeAt(0)
            widget_item.widget().setParent(None)

        for implant_button in implant_chart_buttons:
            but = QtGui.QPushButton(implant_button.description)
            but.setToolTip(implant_button.tooltip)
            but.clicked.connect(
                partial(self.but_clicked,
                        implant_button.shortcut))
            self.but_layout.addWidget(but)
        self.but_layout.addStretch(100)

    def but_clicked(self, shortcut):
        self.chosen_shortcut = shortcut
        self.accept()


if __name__ == "__main__":
    from gettext import gettext as _
    from openmolar.dbtools.patient_class import patient

    app = QtGui.QApplication([])
    mw = QtGui.QWidget()
    mw.pt = patient(11956)
    dl = ImplantChoiceDialog(True, mw)
    if dl.exec_():
        print dl.chosen_shortcut
    localsettings.loadFeeTables()
    dl = ImplantChoiceDialog(False, mw)
    if dl.exec_():
        print dl.chosen_shortcut
