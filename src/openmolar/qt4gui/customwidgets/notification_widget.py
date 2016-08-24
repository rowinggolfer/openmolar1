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
from PyQt5 import QtGui
from PyQt5 import QtWidgets

STYLE = 'color:red; background:yellow; font-weight:bold;'

class NotificationWidget(QtWidgets.QWidget):

    def __init__(self, message, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setStyleSheet(STYLE)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.t_label = QtWidgets.QLabel(
            QtCore.QTime.currentTime().toString("HH:mm"))
        self.t_label.setAlignment(QtCore.Qt.AlignCenter)

        self.label = QtWidgets.QLabel(message)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.layout.addWidget(self.t_label)
        self.layout.addWidget(self.label)


class notificationWidget(QtWidgets.QTabWidget):

    '''
    a custom widget which contains children which come and go
    '''

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(100)
        self.tabBar().tabBarClicked.connect(self.removeMessage)
        self.hide()

    def addMessage(self, message):
        '''
        pass a message
        '''
        widg = NotificationWidget(message, self)
        self.addTab(widg, "x")
        self.show()
        self.enable_buts()

    def enable_buts(self):
        n_tabs = self.count()-1
        for i in range(n_tabs):
            self.tabBar().setTabEnabled(i, False)
        self.tabBar().setTabEnabled(n_tabs, True)
        self.setCurrentIndex(n_tabs)

    def removeMessage(self):
        '''
        user has "acknowledged a message
        '''
        widg = self.currentWidget()
        self.removeTab(self.indexOf(widg))
        widg.deleteLater()
        if self.count() == 0:
            self.hide()
        else:
            self.enable_buts()


if __name__ == "__main__":
    from functools import partial

    app = QtWidgets.QApplication([])
    form = QtWidgets.QMainWindow()
    form.setMinimumWidth(300)

    nw = notificationWidget(form)

    for i in range(5):
        QtCore.QTimer.singleShot(
            i * 3000,
            partial(nw.addMessage, "This is test message %d" % (i + 1)))

    form.setCentralWidget(nw)
    form.show()

    app.exec_()
