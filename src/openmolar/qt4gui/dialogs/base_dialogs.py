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

'''
this module provide 2 classes, BaseDialog and ExtendableDialog.
These are backported from openmolar2
'''


from PyQt4 import QtGui, QtCore


class BaseDialog(QtGui.QDialog):

    '''
    A base class for all my dialogs
    provides a button box with ok and cancel buttons,
    slots connected to accept and reject
    has a VBoxlayout - accessed by self.layout_
    '''

    def __init__(self, parent=None, remove_stretch=False):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("OpenMolar")

        self.button_box = QtGui.QDialogButtonBox(self)
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(
            self.button_box.Cancel | self.button_box.Apply)

        self.cancel_but = self.button_box.button(self.button_box.Cancel)
        self.apply_but = self.button_box.button(self.button_box.Apply)

        self.button_box.setCenterButtons(True)

        self.layout_ = QtGui.QVBoxLayout(self)

        self.button_box.clicked.connect(self._clicked)

        self.check_before_reject_if_dirty = False
        self.dirty = False
        self.enableApply(False)

        self.spacer = QtGui.QSpacerItem(0, 100, QtGui.QSizePolicy.Expanding,
                                        QtGui.QSizePolicy.Expanding)
        self.layout_.addItem(self.spacer)
        self.layout_.addWidget(self.button_box)
        self.insertpoint_offset = 2

        if remove_stretch:
            self.remove_spacer()

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
        if role == QtGui.QDialogButtonBox.ApplyRole:
            self.accept()
        else:
            if not self.check_before_reject_if_dirty:
                self.reject()
            if (not self.dirty or QtGui.QMessageBox.question(self,
               _("Confirm"), self.abandon_message,
                QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                    QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes):
                self.reject()

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
            accept_but = QtGui.QMessageBox.Ok
        elif accept == "yes":
            accept_but = QtGui.QMessageBox.Yes

        if reject == "cancel":
            reject_but = QtGui.QMessageBox.Cancel
        elif reject == "no":
            reject_but = QtGui.QMessageBox.No

        buttons = accept_but | reject_but
        default_but = accept_but if default == "accept" else reject_but

        return QtGui.QMessageBox.question(self, _("Confirm"),
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
        self.more_but = QtGui.QPushButton(icon, "&Advanced")
        self.more_but.setFlat(True)

        self.more_but.setCheckable(True)
        self.more_but.setFocusPolicy(QtCore.Qt.NoFocus)
        self.button_box.addButton(self.more_but, self.button_box.HelpRole)

        self.setOrientation(QtCore.Qt.Vertical)

        frame = QtGui.QFrame(self)
        layout = QtGui.QVBoxLayout(frame)
        self.setExtension(frame)

    def set_advanced_but_text(self, txt):
        self.more_but.setText(txt)

    def _clicked(self, but):
        '''
        overwrite :doc:`BaseDialog` _clicked
        checking to see if addvanced panel is to be displayed.
        '''
        if but == self.more_but:
            self.showExtension(but.isChecked())
            return
        BaseDialog._clicked(self, but)

    def add_advanced_widget(self, widg):
        self.extension().layout().addWidget(widg)

    def hide_extension(self):
        self.more_but.setChecked(False)
        self.showExtension(False)

if __name__ == "__main__":
    app = QtGui.QApplication([])

    dl = BaseDialog()
    QtCore.QTimer.singleShot(1000, dl.accept)
    dl.exec_()

    dl = ExtendableDialog()
    QtCore.QTimer.singleShot(1000, dl.accept)
    dl.exec_()
