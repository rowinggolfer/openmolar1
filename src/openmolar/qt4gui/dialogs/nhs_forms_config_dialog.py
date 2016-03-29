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

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar.settings import localsettings
from openmolar.connect import connect
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

from openmolar.qt4gui.printing.gp17.gp17_config import gp17config


class _PrintSettings(QtWidgets.QWidget):
    user_input = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.left_sb = QtWidgets.QSpinBox()
        self.top_sb = QtWidgets.QSpinBox()
        self.scale_x_sb = QtWidgets.QDoubleSpinBox()
        self.scale_y_sb = QtWidgets.QDoubleSpinBox()
        form_layout = QtWidgets.QFormLayout(self)

        form_layout.addRow(_("Left Offset"), self.left_sb)
        form_layout.addRow(_("Top Offset"), self.top_sb)
        form_layout.addRow(_("Horizontal Scaling"), self.scale_x_sb)
        form_layout.addRow(_("Vertical Scaling"), self.scale_y_sb)

    def set_initial_values(self, left, top, scale_x, scale_y):
        self.left_sb.setValue(left)
        self.top_sb.setValue(top)
        self.scale_x_sb.setValue(scale_x)
        self.scale_y_sb.setValue(scale_y)

        for widg in (self.left_sb, self.top_sb,
                     self.scale_x_sb, self.scale_y_sb):
            widg.valueChanged.connect(self.emit_user_input)

    def value(self, attribute):
        if attribute == "left":
            return str(self.left_sb.value())
        elif attribute == "top":
            return str(self.top_sb.value())
        elif attribute == "scale_x":
            return str(self.scale_x_sb.value())
        elif attribute == "scale_y":
            return str(self.scale_y_sb.value())

    def emit_user_input(self, *args):
        self.user_input.emit()


class NHSFormsConfigDialog(BaseDialog):

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)

        title = _("NHS Form Configuration")
        self.setWindowTitle(title)
        label = QtWidgets.QLabel("<b>%s</b>" % title)
        label.setAlignment(QtCore.Qt.AlignCenter)

        self.gp17_widget = _PrintSettings()
        self.gp17_widget.set_initial_values(
            gp17config.OFFSET_LEFT,
            gp17config.OFFSET_TOP,
            gp17config.SCALE_X,
            gp17config.SCALE_Y)

        self.gp17ifront_widget = _PrintSettings()
        self.gp17ifront_widget.set_initial_values(
            gp17config.GP17i_OFFSET_LEFT,
            gp17config.GP17i_OFFSET_TOP,
            gp17config.GP17i_SCALE_X,
            gp17config.GP17i_SCALE_Y)

        self.gp17iback_widget = _PrintSettings()
        self.gp17iback_widget.set_initial_values(
            gp17config.GP17iback_OFFSET_LEFT,
            gp17config.GP17iback_OFFSET_TOP,
            gp17config.GP17iback_SCALE_X,
            gp17config.GP17iback_SCALE_Y)

        self.gp17_widget.user_input.connect(self.enableApply)
        self.gp17ifront_widget.user_input.connect(self.enableApply)
        self.gp17iback_widget.user_input.connect(self.enableApply)

        tab_widget = QtWidgets.QTabWidget()
        tab_widget.addTab(self.gp17_widget, "GP17")
        tab_widget.addTab(self.gp17ifront_widget, "GP17i (front)")
        tab_widget.addTab(self.gp17iback_widget, "GP17i (back)")

        self.insertWidget(label)
        self.insertWidget(tab_widget)

    def apply(self):
        for widg, section in (
            (self.gp17_widget, "gp17Front"),
            (self.gp17ifront_widget, "gp17iFront"),
            (self.gp17iback_widget, "gp17iBack")
        ):
            for option in ("top", "left", "scale_x", "scale_y"):
                gp17config.set(section, option, widg.value(option))

        gp17config.save_config()
        gp17config.read_conf()

    def sizeHint(self):
        return QtCore.QSize(300, 350)

    def exec_(self):
        if BaseDialog.exec_(self):
            self.apply()
            return True
        return False


if __name__ == "__main__":

    localsettings.initiate()
    app = QtWidgets.QApplication([])

    dl = NHSFormsConfigDialog()

    print((dl.exec_()))
