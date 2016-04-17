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


class MessagePopup(QtWidgets.QWidget):

    '''
    A custom Widget which can be used as a brief non-modal message box.
    '''

    def __init__(self, message, parent=None):
        super(MessagePopup, self).__init__(parent)
        padding = 12

        # create a QTextDocument, which will handle any rich text in our
        # messages.
        doc = QtGui.QTextDocument(self)
        doc.setHtml(message)
        doc.setDocumentMargin(padding)
        doc.adjustSize()
        self.doc = doc

        doc_width, doc_height = doc.size().width(), doc.size().height()

        icon = QtGui.QIcon(":/openmolar.svg")
        self.pixmap = icon.pixmap(48, 48)

        pic_width, pic_height = self.pixmap.width(), self.pixmap.height()

        self.setBrushes()

        self.setMouseTracking(True)

        width = doc_width + pic_width + padding * 2
        if width < self.minimumWidth():
            width = self.minimumWidth()

        height = doc_height
        if height < pic_height:
            height = pic_height
        height += padding * 2

        self.setFixedSize(width, height)

        # values required at painttime.
        self.rect_f = QtCore.QRectF(0, 0, width, height)

        self.text_rectf = QtCore.QRectF(padding, padding, doc_width,
                                        doc_height)

        self.icon_rectf = QtCore.QRectF(padding + doc_width,
                                        padding, pic_width, pic_height)

    def setIcon(self, icon):
        self.pixmap = icon.pixmap(30, 30)
        self.pixmapRect = QtCore.QRectF(self.pixmap.rect())

    def setBrushes(self, alpha=150):
        self.fully_visible = alpha == 150

        pal = self.palette()

        col = pal.shadow().color()
        col.setAlpha(alpha)
        self.border_brush = QtGui.QBrush(col)

        col = pal.toolTipBase().color()
        col.setAlpha(alpha)
        self.back_brush = QtGui.QBrush(col)

        pen_colour = pal.toolTipText().color()
        pen_colour.setAlpha(alpha + 50)
        self.pen = QtGui.QPen(pen_colour)

    def minimumWidth(self):
        w = 300
        if self.parent() is not None:
            if self.parent().width() > w * 4:
                w = self.parent().width() / 4
        return w

    def toggleMouseEvents(self, off=True):
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, off)

    def mouseMoveEvent(self, event):
        self.update()

    def mousePressEvent(self, event):
        self.toggleMouseEvents()

    def leaveEvent(self, *args):
        # gets called after toggleMouseEvents :(
        self.update()

    def leaveEvent_(self, *args):
        '''
        widget won't be mouse aware for leaveEvent..
        so this has to be called by parent
        '''
        self.toggleMouseEvents(False)
        self.update()

    def paintEvent(self, event):
        cursor_pos = self.mapFromGlobal(self.cursor().pos())
        if self.rect().contains(cursor_pos):
            self.setBrushes(40)
        else:
            self.setBrushes()

        painter = QtGui.QPainter(self)

        rect_f = self.rect_f.adjusted(0, 0, -1, -1)
        # above line allows for pen width

        painter.setPen(QtGui.QPen(self.border_brush, 1))
        painter.setBrush(self.border_brush)
        painter.drawRoundedRect(rect_f, 15, 15)

        rect_f = rect_f.adjusted(5, 5, -5, -5)
        painter.setPen(QtGui.QPen(self.back_brush, 1))
        painter.setBrush(self.back_brush)
        painter.drawRoundedRect(rect_f, 15, 15)

        painter.drawPixmap(self.icon_rectf, self.pixmap,
                           QtCore.QRectF(self.pixmap.rect()))

        painter.setPen(self.pen)

        # a hack because documentLayout.drawText method is sluggish
        # when used with a semi-transparent pen.
        # faint version will lack italics and bold styles etc.. but isn't
        # an issue in practice!
        if self.fully_visible:
            dl = self.doc.documentLayout()
            dl.draw(painter, dl.PaintContext())
        else:
            option = QtGui.QTextOption()
            option.setWrapMode(option.WrapAnywhere)
            painter.drawText(self.text_rectf, self.doc.toPlainText(), option)


class Advisor(QtWidgets.QWidget):

    '''
    provides various notifications to the user
    '''

    def __init__(self, parent=None):
        '''
        Advisor.__init__(self, parent=None)
        '''
        QtWidgets.QWidget.__init__(self, parent)
        self.brief_messages = []
        self.briefMessagePosition = QtCore.QPoint(10, 10)

        self.brief_message_box = None
        self.single_shot = QtCore.QTimer(self)
        self.single_shot.setSingleShot(True)
        self.single_shot.timeout.connect(self.hide_brief_message)

        self.right_to_left = False

    def setBriefMessagePosition(self, point, right_to_left=False):
        '''
        set the position the brief message label will appear
        arg is QtCore.QPoint,
        if right_to_left is true, then this point is the top right of the box.
        '''
        self.briefMessagePosition = point
        self.right_to_left = right_to_left

    def hide_brief_message(self):
        if self.brief_message_box:
            self.brief_message_box.hide()
            self.brief_message_box.deleteLater()
        self.brief_message_box = None

    def advise_dl(self, message):
        '''
        convenience function which calls advise with a default of 1.
        useful when connected to a signal
        '''
        self.advise(message, 1)

    def advise_err(self, message):
        '''
        convenience function which calls advise with a default of 1.
        useful when connected to a signal
        '''
        self.advise(message, 2)

    def advise(self, message, warning_level=0):
        '''
        inform the user of events -
        warning level0 = no interaction popup.
        warning level 1 advisory, requires user response.
        warning level 2 warning, and logged in output.
        '''
        def show_brief_messages():
            self.hide_brief_message()
            full_message = "<body>"
            for mess in self.brief_messages:
                full_message += "%s <hr />" % mess
            full_message = full_message.rstrip("<hr />") + "</body>"
            self.brief_message_box = MessagePopup(full_message, self)
            self.brief_message_box.right_to_left = self.right_to_left
            self.brief_message_box.show()
            self.brief_message_box.raise_()
            if self.right_to_left:
                x = (self.briefMessagePosition.x() -
                     self.brief_message_box.width())
                pos = QtCore.QPoint(x, self.briefMessagePosition.y())
            else:
                pos = self.briefMessagePosition
            self.brief_message_box.move(pos)
            app = QtWidgets.QApplication.instance()
            if app:
                app.processEvents()

        def hide_brief_message():
            first_message = self.brief_messages[0]
            self.brief_messages.remove(first_message)
            if self.brief_messages == []:
                self.single_shot.setInterval(2000)
                self.single_shot.start()
            else:
                self.single_shot.stop()
                show_brief_messages()

        if warning_level == 0:
            self.brief_messages.append(message)
            show_brief_messages()
            QtCore.QTimer.singleShot(7000, hide_brief_message)  # 7 seconds

            try:
                self.statusbar.showMessage(message, 10000)
            except AttributeError:
                pass

        elif warning_level == 1:
            QtWidgets.QMessageBox.information(self, _("Advisory"), message)

        elif warning_level == 2:
            QtWidgets.QMessageBox.warning(self, _("Error"), message)

    def wait(self, waiting=True):
        app = QtWidgets.QApplication.instance()
        if waiting:
            app.setOverrideCursor(QtCore.Qt.WaitCursor)
        else:
            app.restoreOverrideCursor()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    advisor = Advisor()
    advisor.show()
    advisor.advise("hello world")
    advisor.advise("hello world", 1)
    advisor.advise("hello world", 2)
    app.exec_()
