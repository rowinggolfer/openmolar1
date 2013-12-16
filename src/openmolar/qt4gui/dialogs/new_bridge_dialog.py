#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011-2012,  Neil Wallace <neil@openmolar.com>                  ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

import logging
import re
from PyQt4 import QtGui, QtCore

from openmolar.qt4gui.customwidgets.upper_case_line_edit import \
UpperCaseLineEdit
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog
from openmolar.qt4gui.customwidgets.simple_chartwidget import SimpleChartWidg

LOGGER = logging.getLogger("openmolar")

RETAINER_LIST = [
("GO", _("Gold")),
("V1", _("Bonded Porcelain")),
("LAVA", _("Lava")),
("OPAL", _("Opalite")),
("EMAX", _("Emax")),
("EVER", _("Everest")),
("SR", _("Resin")),
("OT", _("Other")),
]

PONTIC_LIST = RETAINER_LIST

class _OptionPage(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.dialog = parent
        self.label = QtGui.QLabel(_("Choose from the following options"))
        self.label.setWordWrap(True)
        self.frame = QtGui.QFrame()

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.frame)
        layout.addStretch(100)

    def sizeHint(self):
        return QtCore.QSize(400, 400)

    @property
    def is_completed(self):
        '''
        should be overwritten!
        '''
        return True

    @property
    def error_message(self):
        '''
        should be overwritten!
        '''
        return _("You haven't completed this option")

    @property
    def return_text(self):
        return ""

    @property
    def next_index(self):
        return 1

    def cleanup(self):
        pass

class PageZero(_OptionPage):
    def __init__(self, parent=None):
        _OptionPage.__init__(self, parent)
        self.upper_radioButton = QtGui.QRadioButton(_("Upper Bridge"))
        self.lower_radioButton = QtGui.QRadioButton(_("Lower Bridge"))

        layout = QtGui.QVBoxLayout(self.frame)
        layout.addWidget(self.upper_radioButton)
        layout.addWidget(self.lower_radioButton)

    @property
    def is_completed(self):
        return (self.upper_radioButton.isChecked() or
            self.lower_radioButton.isChecked())

    @property
    def properties(self):
        if self.upper_radioButton.isChecked():
            return (("arch", "upper"),)
        return (("arch", "lower"),)

class PageOne(_OptionPage):
    def __init__(self, parent=None):
        _OptionPage.__init__(self, parent)
        self.label.setText(_("Bridge Type"))
        self.radioButton1 = QtGui.QRadioButton(_("Conventional Bridge"))
        self.radioButton2 = QtGui.QRadioButton(_("Resin Retained Bridge"))

        layout = QtGui.QVBoxLayout(self.frame)
        layout.addWidget(self.radioButton1)
        layout.addWidget(self.radioButton2)

    @property
    def is_completed(self):
        return (self.radioButton1.isChecked() or
            self.radioButton2.isChecked())

    @property
    def properties(self):
        if self.radioButton2.isChecked():
            return (("type", "conventional"),)
        return (("type", "resin_retained"),)

class PageTwo(_OptionPage):
    def __init__(self, parent=None):
        _OptionPage.__init__(self, parent)
        self.label.setText(_("Material"))
        self.radio_buttons = {}
        layout = QtGui.QGridLayout(self.frame)
        i = 0
        for shortcut, description in RETAINER_LIST:
            if self.radio_buttons.has_key(shortcut):
                LOGGER.warning("duplication in BRIDGE MATERIAL LIST")
                continue
            rad_but = QtGui.QRadioButton(description)
            layout.addWidget(rad_but, i//2, i%2)
            self.radio_buttons[shortcut] = rad_but
            i += 1

    @property
    def is_completed(self):
        for rad_but in self.radio_buttons.values():
            if rad_but.isChecked():
                return True
        return False

    @property
    def properties(self):
        for shortcut, rad_but in self.radio_buttons.iteritems():
            if rad_but.isChecked():
                return (("material", shortcut),)

class PageThree(_OptionPage):
    def __init__(self, parent=None):
        _OptionPage.__init__(self, parent)
        self.dl = parent
        self.label.setText(_(
        "Please select teeth which are to be used as retainers"))
        self.chartwidg = SimpleChartWidg(self)
        layout = QtGui.QVBoxLayout(self.frame)
        layout.addWidget(self.chartwidg)

    def showEvent(self, event=None):
        if self.dl.is_upper_input:
            self.chartwidg.disable_lowers()
        else:
            self.chartwidg.disable_uppers()

    @property
    def completed(self):
        return list(self.properties) != []

    @property
    def properties(self):
        for tooth in  self.chartwidg.getSelected():
            yield(tooth, "retainer")

class PageFour(_OptionPage):
    def __init__(self, parent=None):
        _OptionPage.__init__(self, parent)
        self.dl = parent
        self.label.setText(_(
        "Please select teeth which are to be used as pontics"))
        self.chartwidg = SimpleChartWidg(self)
        layout = QtGui.QVBoxLayout(self.frame)
        layout.addWidget(self.chartwidg)

    def showEvent(self, event=None):
        if self.dl.is_upper_input:
            self.chartwidg.disable_lowers()
        else:
            self.chartwidg.disable_uppers()

    @property
    def completed(self):
        return list(self.properties) != []

    @property
    def properties(self):
        for tooth in  self.chartwidg.getSelected():
            yield(tooth, "pontic")

class AcceptPage(_OptionPage):
    def __init__(self, parent=None):
        _OptionPage.__init__(self, parent)
        self.label.setText("%s<hr />%s"% (
        _("You have completed your input."),
        _("Please click on Apply")))
        self.frame.hide()

class NewBridgeDialog(ExtendableDialog):
    chosen_properties = {}
    def __init__(self, om_gui = None):
        ExtendableDialog.__init__(self, om_gui)

        self.om_gui = om_gui
        message = (_("Chart/Plan a Bridge"))
        self.setWindowTitle(message)
        self.header_label = QtGui.QLabel(message)
        self.header_label.setAlignment(QtCore.Qt.AlignCenter)

        self.wizard_widget = QtGui.QStackedWidget()

        page0 = PageZero(self)
        page1 = PageOne(self)
        page2 = PageTwo(self)
        page3 = PageThree(self)
        page4 = PageFour(self)
        accept_page = AcceptPage(self)

        self.wizard_widget.addWidget(page0)
        self.wizard_widget.addWidget(page1)
        self.wizard_widget.addWidget(page2)
        self.wizard_widget.addWidget(page3)
        self.wizard_widget.addWidget(page4)
        self.wizard_widget.addWidget(accept_page)

        self.insertWidget(self.header_label)
        self.insertWidget(self.wizard_widget)

        self.advanced_label = QtGui.QLabel("self.advanced_label")
        self.add_advanced_widget(self.advanced_label)

        self.next_but = self.button_box.addButton(
            _("Next"), self.button_box.ActionRole)

        self.apply_but.hide()

    @property
    def is_upper_input(self):
        return self.chosen_properties.get("arch") == "upper"

    @property
    def current_index(self):
        return self.wizard_widget.currentIndex()

    @property
    def current_page(self):
        return self.wizard_widget.widget(self.current_index)

    def next_widget(self):
        if not self.current_page.is_completed:
            QtGui.QMessageBox.information(self, _("Whoops"),
            self.current_page.error_message)
            return

        for key, value in self.current_page.properties:
            self.chosen_properties[key] = value
        self.current_page.cleanup()

        index_ = self.current_index + self.current_page.next_index
        if index_ >= self.wizard_widget.count() - 1:
            self.apply_but.show()
            self.enableApply()
            self.next_but.hide()

        self.wizard_widget.setCurrentIndex(index_)

    def _clicked(self, but):
        '''
        "private" function called when button box is clicked
        '''
        role = self.button_box.buttonRole(but)
        if role == self.button_box.ActionRole:
            self.next_widget()
        else:
            ExtendableDialog._clicked(self, but)


if __name__ == "__main__":

    app = QtGui.QApplication([])
    LOGGER.setLevel(logging.DEBUG)
    dl = NewBridgeDialog(None)
    if dl.exec_():
        print dl.chosen_properties