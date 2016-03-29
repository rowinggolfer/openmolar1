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

'''
this module provide 2 classes, BaseDialog and ExtendableDialog.
These are backported from openmolar2
'''

from gettext import gettext as _
import logging

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

LOGGER = logging.getLogger("openmolar")

class BaseDialog(QtWidgets.QDialog):

    '''
    A base class for all my dialogs
    provides a button box with ok and cancel buttons,
    slots connected to accept and reject
    has a VBoxlayout - accessed by self.layout_
    '''

    def __init__(self, parent=None, remove_stretch=False):
        QtWidgets.QDialog.__init__(self, parent)
        self.setWindowTitle("OpenMolar")

        self.button_box = QtWidgets.QDialogButtonBox(self)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(
            self.button_box.Cancel | self.button_box.Apply)

        self.cancel_but = self.button_box.button(self.button_box.Cancel)
        self.apply_but = self.button_box.button(self.button_box.Apply)

        self.button_box.setCenterButtons(True)

        self.layout_ = QtWidgets.QVBoxLayout(self)

        self.button_box.clicked.connect(self._clicked)

        self.check_before_reject_if_dirty = False
        self.dirty = False
        self.enableApply(False)

        if not remove_stretch:
            self.spacer = QtWidgets.QSpacerItem(
                0, 50, QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding)
            self.layout_.addItem(self.spacer)
            self.insertpoint_offset = 2
        else:
            self.spacer = None
            self.insertpoint_offset = 1
        self.layout_.addWidget(self.button_box)

    def sizeHint(self):
        '''
        Overwrite this function inherited from QWidget
        '''
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        '''
        Overwrite this function inherited from QWidget
        '''
        return QtCore.QSize(300, 300)

    def remove_spacer(self):
        '''
        If this is called, then the spacer added at init is removed.
        sometimes the spacer mucks up dialogs
        '''
        if self.spacer is not None:
            self.layout_.removeItem(self.spacer)
            self.insertpoint_offset = 1

    @property
    def abandon_message(self):
        return _("Abandon Changes?")

    def set_check_on_cancel(self, check):
        '''
        if true, then user will be asked if changes should be abandoned
        if the dialog is rejected, and given the opportunity to continue
        '''
        self.check_before_reject_if_dirty = check

    def set_accept_button_text(self, text):
        '''
        by default, the text here is "apply"...
        change as required using this function
        '''
        self.apply_but.setText(text)

    def set_reject_button_text(self, text):
        '''
        by default, the text here is "cancel"...
        change as required using this function
        '''
        self.cancel_but.setText(text)

    def insertWidget(self, widg):
        '''
        insert widget at the bottom of the layout
        '''
        count = self.layout_.count()
        insertpoint = count - self.insertpoint_offset
        self.layout_.insertWidget(insertpoint, widg)

    def _clicked(self, but):
        '''
        "private" function called when button box is clicked
        '''
        role = self.button_box.buttonRole(but)
        if role == QtWidgets.QDialogButtonBox.ApplyRole:
            self.accept()
        else:
            self.reject()

    def reject(self):
        if not (self.check_before_reject_if_dirty and self.dirty):
            QtWidgets.QDialog.reject(self)
        else:
            if QtWidgets.QMessageBox.question(self,
               _("Confirm"), self.abandon_message,
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.Yes:
                QtWidgets.QDialog.reject(self)

    def enableApply(self, enable=True):
        '''
        call this to enable the apply button (which is disabled by default)
        '''
        self.apply_but.setEnabled(enable)

    def get_confirm(self, message,
                    accept="ok", reject="cancel", default="accept"):
        '''
        a convenience function to raise a dialog for confirmation of an action
        '''
        if accept == "ok":
            accept_but = QtWidgets.QMessageBox.Ok
        elif accept == "yes":
            accept_but = QtWidgets.QMessageBox.Yes

        if reject == "cancel":
            reject_but = QtWidgets.QMessageBox.Cancel
        elif reject == "no":
            reject_but = QtWidgets.QMessageBox.No

        buttons = accept_but | reject_but
        default_but = accept_but if default == "accept" else reject_but

        return QtWidgets.QMessageBox.question(
            self,  _("Confirm"),
            message, buttons, default_but) == accept_but


class ExtendableDialog(BaseDialog):

    '''
    builds on BaseDialog, adding an area for advanced options
    unlike BaseDialog.. this dialog has no spacer item by default
    '''

    def __init__(self, parent=None, remove_stretch=False):
        BaseDialog.__init__(self, parent, remove_stretch)

        self.button_box.setCenterButtons(False)

        icon = QtGui.QIcon.fromTheme("go-down")
        #: a pointer to the Advanced button
        self.more_but = QtWidgets.QPushButton(icon, "&Advanced")
        self.more_but.setFlat(True)
        self.more_but.setCheckable(True)
        self.more_but.setFocusPolicy(QtCore.Qt.NoFocus)
        self.button_box.addButton(self.more_but, self.button_box.HelpRole)

        self.extension_frame = QtWidgets.QFrame(self)
        QtWidgets.QVBoxLayout(self.extension_frame)
        self.layout().addWidget(self.extension_frame)
        self.extension_frame.hide()

    def set_advanced_but_text(self, txt):
        self.more_but.setText(txt)

    def _clicked(self, but):
        '''
        overwrite :doc:`BaseDialog` _clicked
        checking to see if addvanced panel is to be displayed.
        '''
        if but == self.more_but:
            self.show_extension(but.isChecked())
            but.setChecked(not but.isChecked())
            return
        BaseDialog._clicked(self, but)

    def add_advanced_widget(self, widg):
        self.extension_frame.layout().addWidget(widg)

    def show_extension(self, show):
        LOGGER.debug("show extenssion, show=%s", show)
        self.more_but.setChecked(not show)
        self.extension_frame.setVisible(show)


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    dl = BaseDialog()
    QtCore.QTimer.singleShot(1000, dl.accept)
    dl.exec_()

    dl = ExtendableDialog()
    QtCore.QTimer.singleShot(1000, dl.accept)
    dl.exec_()
