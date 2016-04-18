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
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from openmolar.dbtools.feescales import FeescaleConfigurer
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

LOGGER = logging.getLogger("openmolar")


class FeescaleWidget(QtWidgets.QWidget):
    '''
    a widget to allow user interaction for the FeescaleConfigDialog
    '''

    promote_signal = QtCore.pyqtSignal()
    demote_signal = QtCore.pyqtSignal()
    check_required_signal = QtCore.pyqtSignal()

    def __init__(self, feescale, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.feescale = feescale

        self.label = QtWidgets.QLabel("")

        self.in_use_checkbox = QtWidgets.QCheckBox(_("In use"))
        self.in_use_checkbox.setChecked(feescale.in_use)

        self.comment_line_edit = QtWidgets.QLineEdit()
        message = feescale.comment if feescale.comment else feescale.name
        self.comment_line_edit.setText(message)

        p_map = QtGui.QPixmap(QtGui.QPixmap(":/down.png"))
        self.down_button = QtWidgets.QPushButton(QtGui.QIcon(p_map), "")
        self.down_button.setToolTip(_("Demote the feescale"))

        p_map = QtGui.QPixmap(QtGui.QPixmap(":/up.png"))
        self.up_button = QtWidgets.QPushButton(QtGui.QIcon(p_map), "")
        self.up_button.setToolTip(_("Promote the feescale"))

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        layout.addWidget(self.in_use_checkbox)
        layout.addWidget(self.comment_line_edit)
        layout.addWidget(self.down_button)
        layout.addWidget(self.up_button)

        self.down_button.clicked.connect(self.demote_signal.emit)
        self.up_button.clicked.connect(self.promote_signal.emit)
        self.comment_line_edit.textEdited.connect(
            self.check_required_signal.emit)
        self.in_use_checkbox.stateChanged.connect(
            self.check_required_signal.emit)

    def enable(self):
        self.down_button.setEnabled(True)
        self.up_button.setEnabled(True)

    @property
    def in_use(self):
        return self.in_use_checkbox.isChecked()

    @property
    def comment(self):
        return self.comment_line_edit.text()

    @property
    def is_dirty(self):
        return (self.in_use != self.feescale.in_use or
                self.comment != self.feescale.comment)

    def disable_demote(self):
        self.down_button.setEnabled(False)

    def disable_promote(self):
        self.up_button.setEnabled(False)


class FeescaleConfigDialog(BaseDialog):
    '''
    This dialog allows the user to alter comments about a feescale,
    and make changes to the priorites they are loaded into openmolar.
    '''

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent, remove_stretch=True)

        title = _("Confgure Feescales Dialog")
        self.setWindowTitle(title)
        label = WarningLabel(
            "%s<hr />%s" % (
                _("This dialog enables you to modify the metadata which "
                  "determines the order feescales are loaded."),
                _("You can also archive a feescale by unchecking 'in use'.")))
        self.insertWidget(label)
        self.configurer = FeescaleConfigurer()
        LOGGER.debug("Feescales to config\n%s", "\n".join(
            ["  %s" % f for f in self.configurer.feescales]))

        frame = QtWidgets.QFrame()
        self.fs_layout = QtWidgets.QVBoxLayout(frame)
        self.fs_layout.setContentsMargins(0, 0, 0, 0)
        self.fs_layout.setSpacing(0)
        for feescale in self.configurer.feescales:
            widg = FeescaleWidget(feescale)
            widg.promote_signal.connect(self.promote_widget)
            widg.demote_signal.connect(self.demote_widget)
            widg.check_required_signal.connect(self.check_enable)
            self.fs_layout.addWidget(widg)

        scroll_area = QtWidgets.QScrollArea(self)
        scroll_area.setWidget(frame)
        scroll_area.setWidgetResizable(True)
        self.insertWidget(scroll_area)

        self.enable_buttons()

    def sizeHint(self):
        return QtCore.QSize(600, 600)

    @property
    def fs_widgets(self):
        for i in range(self.fs_layout.count()):
            widg = self.fs_layout.itemAt(i).widget()
            if type(widg) == FeescaleWidget:
                yield widg

    @property
    def n_active_feescales(self):
        i = 0
        for widg in self.fs_widgets:
            if widg.in_use:
                i += 1
        return i

    def enable_buttons(self):
        for i, widg in enumerate(self.fs_widgets):
            widg.label.setText("%02d" % (i + 1))
            widg.enable()
        w_list = list(self.fs_widgets)
        w_list[0].disable_promote()
        w_list[-1].disable_demote()
        self.check_enable()

    def check_enable(self):
        self.enableApply(self.is_dirty)

    def promote_widget(self):
        widg = self.sender()
        LOGGER.debug("promote %s", widg.feescale)
        index = self.fs_layout.indexOf(widg)
        if index == 0:  # already highest in the list!
            return
        self.fs_layout.removeWidget(widg)
        self.fs_layout.insertWidget(index-1, widg)
        self.enable_buttons()

    def demote_widget(self):
        widg = self.sender()
        LOGGER.debug("demote %s", widg.feescale)
        index = self.fs_layout.indexOf(widg)
        if index == len(self.configurer.feescales):  # already bottom of list
            return
        self.fs_layout.removeWidget(widg)
        self.fs_layout.insertWidget(index+1, widg)
        self.enable_buttons()

    @property
    def is_dirty(self):
        for i, widg in enumerate(self.fs_widgets):
            if widg.is_dirty:
                return True
            if widg.feescale != self.configurer.feescales[i]:
                return True
        return False

    def _apply(self):
        for priority, widg in enumerate(self.fs_widgets):
            self.configurer.apply_changes(widg.feescale.ix,
                                          widg.in_use,
                                          widg.comment,
                                          priority + 1)

    def exec_(self):
        if BaseDialog.exec_(self):
            self._apply()
            return True
        return False
