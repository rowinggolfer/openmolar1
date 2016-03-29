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

from gettext import gettext as _
import logging
import os
import re

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtPrintSupport
from PyQt5 import QtWidgets

from openmolar.settings import localsettings
from openmolar.qt4gui.compiled_uis import Ui_bulkmail_options

LOGGER = logging.getLogger("openmolar")

DATE_FORMAT = "MMMM, yyyy"
DEBUG = False

SALUTATION = _("Dear")

BODY = '''%s\n%s''' % (
    _("We are writing to inform you that your dental examination is now due."),
    _("Please contact the surgery to arrange an appointment. *")
)

FAMILY_BODY = '''%s\n%s''' % (
    _("We are writing to inform you that your dental examinations "
      "are now due."),
    _("Please contact the surgery to arrange suitable appointments. *"),
)

SIGN_OFF = _("Yours sincerely,")

PS_TEXT = _('* P.S If you already have a future appointment with us - '
            'please accept our apologies and ignore this letter.')

FOOTER = _('We are currently accepting new patients to the practice.'
           'We would be delighted if you would recommend us to your '
           'friends and family.')

try:
    filepath = os.path.join(localsettings.localFileDirectory,
                            "recall_footer.txt")
    f = open(filepath, "r")
    CUSTOM_TEXT = f.read()
    f.close()
except IOError:
    LOGGER.warning("no recall footer found in '%s'" % filepath)
    CUSTOM_TEXT = ""


class OMLetter(object):

    def __init__(self, recipients):
        self.recipients = recipients

    @property
    def head(self):
        return self.recipients[0]

    @property
    def recd(self):
        return self.head.recd

    @property
    def _topline(self):
        head = self.head
        line_ = "%s %s %s" % (
            head.title,
            head.fname.strip(),
            head.sname.strip()
        )
        for r in self.recipients[1:]:
            if r.age > 18:
                line_ += "\n%s %s %s" % (r.title, r.fname, r.sname)
            else:
                line_ += ", %s" % (r.fname)

        if ", " in line_:
            i = line_.rindex(", ")
            line_ = "%s and%s" % (line_[:i], line_[i + 1:])

        return line_

    @property
    def address(self):
        head = self.head

        address_ = '%s\n%s\n%s\n%s\n%s\n%s\n%s' % (
            self._topline,
            head.addr1.title(),
            head.addr2.title(),
            head.addr3.title(),
            head.town,
            head.county,
            head.pcde)

        while re.search(" *\n *\n", address_):
            address_ = re.sub(" *\n\n", "\n", address_)

        return address_

    @property
    def subjects(self):
        subjects_ = []
        for r in self.recipients:
            subjects_.append("%s %s %s - %s %s" % (
                r.title, r.fname, r.sname,
                _("our ref"), r.serialno))
        return subjects_

    @property
    def subject_text(self):
        text = ""
        for subject in self.subjects:
            text += "%s\n" % subject
        return text

    @property
    def is_family(self):
        return len(self.recipients) > 1

    @property
    def salutation(self):

        if self.is_family:
            salut_ = _("Patients")
        elif self.head.age < 18:
            salut_ = self.head.fname
        else:
            salut_ = "%s %s" % (self.head.title, self.head.sname.strip())

        return "%s %s," % (SALUTATION, salut_)

    @property
    def text(self):
        if self.is_family:
            return FAMILY_BODY
        return BODY


class TreeItem(object):

    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        try:
            return self.itemData[column]
        except IndexError:
            return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0


class treeModel(QtCore.QAbstractItemModel):

    def __init__(self, header, mydata):
        super().__init__()
        self.FAMILYICON = QtGui.QIcon()
        self.FAMILYICON.addPixmap(QtGui.QPixmap(":/agt_family.png"))

        self.rootItem = TreeItem(header)
        self.setupModelData(mydata, self.rootItem)

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return item.data(index.column())
        elif role == QtCore.Qt.DecorationRole and index.column() == 1:
            if item.itemData.grouped:
                return self.FAMILYICON
        elif role == QtCore.Qt.BackgroundRole:
            if item.itemData.grouped:
                if item.itemData.letterno % 2:
                    return QtGui.QBrush(QtGui.QColor(190, 190, 190))
                else:
                    return QtGui.QBrush(QtGui.QColor(160, 160, 160))
            else:
                return None
        elif role == QtCore.Qt.UserRole:
            # a user role which simply returns the python object
            return item.itemData

        return None

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
           role == QtCore.Qt.DisplayRole):
            return self.rootItem.data(section)

        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def setupModelData(self, lines, parent):
        parents = [parent]
        indentations = [0]

        letterNo = 0

        for lineData in lines:
            position = 0

            if lineData[0] == letterNo:
                position = 1
            letterNo = lineData[0]

            if position > indentations[-1]:
                if parents[-1].childCount() > 0:
                    parents.append(
                        parents[-1].child(parents[-1].childCount() - 1))
                    indentations.append(position)
            else:
                while position < indentations[-1] and len(parents) > 0:
                    parents.pop()
                    indentations.pop()

            parents[-1].appendChild(TreeItem(lineData, parents[-1]))


class bulkMails(object):

    def __init__(self, om_gui):
        self.om_gui = om_gui
        self.printer = QtPrintSupport.QPrinter()
        self.printer.setPageSize(QtPrintSupport.QPrinter.A4)
        self.headers = (_("no data loaded"),)
        self.recipients = ()
        self.bulk_model = treeModel(self.headers, self.recipients)
        self.adate = localsettings.currentDay()
        self.expanded = False
        self.use_given_recall_date = False
        self.LONGDATE = True

    def showOptions(self):
        '''
        user is wishing to change some default setting
        currently the only option is the date
        '''
        def enableDate(checked):
            '''
            only enable the date Edit if customRadio button is checked
            '''
            dl.dateEdit.setEnabled(checked)
        dialog = QtWidgets.QDialog(self.om_gui)
        dl = Ui_bulkmail_options.Ui_Dialog()
        dl.setupUi(dialog)
        dl.dateEdit.setDate(localsettings.currentDay())
        dl.custDate_radioButton.toggled.connect(enableDate)
        if dialog.exec_():
            if dl.custDate_radioButton.isChecked():
                self.adate = dl.dateEdit.date().toPyDate()
            if dl.today_radioButton.isChecked():
                self.adate = localsettings.currentDay()
            self.use_given_recall_date = dl.recd_radioButton.isChecked()
            self.LONGDATE = dl.fullDate_radioButton.isChecked()

            self.om_gui.advise(_("options set"), 1)

    def expand_contract(self):
        '''
        change the expansion state
        '''
        self.expanded = not self.expanded
        if self.expanded:
            self.om_gui.ui.bulk_mailings_treeView.expandAll()
        else:
            self.om_gui.ui.bulk_mailings_treeView.collapseAll()
        self.update_expand_ButtonText()

    def update_expand_ButtonText(self):
        '''
        make sure the expand / collapse button text is correct
        '''
        if self.expanded:
            self.om_gui.ui.bulk_mail_expand_pushButton.setText(
                _("Collapse All"))
        else:
            self.om_gui.ui.bulk_mail_expand_pushButton.setText(
                _("Expand All"))

    def setData(self, headers, recipients):
        '''
        load the recipient data
        '''
        self.headers = headers
        self.recipients = recipients
        self.populateTree()
        self.expanded = False
        self.update_expand_ButtonText()
        for i in range(len(self.headers)):
            self.om_gui.ui.bulk_mailings_treeView.resizeColumnToContents(i)

    def populateTree(self):
        '''
        load the bulk mailing tree view
        '''
        self.bulk_model = treeModel(self.headers, self.recipients)
        self.om_gui.ui.bulk_mailings_treeView.setModel(self.bulk_model)

    def iterate_letters(self):
        '''
        iterate over the letters
        '''
        letters = {}
        for recipient in self.recipients:
            if recipient.letterno in letters:
                letters[recipient.letterno].append(recipient)
            else:
                letters[recipient.letterno] = [recipient]

        for key in sorted(letters):
            recipients = letters[key]
            letter = OMLetter(recipients)
            yield letter

    def selected(self, index):
        '''
        emit the serialno of the selected row
        '''
        try:
            # item = index.internalPointer()
            pt = self.bulk_model.data(index, QtCore.Qt.UserRole)
            print(pt.serialno)
            return pt.serialno

        except IndexError:
            print("selected bulk mail out of range")

    def print_(self):
        dialog = QtPrintSupport.QPrintDialog(self.printer, self.om_gui)
        if not dialog.exec_():
            return

        font = QtGui.QFont("Helvetica", 11)
        fm = QtGui.QFontMetrics(font)
        line_height = fm.height()

        italic_font = QtGui.QFont(font)
        italic_font.setItalic(True)

        sigFont = QtGui.QFont("URW Chancery L", 18)
        sigFont.setBold(True)
        sig_font_height = QtGui.QFontMetrics(sigFont).height() * 1.2

        pageRect = self.printer.pageRect()

        LEFT = 60
        RIGHT = 80
        TOP = 170
        RECT_WIDTH = pageRect.width() - (LEFT + RIGHT)

        ADDRESS_LEFT = 80
        ADDRESS_HEIGHT = 140
        FOOTER_HEIGHT = 180
        DATE_HEIGHT = 2 * line_height
        BODY_HEIGHT = pageRect.height() - (
            TOP + ADDRESS_HEIGHT + FOOTER_HEIGHT + DATE_HEIGHT)

        addressRect = QtCore.QRectF(ADDRESS_LEFT, TOP,
                                    300, ADDRESS_HEIGHT)

        dateRect = QtCore.QRectF(LEFT, addressRect.bottom(),
                                 RECT_WIDTH, DATE_HEIGHT)

        bodyRect = QtCore.QRectF(LEFT, dateRect.bottom(),
                                 RECT_WIDTH, BODY_HEIGHT)

        footerRect = QtCore.QRectF(LEFT,
                                   pageRect.height() - FOOTER_HEIGHT,
                                   RECT_WIDTH, FOOTER_HEIGHT)

        painter = QtGui.QPainter(self.printer)

        first_page = True
        page_no = 0

        for letter in self.iterate_letters():
            page_no += 1

            if dialog.printRange() == dialog.PageRange:
                if page_no < dialog.fromPage():
                    continue
                if dialog.toPage() != 0 and page_no > dialog.toPage():
                    continue

            if not first_page:
                self.printer.newPage()
            first_page = False

            painter.save()
            painter.setFont(font)
            painter.setPen(QtCore.Qt.black)

            option = QtGui.QTextOption(QtCore.Qt.AlignLeft)
            option.setWrapMode(QtGui.QTextOption.WordWrap)

            # address
            painter.drawText(addressRect, letter.address, option)
            if DEBUG:
                painter.drawRect(addressRect.adjusted(2, 2, -2, -2))
            # date

            if self.use_given_recall_date:
                pdate = letter.recd
            else:
                pdate = self.adate

            if self.LONGDATE:
                pdate_str = localsettings.longDate(pdate)
            else:
                pdate_str = "%s %s" % (localsettings.monthName(pdate),
                                       pdate.year)

            painter.drawText(dateRect, pdate_str,
                             QtGui.QTextOption(QtCore.Qt.AlignRight))
            if DEBUG:
                painter.drawRect(dateRect.adjusted(2, 2, -2, -2))
            # salutation
            rect = bodyRect.adjusted(
                0, 0, 0, 2 * line_height - bodyRect.height())
            painter.drawText(rect, letter.salutation, option)
            if DEBUG:
                painter.drawRect(rect.adjusted(2, 2, -2, -2))

            # subject
            # option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
            font.setBold(True)
            painter.setFont(font)
            subject_count = len(letter.subjects) + 1
            rect = QtCore.QRectF(
                rect.bottomLeft().x(), rect.bottomLeft().y(),
                bodyRect.width(), line_height * subject_count)

            subj_rect = rect.adjusted(50, 0, -50, 0)
            painter.drawText(subj_rect, letter.subject_text, option)
            if DEBUG:
                painter.drawRect(subj_rect.adjusted(2, 2, -2, -2))
            font.setBold(False)
            painter.setFont(font)

            # body
            line_count = letter.text.count("\n") + 3
            body_rect = QtCore.QRectF(
                rect.bottomLeft().x(), subj_rect.bottomLeft().y(),
                bodyRect.width(), line_height * line_count)

            painter.drawText(body_rect, letter.text, option)
            if DEBUG:
                painter.drawRect(body_rect.adjusted(2, 2, -2, -2))

            # custom
            line_count = CUSTOM_TEXT.count("\n") + 5
            custom_rect = QtCore.QRectF(
                body_rect.bottomLeft().x(), body_rect.bottomLeft().y(),
                bodyRect.width(), line_height * line_count)

            painter.setFont(font)
            painter.drawText(custom_rect, CUSTOM_TEXT, option)

            if DEBUG:
                painter.drawRect(custom_rect.adjusted(2, 2, -2, -2))

            # signature
            # place signature immediately after the body
            # + custom text (which will vary)

            sign_off_rect = QtCore.QRectF(
                custom_rect.bottomLeft().x(), custom_rect.bottomLeft().y(),
                body_rect.width(), line_height * 1.5)
            painter.drawText(sign_off_rect, SIGN_OFF, option)
            if DEBUG:
                painter.drawRect(sign_off_rect.adjusted(2, 2, -2, -2))

            sig_rect = sign_off_rect.adjusted(
                20, sign_off_rect.height(), 0, sig_font_height)
            painter.save()
            painter.setFont(sigFont)
            painter.drawText(sig_rect, localsettings.PRACTICE_NAME, option)
            if DEBUG:
                painter.drawRect(sig_rect.adjusted(2, 2, -2, -2))
            painter.restore()

            # ps
            line_count = PS_TEXT.count("\n") + 2
            ps_rect = QtCore.QRectF(
                body_rect.bottomLeft().x(),
                sig_rect.bottomLeft().y() + line_height*2,
                bodyRect.width(), line_height * line_count)

            painter.setFont(font)
            painter.drawText(ps_rect, PS_TEXT, option)

            if DEBUG:
                painter.drawRect(ps_rect.adjusted(2, 2, -2, -2))

            # footer
            option = QtGui.QTextOption(QtCore.Qt.AlignHCenter)
            option.setWrapMode(QtGui.QTextOption.WordWrap)

            painter.drawLine(footerRect.topLeft(), footerRect.topRight())
            painter.setFont(italic_font)

            painter.drawText(footerRect, FOOTER, option)
            if DEBUG:
                painter.drawRect(footerRect.adjusted(2, 2, -2, -2))

            # fold marks
            pen = QtGui.QPen(QtGui.QBrush(QtCore.Qt.black), 3)
            painter.setPen(pen)
            top_fold_y = pageRect.height() / 3
            painter.drawLine(0, top_fold_y, 10, top_fold_y)

            top_fold_y = pageRect.height() * 2 / 3
            painter.drawLine(0, top_fold_y, 10, top_fold_y)

            painter.restore()


if __name__ == "__main__":
    DEBUG = True
    localsettings.station = "reception"
    app = QtWidgets.QApplication([])
    os.chdir(os.environ.get("HOME", "."))
    from openmolar.qt4gui import maingui
    from openmolar.dbtools import recall

    om_gui = maingui.OpenmolarGui()

    conditions = "new_patients.serialno=%s"
    values = (1,)
    patients = recall.getpatients(conditions, values)

    letters = bulkMails(om_gui)
    # letters.showOptions()
    letters.setData(recall.HEADERS, patients)
    letters.print_()
    app.closeAllWindows()
