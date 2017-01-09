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

LOGGER = logging.getLogger("openmolar")

STYLE = 'color:red; background:yellow; font-weight:bold;'

class NotificationLabel(QtWidgets.QWidget):

    def __init__(self, message, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.message = message
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


class NotificationWidget(QtWidgets.QTabWidget):

    '''
    a custom widget which contains children which come and go
    '''

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaximumHeight(100)
        self.tabBar().tabBarClicked.connect(self.removeMessage)
        self.hide()

    def remove_forum_messages(self, user):
        LOGGER.debug("remove_forum_messages %s", user)
        n_tabs = self.count()
        try:
            for i in range(n_tabs):
                widg = self.widget(i)
                if re.match("%s %s" % (user, _("has unread posts")),
                            widg.message):
                    self.removeTab(i)
                    widg.deleteLater()
        except AttributeError:  # currentWidget may be None
            LOGGER.info("ignoring remove message")
        if self.count() == 0:
            self.hide()

    def addMessage(self, message):
        '''
        pass a message
        '''
        LOGGER.debug("addMessage %s", message)
        m = re.match("(.*) %s" % _("has unread posts"), message)
        if m:
            self.remove_forum_messages(m.groups()[0])

        n_tabs = self.count()-1
        for i in range(n_tabs):
            try:
                if message == self.widget(i).message:
                    self.tabBar().moveTab(i, n_tabs)
                    break
            except AttributeError:  # currentWidget may be None
                pass
        self.enable_buts()
        try:
            if message == self.currentWidget().message:
                return
        except AttributeError:  # currentWidget may be None
            pass
        widg = NotificationLabel(message, self)
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
    from gettext import gettext as _
    LOGGER.setLevel(logging.DEBUG)

    app = QtWidgets.QApplication([])
    form = QtWidgets.QMainWindow()
    form.setMinimumWidth(300)

    nw = NotificationWidget(form)

    for i, n in enumerate([1, 2, 3, 3, 3, 1, 1, 5]):
        QtCore.QTimer.singleShot(
            i * 2500,
            partial(nw.addMessage, "NW has unread posts (%d)" % n))

    form.setCentralWidget(nw)
    form.show()

    app.exec_()
