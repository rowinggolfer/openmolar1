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
import re
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar.qt4gui.customwidgets.upper_case_line_edit import \
    UpperCaseLineEdit
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog
from openmolar.qt4gui.customwidgets.simple_chartwidget import SimpleChartWidg

LOGGER = logging.getLogger("openmolar")

VALID_INPUTS = (
    "SR_F$",
    "SR_P/(R[1-8]{1,8},)?(L[1-8]{1,8})?$",
    "CC_F$",
    "CC_P/(R[1-8]{1,8},)?(L[1-8]{1,8})?$",
    "FL_F$",
    "FL_P/(R[1-8]{1,8},)?(L[1-8]{1,8})?$",
    "SL",
    "ST",
    "",  # this one in case of no input whatsoever!
)


class _OptionPage(QtWidgets.QWidget):
    finished_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.dialog = parent
        self.label = QtWidgets.QLabel(_("Choose from the following options"))
        self.label.setWordWrap(True)
        self.frame = QtWidgets.QFrame()

        layout = QtWidgets.QVBoxLayout(self)
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


class PageTwo(_OptionPage):

    def __init__(self, parent=None):
        _OptionPage.__init__(self, parent)
        layout = QtWidgets.QVBoxLayout(self.frame)
        self.full_radioButton = QtWidgets.QRadioButton(
            _("Complete Denture"))
        self.partial_radioButton = QtWidgets.QRadioButton(
            _("Partial Denture"))

        layout.addWidget(self.full_radioButton)
        layout.addWidget(self.partial_radioButton)

    @property
    def is_completed(self):
        '''
        simply check user has checked a box
        '''
        for widg in (self.full_radioButton, self.partial_radioButton):
            if widg.isChecked():
                return True
        return False

    @property
    def next_index(self):
        if self.partial_radioButton.isChecked():
            return 1
        # skip the teeth choosing page if a complete denture
        return 2

    @property
    def return_text(self):
        if self.full_radioButton.isChecked():
            return "F"
        return "P/"


class PageZero(_OptionPage):

    def __init__(self, parent=None):
        _OptionPage.__init__(self, parent)
        self._is_completed = False
        self._chosen_arch = "upper"
        self._return_text = ""

        upper_but = QtWidgets.QPushButton(_("New UPPER Denture"))
        upper_but.setMinimumSize(QtCore.QSize(150, 150))
        lower_but = QtWidgets.QPushButton(_("New LOWER Denture"))
        lower_but.setMinimumSize(QtCore.QSize(150, 150))
        full_fulls_but = QtWidgets.QPushButton(
            _("Complete Upper AND Lower Acrylic Dentures"))
        full_fulls_but.setMinimumSize(QtCore.QSize(150, 150))

        layout = QtWidgets.QGridLayout(self.frame)
        layout.addWidget(upper_but, 0, 0)
        layout.addWidget(lower_but, 0, 1)
        layout.addWidget(full_fulls_but, 1, 0, 1, 2)

        upper_but.clicked.connect(self._finished)
        lower_but.clicked.connect(self._lower)
        full_fulls_but.clicked.connect(self._full_fulls)

    @property
    def is_completed(self):
        return self._is_completed

    @property
    def return_text(self):
        return self._return_text

    @property
    def chosen_arch(self):
        return self._chosen_arch

    def _finished(self):
        self._is_completed = True
        self.finished_signal.emit()

    def _lower(self):
        self._chosen_arch = "lower"
        self._finished()

    @property
    def next_index(self):
        if self._return_text == "SR_F/F":
            return 4
        return 1

    def _full_fulls(self):
        self._return_text = "SR_F/F"
        self._finished()


class PageOne(_OptionPage):

    def __init__(self, parent=None):
        _OptionPage.__init__(self, parent)
        self.acrylic_radioButton = QtWidgets.QRadioButton(_("Acrylic Denture"))
        self.metal_radioButton = QtWidgets.QRadioButton(_("Chrome Denture"))
        self.flexible_radioButton = QtWidgets.QRadioButton(_("Flexible Denture"))

        layout = QtWidgets.QVBoxLayout(self.frame)
        layout.addWidget(self.acrylic_radioButton)
        layout.addWidget(self.metal_radioButton)
        layout.addWidget(self.flexible_radioButton)

    @property
    def is_completed(self):
        return (self.acrylic_radioButton.isChecked() or
                self.metal_radioButton.isChecked() or
                self.flexible_radioButton.isChecked())

    @property
    def return_text(self):
        if self.acrylic_radioButton.isChecked():
            return "SR_"
        if self.metal_radioButton.isChecked():
            return "CC_"
        if self.flexible_radioButton.isChecked():
            return "FL_"


class PageThree(_OptionPage):

    def __init__(self, parent=None):
        _OptionPage.__init__(self, parent)
        self.dl = parent
        self.label.setText(
            _("Please select teeth which this denture is to replace"))
        self.chartwidg = SimpleChartWidg(self, auto_ctrl_key=True)
        layout = QtWidgets.QVBoxLayout(self.frame)
        layout.addWidget(self.chartwidg)

    def showEvent(self, event=None):
        if self.dl.is_upper_input:
            LOGGER.debug("hiding lower teeth")
            self.chartwidg.disable_lowers()
        else:
            LOGGER.debug("hiding upper teeth")
            self.chartwidg.disable_uppers()

    @property
    def return_text(self):
        r_teeth, l_teeth = set([]), set([])
        for tooth in self.chartwidg.getSelected():
            m = re.match("[ul]([lr])(\d)", tooth)
            if m:
                if m.groups()[0] == "r":
                    r_teeth.add(m.groups()[1])
                else:
                    l_teeth.add(m.groups()[1])
        retval = ""
        if r_teeth:
            retval += "R"
            for tooth in sorted(r_teeth, reverse=True):
                retval += tooth
        if l_teeth:
            if retval != "":
                retval += ","
            retval += "L"
            for tooth in sorted(l_teeth):
                retval += tooth
        return retval


class PageFour(_OptionPage):

    def __init__(self, parent=None):
        _OptionPage.__init__(self, parent)
        self.label.setText(
            _("You may wish to add the following optional items"))

        self.st_checkBox = QtWidgets.QCheckBox(_("Special Tray"))
        self.sl_checkBox = QtWidgets.QCheckBox(_("Soft Lining"))

        layout = QtWidgets.QVBoxLayout(self.frame)
        layout.addWidget(self.st_checkBox)
        layout.addWidget(self.sl_checkBox)

    @property
    def _additional_text(self):
        text_ = ""
        if self.st_checkBox.isChecked():
            text_ += " ST"
        if self.sl_checkBox.isChecked():
            text_ += " SL"
        return text_

    @property
    def return_text(self):
        if self.dialog.default_lineedit.text() != "":
            return self._additional_text
        return ""


class AcceptPage(_OptionPage):

    def __init__(self, parent=None):
        _OptionPage.__init__(self, parent)
        self.label.setText("%s<hr />%s" % (
                           _("You have completed your input."),
                           _("Please click on Apply")))
        self.frame.hide()


class NewDentureDialog(ExtendableDialog):

    def __init__(self, om_gui=None):
        ExtendableDialog.__init__(self, om_gui)

        self.om_gui = om_gui
        message = (_("Add A New Denture To The Treatment Plan"))
        self.setWindowTitle(message)
        self.header_label = QtWidgets.QLabel(message)
        self.header_label.setAlignment(QtCore.Qt.AlignCenter)

        self.ndu_le = UpperCaseLineEdit()
        self.ndl_le = UpperCaseLineEdit()

        self.set_default_lineedit(self.ndl_le)

        self.wizard_widget = QtWidgets.QStackedWidget()

        page0 = PageZero(self)
        page0.finished_signal.connect(self.next_widget)
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

        frame = QtWidgets.QFrame()
        layout = QtWidgets.QFormLayout(frame)
        layout.addRow(_("Upper Denture"), self.ndu_le)
        layout.addRow(_("Lower Denture"), self.ndl_le)

        self.add_advanced_widget(frame)

        self.next_but = self.button_box.addButton(
            _("Next"), self.button_box.ActionRole)

        self.apply_but.hide()

        self.ndu_le.textChanged.connect(self.enable_apply)
        self.ndl_le.textChanged.connect(self.enable_apply)

        self.ndu_le.editingFinished.connect(self.advanced_apply)
        self.ndl_le.editingFinished.connect(self.advanced_apply)

    @property
    def current_index(self):
        return self.wizard_widget.currentIndex()

    @property
    def current_page(self):
        return self.wizard_widget.widget(self.current_index)

    def next_widget(self):
        if not self.current_page.is_completed:
            QtWidgets.QMessageBox.information(self, _("Whoops"),
                                          self.current_page.error_message)
            return

        if self.current_index == 0:
            self.set_default_lineedit(self.current_page.chosen_arch)

        le = self.default_lineedit
        le.setText(le.text() + self.current_page.return_text)

        self.current_page.cleanup()

        if self.current_index == 4:
            if "F/F" in self.upper_input:
                le = self.ndl_le
                le.setText(le.text() + self.current_page.return_text)

        index_ = self.current_index + self.current_page.next_index
        if index_ >= self.wizard_widget.count() - 1:
            self.apply_but.show()
            self.next_but.hide()

        self.wizard_widget.setCurrentIndex(index_)

    @property
    def is_upper_input(self):
        return self.default_lineedit == self.ndu_le

    @property
    def default_lineedit(self):
        return self._default_lineedit

    def set_default_lineedit(self, value="upper"):
        if value == "upper":
            self._default_lineedit = self.ndu_le
        else:
            self._default_lineedit = self.ndl_le

    def _clicked(self, but):
        '''
        "private" function called when button box is clicked
        '''
        role = self.button_box.buttonRole(but)
        if role == self.button_box.ActionRole:
            self.next_widget()
        else:
            ExtendableDialog._clicked(self, but)

    @property
    def check_valid_input(self):
        ndus, ndls = self.upper_input, self.lower_input
        for ndu in ndus.split(" "):
            matched = False
            for input_ in VALID_INPUTS:
                if re.match(input_, ndu):
                    matched = True
            if not matched:
                QtWidgets.QMessageBox.warning(
                    self,
                    _("Warning"),
                    _("Your upper denture input is invalid"))
                return False
        for ndl in ndls.split(" "):
            LOGGER.debug("checking '%s'" % ndl)
            matched = False
            for input_ in VALID_INPUTS:
                if re.match(input_, ndl):
                    matched = True
            if not matched:
                QtWidgets.QMessageBox.warning(
                    self,
                    ("Warning"),
                    _("Your lower denture input is invalid"))
                return False
        return True

    def enable_apply(self, *args):
        self.enableApply(self.upper_input != "" or self.lower_input != "")

    def advanced_apply(self, *args):
        self.apply_but.show()
        self.enableApply(self.upper_input != "" or self.lower_input != "")

    @property
    def upper_input(self):
        return str(self.ndu_le.text()).strip(" ")

    @property
    def lower_input(self):
        return str(self.ndl_le.text()).strip(" ")

    @property
    def chosen_treatments(self):
        for input_ in self.upper_input.split(" "):
            if input_ != "":
                yield ("ndu", input_)
        for input_ in self.lower_input.split(" "):
            if input_ != "":
                yield ("ndl", input_)

    def exec_(self):
        result = ExtendableDialog.exec_(self)
        if result:
            result = self.check_valid_input or self.exec_()
        return result


if __name__ == "__main__":

    app = QtWidgets.QApplication([])
    LOGGER.setLevel(logging.DEBUG)
    dl = NewDentureDialog(None)
    if dl.exec_():
        for att, tx in dl.chosen_treatments:
            print(att, tx)
