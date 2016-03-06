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

from PyQt4 import QtGui, QtCore


class notificationGB(QtGui.QWidget):

    '''
    a customised groupBox
    '''
    acknowledged = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.counter = None

        self.layout = QtGui.QGridLayout(self)
        self.layout.setMargin(0)

        self.t_label = QtGui.QLabel()
        self.t_label.setAlignment(QtCore.Qt.AlignCenter)

        self.label = QtGui.QLabel()
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("color: red")
        # self.label.setWordWrap(True)

        icon = QtGui.QIcon.fromTheme(
            "window-close", QtGui.QIcon(":/quit.png"))
        self.but = QtGui.QPushButton(icon, "")
        self.but.setMaximumWidth(40)

        self.line = QtGui.QFrame()
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)

        self.layout.addWidget(self.t_label, 0, 0)
        self.layout.addWidget(self.label, 1, 0)
        self.layout.addWidget(self.but, 0, 1, 2, 1)
        self.layout.addWidget(self.line, 2, 0, 1, 2)

        self.line.hide()

        self.but.clicked.connect(self.send_acknowledged_signal)

    def setId(self, arg):
        '''
        give the widget a unique ID
        '''
        self.counter = arg

    def setMessage(self, message):
        '''
        set the label's text
        '''
        t = QtCore.QTime.currentTime()
        self.t_label.setText("<b>%s:%02d</b>" % (t.hour(), t.minute()))
        self.label.setText(message)

    def set_minimised(self, bool_):
        for widg in (self.but, self.t_label, self.label):
            widg.setVisible(not bool_)
        self.line.setVisible(bool_)

    def send_acknowledged_signal(self):
        '''
        the "acknowledge" check box has been toggled
        '''
        self.acknowledged.emit()


class notificationWidget(QtGui.QWidget):

    '''
    a custom widget which contains children which come and go
    '''

    def __init__(self, parent=None):
        super(notificationWidget, self).__init__(parent)
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.setMargin(0)
        self.widgets = []

    def addMessage(self, message):
        '''
        pass a message
        '''
        for widg in self.widgets:
            widg.set_minimised(True)

        widg = notificationGB(self)
        widg.setMessage(message)
        self.widgets.append(widg)

        self.layout.insertWidget(0, widg)

        widg.acknowledged.connect(self.removeMessage)
        self.show()

    def removeMessage(self):
        '''
        user has "acknowledged a message
        '''
        widg = self.sender()
        widg.hide()
        self.widgets.remove(widg)
        widg.deleteLater()

        if len(self.widgets) > 0:
            self.widgets[-1].set_minimised(False)
        else:
            self.hide()


if __name__ == "__main__":

    from openmolar.settings import localsettings
    from functools import partial

    def test(arg=None):
        print("clicked = ", arg)

    app = QtGui.QApplication([])
    form = QtGui.QMainWindow()
    form.setMinimumWidth(300)

    nw = notificationWidget(form)
    QtCore.QObject.connect(nw, QtCore.SIGNAL("clicked()"), test)

    for i in range(5):
        QtCore.QTimer.singleShot(i * 3000,
                                 partial(
                                 nw.addMessage, "This is test message %d" %
                                 (i + 1))
                                 )

    form.setCentralWidget(nw)
    form.show()

    app.exec_()
