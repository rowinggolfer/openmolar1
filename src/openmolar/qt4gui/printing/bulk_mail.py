# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import math
import os, sys
from PyQt4 import QtCore, QtGui

if __name__ == "__main__":

    sys.path.insert(0, os.path.abspath("../../../"))

from openmolar.settings import localsettings
from openmolar.qt4gui.compiled_uis import Ui_bulkmail_options

DATE_FORMAT = "MMMM, yyyy"

try:
    f = open(os.path.join(
        localsettings.localFileDirectory, "recall_footer.txt"), "r")
    PROMO_TEXT = f.read()
    f.close()
except OSError:
    print "no recall footer found"
    PROMO_TEXT= ""


class omLetter(object):
    def __init__(self):
        self.salutation = ""
        self.address_topline =""
        self.patients = ""
        self.address = ""
        self.recd = None
        self.body = '''\n\n%s <<SALUTATION>>,
\n<<NAMES>>\n\n%s\n\n%s\n\n%s'''% (_("Dear"),
_("We are writing to inform you that your dental examination is now due."),
_("Please contact the surgery to arrange an appointment. *"),
_("We look forward to seeing you in the near future."))
        self.bodyfamily = '''\n\n%s,\n\n<<NAMES>>\n%s\n\n%s\n%s'''%(
_("Dear Patients"),
_("We are writing to inform you that your dental examinations are now due."),
_("Please contact the surgery to arrange suitable appointments. *"),
_("We look forward to seeing you in the near future."))

        self.sign_off = _("Yours sincerely,")

        self.promo_text = PROMO_TEXT
        self.signature = localsettings.CORRESPONDENCE_SIG

        self.footer = _('''* If you already have a future appointment with us -
please accept our apologies and ignore this letter.''')

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
            return QtCore.QVariant(self.itemData[column])
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
        super(QtCore.QAbstractItemModel, self).__init__()
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
            return QtCore.QVariant()

        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return item.data(index.column())
        elif role == QtCore.Qt.DecorationRole and index.column() == 1:
            if item.itemData.grouped:
                return QtCore.QVariant(self.FAMILYICON)
        elif role == QtCore.Qt.BackgroundRole:
            if item.itemData.grouped:
                if item.itemData.letterno % 2:
                    brush = QtGui.QBrush(QtGui.QColor(190, 190, 190))
                else:
                    brush = QtGui.QBrush(QtGui.QColor(160, 160, 160))
                return QtCore.QVariant(brush)
            else:
                return QtCore.QVariant()
        elif role == QtCore.Qt.UserRole:
            ## a user role which simply returns the python object
            return item.itemData

        return QtCore.QVariant()

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
        role == QtCore.Qt.DisplayRole):
            return self.rootItem.data(section)

        return QtCore.QVariant()

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

        number = 0
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
        self.printer = QtGui.QPrinter()
        self.printer.setPageSize(QtGui.QPrinter.A4)
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
        dialog = QtGui.QDialog(self.om_gui)
        dl = Ui_bulkmail_options.Ui_Dialog()
        dl.setupUi(dialog)
        dl.dateEdit.setDate(localsettings.currentDay())
        dialog.connect(dl.custDate_radioButton,
        QtCore.SIGNAL("toggled (bool)"), enableDate)
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
        self.expanded =  False
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
            if letters.has_key(recipient.letterno):
                letters[recipient.letterno].append(recipient)
            else:
                letters[recipient.letterno] = [recipient]

        for key in sorted(letters):
            recipients = letters[key]
            head = recipients[0]
            address = '%s\n%s\n%s\n%s\n%s\n%s'% (
            head.addr1.title(), head.addr2.title(),
            head.addr3.title(), head.town,
            head.county, head.pcde)

            letter = omLetter()
            while "\n\n" in address:
                address = address.replace("\n\n","\n")
            letter.address = address
            letter.recd = head.recd

            letter.names = ""
            for r in recipients:
                letter.names += "        %s %s %s - %s %s\n"% (
                r.title, r.fname, r.sname, _("our ref"), r.serialno)

            letter.address_topline = "%s %s %s"% (head.title,
            head.fname.strip(), head.sname.strip())

            if head.age < 18:
                letter.salutation = head.fname
            else:
                letter.salutation = "%s %s"% (head.title, head.sname.strip())

            for r in recipients[1:]:
                if r.age > 18:
                    letter.address_topline += "\n%s %s %s"% (r.title,
                    r.fname, r.sname)
                else:
                    letter.address_topline += ", %s"% (r.fname)

            if ", " in letter.address_topline:
                i = letter.address_topline.rindex(", ")
                letter.address_topline = "%s and%s"% (
                letter.address_topline[:i], letter.address_topline[i+1:])

            isFamily = len(recipients)>1
            isLastLetter = key == sorted(letters)[-1]

            yield letter, isFamily, isLastLetter

    def selected(self, index):
        '''
        emit the serialno of the selected row
        '''
        try:
            #item = index.internalPointer()
            pt = self.bulk_model.data(index, QtCore.Qt.UserRole)
            print pt.serialno
            return pt.serialno

        except IndexError:
            print "selected bulk mail out of range"

    def printViaQPainter(self, showRects = False):
        dialog = QtGui.QPrintDialog(self.printer, self.om_gui)
        if not dialog.exec_():
            return

        sansFont = QtGui.QFont("Helvetica", 10)
        sansLineHeight = QtGui.QFontMetrics(sansFont).height()
        serifFont = QtGui.QFont("Times", 11)
        serifLineHeight = QtGui.QFontMetrics(serifFont).height()
        sigFont = QtGui.QFont("Lucida Handwriting",13)
        fm = QtGui.QFontMetrics(serifFont)
        datewidth = fm.width("Wednesday September 2999 ")
        dateheight = fm.height()
        pageRect = self.printer.pageRect()

        LEFT = 50
        TOP = 150
        RECT_WIDTH = pageRect.width() - (2 * LEFT)
        ADDRESS_HEIGHT = 150
        FOOTER_HEIGHT = 150
        BODY_HEIGHT = pageRect.height() - TOP - ADDRESS_HEIGHT - FOOTER_HEIGHT

        addressRect = QtCore.QRectF(LEFT, TOP, RECT_WIDTH, ADDRESS_HEIGHT)

        dateRect = QtCore.QRectF(LEFT + RECT_WIDTH - datewidth,
        TOP + ADDRESS_HEIGHT, datewidth, dateheight)

        bodyRect = QtCore.QRectF(LEFT, TOP + ADDRESS_HEIGHT + dateheight,
        RECT_WIDTH, BODY_HEIGHT)

        promoRect = bodyRect.adjusted(0, BODY_HEIGHT*.5, 0, 0)

        sigRect = bodyRect.adjusted(0,bodyRect.height()*.75,0,0)

        footerRect = QtCore.QRectF(LEFT,
        pageRect.height() - FOOTER_HEIGHT,
        RECT_WIDTH, FOOTER_HEIGHT)

        painter = QtGui.QPainter(self.printer)
        
        if dialog.printRange() == dialog.PageRange:
            page = dialog.fromPage()
        else:
            page = 1
        
        for letter, FamilyLetter, lastpage in self.iterate_letters():
            if dialog.toPage() != 0 and page > dialog.toPage():
                continue 
            if page < dialog.fromPage():
                continue
                
            painter.save()
            painter.setPen(QtCore.Qt.black)

            option = QtGui.QTextOption(QtCore.Qt.AlignLeft)
            option.setWrapMode(QtGui.QTextOption.WordWrap)

            ##address
            painter.drawText(addressRect, "%s\n%s"% (
            letter.address_topline, letter.address), option)
            if showRects:
                painter.drawRect(addressRect)
            ##date
            painter.setFont(serifFont)
            if self.use_given_recall_date:
                pdate = letter.recd
            else:
                pdate = self.adate

            if self.LONGDATE:
                pdate_str = localsettings.longDate(pdate)
            else:
                pdate_str = "%s %s"% (localsettings.monthName(pdate),
                pdate.year)

            painter.drawText(dateRect, pdate_str)
            if showRects:
                painter.drawRect(dateRect)

            ##body
            if FamilyLetter:
                painter.drawText(bodyRect, letter.bodyfamily.replace(
                "<<NAMES>>",letter.names), option)
            else:
                body = letter.body.replace(
                "<<SALUTATION>>",letter.salutation)
                body = body.replace("<<NAMES>>",letter.names)
                painter.drawText(bodyRect, body, option)
            if showRects:
                painter.drawRect(bodyRect)

            ##promo
            font = painter.font()
            font.setItalic(True)
            painter.setFont(font)
            painter.drawText(promoRect, letter.promo_text, option)
            if showRects:
                painter.drawRect(bodyRect)
            font.setItalic(False)
            painter.setFont(font)



            ##signature
            painter.drawText(sigRect, letter.sign_off, option)

            painter.setFont(sigFont)
            painter.drawText(sigRect. adjusted(0, 40,0,0),
                letter.signature, option)
            if showRects:
                painter.drawRect(sigRect)


            ##footer
            painter.drawLine(footerRect.topLeft(), footerRect.topRight())
            font = QtGui.QFont("Helvetica", 7)
            font.setItalic(True)
            painter.setFont(font)

            option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
            option.setWrapMode(QtGui.QTextOption.WordWrap)

            painter.drawText(footerRect, letter.footer, option)
            if showRects:
                painter.drawRect(footerRect)

            page += 1
            if not lastpage:
                self.printer.newPage()
            painter.restore()

if __name__ == "__main__":

    app = QtGui.QApplication([])
    import datetime,os
    os.chdir("/home/neil")
    from openmolar.qt4gui import maingui
    from openmolar.dbtools import recall

    om_gui = maingui.openmolarGui(app)
    start = datetime.date(2009,2,1)
    end = datetime.date(2009,2,1)

    letters = bulkMails(om_gui)
    letters.showOptions()
    letters.setData(recall.HEADERS, recall.getpatients(start, end))
    letters.printViaQPainter(True)
    app.closeAllWindows()
