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

from functools import partial
from gettext import gettext as _
import logging

from PyQt5 import QtCore, QtWidgets
from openmolar.settings import localsettings

LOGGER = logging.getLogger("openmolar")


class control(QtWidgets.QLabel):

    '''
    a custom label for the top of the appointment overview widgets
    '''
    dayview_signal = QtCore.pyqtSignal(object)
    edit_hours_signal = QtCore.pyqtSignal(object)
    edit_memo_signal = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super(control, self).__init__(parent)
        self.setMinimumSize(80, 40)
        self.memo = ""
        self.setWordWrap(True)
        self.date = QtCore.QDate(1900, 1, 1)

        self.recent_double_click = False

    def setDate(self, arg):
        '''
        takes a QDate
        '''
        self.date = arg
        self.memo = ""
        self.updateLabels()

    def setMemo(self, arg):
        '''
        takes a string
        '''
        self.memo = arg
        self.updateLabels()

    def updateLabels(self):
        day = localsettings.readableDate(self.date.toPyDate()).replace(
            ",", "<br />")
        if self.memo != "":
            str = "<center><b>%s</b><br />%s</center>" % (day, self.memo)
        else:
            str = "<center><b>%s</b></center>" % day
        self.setText(str)

    def mouseMoveEvent(self, e):
        self.setStyleSheet("background:white")

    def leaveEvent(self, e):
        self.setStyleSheet("")

    def mousePressEvent(self, event):
        QtCore.QTimer.singleShot(
            200,
            partial(self.raise_context_menu, event.globalPos()))

    def raise_context_menu(self, point):
        if not self.recent_double_click:
            menu = QtWidgets.QMenu(self)
            action = menu.addAction(_("Switch to day view of this date"))
            action.triggered.connect(self.call_day_view)
            menu.setDefaultAction(action)
            menu.addSeparator()
            action = menu.addAction(_("Edit Memos"))
            action.triggered.connect(self.call_edit_memo)
            action = menu.addAction(_("Edit Clinician Hours"))
            action.triggered.connect(self.call_edit_hours)
            menu.exec_(point)

    def mouseDoubleClickEvent(self, event):
        LOGGER.debug("doubleclick")
        self.recent_double_click = True
        self.call_day_view()
        QtCore.QTimer.singleShot(500, self.reset_double_click)

    def reset_double_click(self):
        self.recent_double_click = False

    def call_day_view(self):
        LOGGER.debug("Call for Day View")
        self.dayview_signal.emit(self.date)

    def call_edit_hours(self):
        self.edit_hours_signal.emit(self.date)

    def call_edit_memo(self):
        self.edit_memo_signal.emit(self.date.toPyDate())


class _TestBook(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.control = control()
        self.control.setDate(QtCore.QDate.currentDate().addDays(3))
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.control)
        layout.addWidget(QtWidgets.QTextEdit())

    def sizeHint(self):
        return QtCore.QSize(100, 400)


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)

    app = QtWidgets.QApplication([])
    widg = _TestBook()
    widg.show()
    app.exec_()
