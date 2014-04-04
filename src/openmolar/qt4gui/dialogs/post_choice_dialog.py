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

PostChartButton = namedtuple('PostChartButton',
                            ("shortcut", "description", "tooltip"))

STATIC_LIST = []
for shortcut, description in (
    ("CR,C1", _("Cast Precious Metal")),
    ("CR,C2", _("Cast Non-Precious Metal")),
    ("CR,OP", _("Other")),
):
    pcb = PostChartButton(shortcut, description, "")
    STATIC_LIST.append(pcb)


class PostChoiceDialog(ExtendableDialog):

    def __init__(self, static, parent=None):
        ExtendableDialog.__init__(self, parent, remove_stretch=True)
        self.setWindowTitle(_("Post Choice Dialog"))
        self.om_gui = parent
        self.chosen_shortcut = None

        scroll_area = QtGui.QScrollArea()
        frame = QtGui.QFrame()
        scroll_area.setWidget(frame)
        scroll_area.setWidgetResizable(True)
        self.but_layout = QtGui.QGridLayout(frame)
        self.insertWidget(scroll_area)

        self.apply_but.hide()

        if static:
            self.more_but.hide()
            self.add_buttons(STATIC_LIST)
        else:
            all_posts_but = QtGui.QPushButton(
                _("Show Post types from all feescales"))
            all_posts_but.clicked.connect(self._show_all_posts)
            self.add_advanced_widget(all_posts_but)

            self.add_buttons(
                self.om_gui.pt.fee_table.ui_lists["post_buttons"])

    def sizeHint(self):
        return QtCore.QSize(400, 500)

    def add_buttons(self, post_chart_buttons):
        while self.but_layout.count():
            widget_item = self.but_layout.takeAt(0)
            widget_item.widget().setParent(None)
        row = 0
        for row, post_button in enumerate(post_chart_buttons):
            but = QtGui.QPushButton(post_button.description)
            but.setToolTip(post_button.tooltip)
            but.clicked.connect(
                partial(self.but_clicked, post_button.shortcut))
            self.but_layout.addWidget(but, row // 2, row % 2)
        self.but_layout.setRowStretch((row + 2) // 2, 100)

    def _show_all_posts(self):
        self.add_buttons(localsettings.FEETABLES.ui_post_chart_buttons)
        self.hide_extension()

    def but_clicked(self, shortcut):
        self.chosen_shortcut = shortcut
        self.accept()

if __name__ == "__main__":
    from gettext import gettext as _
    from openmolar.dbtools.patient_class import patient

    app = QtGui.QApplication([])
    mw = QtGui.QWidget()
    mw.pt = patient(11956)
    dl = PostChoiceDialog(True, mw)
    if dl.exec_():
        print dl.chosen_shortcut
    localsettings.loadFeeTables()
    dl = PostChoiceDialog(False, mw)
    if dl.exec_():
        print dl.chosen_shortcut
