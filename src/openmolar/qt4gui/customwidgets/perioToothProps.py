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

from PyQt4 import QtGui, QtCore
from openmolar.qt4gui.compiled_uis import Ui_toothPerioProps
from openmolar.qt4gui import colours
from openmolar.settings import allowed


class tpWidget(Ui_toothPerioProps.Ui_Form, QtGui.QWidget):

    def __init__(self, parent=None):
        super(tpWidget, self).__init__(parent)
        self.setupUi(self)
        hlayout = QtGui.QHBoxLayout(self.le_frame)
        hlayout.setContentsMargins(0, 0, 0, 0)
        self.lineEdit = chartLineEdit()
        self.lineEdit.setMaxLength(2)
        hlayout.addWidget(self.lineEdit)
        self.oldtooth = tooth()  # self.frame)
        self.oldtooth.setEnabled(False)
        toothlayout = QtGui.QHBoxLayout(self.orig_frame)
        toothlayout.addWidget(self.oldtooth)
        self.tooth = tooth()  # self.frame)
        toothlayout = QtGui.QHBoxLayout(self.new_frame)
        toothlayout.addWidget(self.tooth)

        self.signals()
        self.originalProps = {}

    def setExistingProps(self, arg):
        if arg == "":
            self.originalProps = ""
            self.lineEdit.setText("")
        else:
            arg = arg.strip() + ":"
            arg = arg.replace(" ", ":")
            self.originalProps = arg
            self.lineEdit.setText(arg)

    def clear(self):
        self.lineEdit.setText("")
        self.tooth.clear()
        self.tooth.update()
        self.finishedEdit()  # doesn';t work!

    def finishedEdit(self):
        newprops = str(self.lineEdit.text().toAscii())
        self.emit(QtCore.SIGNAL("Changed_Properties"), newprops)

    def keyNav(self, arg):
        if arg == "up":
            self.prevTooth()
        elif arg == "down":
            self.nextTooth()

    def leftTooth(self):
        if self.tooth.isUpper:
            self.prevTooth()
        else:
            self.nextTooth()

    def rightTooth(self):
        if not self.tooth.isUpper:
            self.prevTooth()
        else:
            self.nextTooth()

    def prevTooth(self):
        self.finishedEdit()
        self.emit(QtCore.SIGNAL("NextTooth"), ("up"))

    def nextTooth(self):
        self.finishedEdit()
        self.emit(QtCore.SIGNAL("NextTooth"), ("down"))

    def signals(self):
        QtCore.QObject.connect(
            self.clear_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.clear)
        QtCore.QObject.connect(
            self.lineEdit,
            QtCore.SIGNAL("ArrowKeyPressed"),
            self.keyNav)
        QtCore.QObject.connect(
            self.rightTooth_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.rightTooth)
        QtCore.QObject.connect(
            self.leftTooth_pushButton,
            QtCore.SIGNAL("clicked()"),
            self.leftTooth)


class tooth(QtGui.QWidget):

    def __init__(self, parent=None):
        super(tooth, self).__init__(parent)
        self.isBacktooth = True
        self.quadrant = 1
        self.isUpper = True
        self.isRight = True
        self.setMouseTracking(True)
        self.shapes()
        self.clear()

    def sizeHint(self):
        return self.parent().size()

    def minimumSizeHint(self):
        return QtCore.QSize(80, 80)

    def setBacktooth(self, arg):
        if self.isBacktooth != arg:
            self.isBacktooth = arg
            self.shapes()

    def setRightSide(self, arg):
        self.isRight = arg

    def setUpper(self, arg):
        self.isUpper = arg

    def clear(self):
        self.filledSurfaces = ""
        if self.isBacktooth:
            self.fillcolour = colours.AMALGAM
        else:
            self.fillcolour = colours.COMP

    def leaveEvent(self, event):
        self.mouseOverSurface = None
        self.update()

    def mouseMoveEvent(self, event):
        y = event.y()
        x = event.x()
        print "mouse moving on perio widget", x, y

    def mousePressEvent(self, event):
        y = event.y()
        x = event.x()
        self.emit(QtCore.SIGNAL("toothclicked"))  # not used

    def resizeEvent(self, event):
        self.shapes()

    def shapes(self):
        self.toothRect = QtCore.QRectF(0, 0, self.width(), self.height())
        irw = self.toothRect.width() * \
            0.25  # inner rectangle width
        if self.isBacktooth:
            irh = self.toothRect.height() * \
                0.25  # backtooth inner rectangle height
        else:
            irh = self.toothRect.height() * \
                0.40  # fronttooth inner rectangle height
        self.innerRect = self.toothRect.adjusted(irw, irh, -irw, -irh)

        self.mesial = QtGui.QPolygon([0, 0,
                                      self.innerRect.topLeft().x(
                                      ), self.innerRect.topLeft().y(),
                                      self.innerRect.bottomLeft().x(
                                      ), self.innerRect.bottomLeft().y(),
                                      self.toothRect.bottomLeft().x(), self.toothRect.bottomLeft().y()])

        self.occlusal = QtGui.QPolygon(
            [self.innerRect.topLeft().x(), self.innerRect.topLeft().y(),
             self.innerRect.topRight().x(), self.innerRect.topRight().y(),
             self.innerRect.bottomRight().x(
             ), self.innerRect.bottomRight().y(),
                self.innerRect.bottomLeft().x(), self.innerRect.bottomLeft().y()])

        self.distal = QtGui.QPolygon(
            [self.innerRect.topRight().x(), self.innerRect.topRight().y(),
             self.toothRect.topRight().x(), self.toothRect.topRight().y(),
             self.toothRect.bottomRight().x(
             ), self.toothRect.bottomRight().y(),
             self.innerRect.bottomRight().x(), self.innerRect.bottomRight().y()])

        self.buccal = QtGui.QPolygon([0, 0,
                                      self.toothRect.topRight().x(
                                      ), self.toothRect.topRight().y(),
                                      self.innerRect.topRight().x(
                                      ), self.innerRect.topRight().y(),
                                      self.innerRect.topLeft().x(), self.innerRect.topLeft().y()])

        self.palatal = QtGui.QPolygon(
            [self.toothRect.bottomLeft().x(), self.toothRect.bottomLeft().y(),
             self.innerRect.bottomLeft().x(), self.innerRect.bottomLeft().y(),
             self.innerRect.bottomRight().x(
             ), self.innerRect.bottomRight().y(),
                self.toothRect.bottomRight().x(), self.toothRect.bottomRight().y()])

        self.mouseOverSurface = None  # initiate a value

    def paintEvent(self, event=None):
        '''override the paint event so that we can draw our grid'''
        if self.isBacktooth:
            if self.isUpper:
                if self.isRight:
                    surfs = "DBPMO"
                else:
                    surfs = "MBPDO"
            else:
                if self.isRight:
                    surfs = "DLBMO"
                else:
                    surfs = "MLBDO"
        else:
            if self.isUpper:
                if self.isRight:
                    surfs = "DBPMI"
                else:
                    surfs = "MBPDI"
            else:
                if self.isRight:
                    surfs = "DLBMI"
                else:
                    surfs = "MLBDI"

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.setPen(QtGui.QColor("gray"))
        painter.setBrush(colours.IVORY)
        painter.drawRect(self.toothRect)
        painter.drawRect(self.innerRect)
        painter.drawLine(self.toothRect.topLeft(), self.innerRect.topLeft())
        painter.drawLine(self.toothRect.topRight(), self.innerRect.topRight())
        painter.drawLine(
            self.toothRect.bottomLeft(),
            self.innerRect.bottomLeft())
        painter.drawLine(
            self.toothRect.bottomRight(),
            self.innerRect.bottomRight())
        option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
        rect = self.toothRect.adjusted(0, 0, -self.innerRect.right(), 0)
        painter.drawText(QtCore.QRectF(rect), surfs[0], option)
        rect = self.toothRect.adjusted(0, 0, 0, -self.innerRect.bottom())
        painter.drawText(QtCore.QRectF(rect), surfs[1], option)
        rect = self.toothRect.adjusted(0, self.innerRect.bottom(), 0, 0)
        painter.drawText(QtCore.QRectF(rect), surfs[2], option)
        rect = self.toothRect.adjusted(self.innerRect.right(), 0, 0, 0)
        painter.drawText(QtCore.QRectF(rect), surfs[3], option)
        painter.drawText(QtCore.QRectF(self.innerRect), surfs[4], option)


class chartLineEdit(QtGui.QLineEdit):

    '''override the keypress event for up and down arrow keys.
    '''

    def __init__(self, parent=None):
        super(chartLineEdit, self).__init__(parent)

    def keyPressEvent(self, event):
        '''overrudes QWidget's keypressEvent'''
        if event.key() == QtCore.Qt.Key_Up:
            self.emit(QtCore.SIGNAL("ArrowKeyPressed"), ("up"))
        elif event.key() == QtCore.Qt.Key_Return:
            self.emit(QtCore.SIGNAL("ArrowKeyPressed"), ("down"))
        elif event.key() == QtCore.Qt.Key_Down:
            self.emit(QtCore.SIGNAL("ArrowKeyPressed"), ("down"))
        else:
            QtGui.QLineEdit.keyPressEvent(self, event)

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    ui = tpWidget(Form)
    ui.setExistingProps("MOD ")
    # Form.setEnabled(False)
    Form.show()
    sys.exit(app.exec_())
