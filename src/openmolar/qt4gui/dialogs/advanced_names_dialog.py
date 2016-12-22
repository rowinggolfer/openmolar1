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
LOGGER = logging.getLogger("openmolar")

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar.connect import connect

from openmolar.qt4gui.customwidgets.om_webview import OMWebView
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel
from openmolar.qt4gui.customwidgets.upper_case_line_edit \
    import UpperCaseLineEdit
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog


PSEUDONYMS_QUERY = '''SELECT ix, alt_fname, alt_sname, comment, search_include
FROM pseudonyms WHERE serialno=%s'''

INSERT_PSN_QUERY = '''INSERT INTO pseudonyms (serialno, alt_sname, comment)
VALUES (%s, %s, 'previous surname')'''

INSERT_ALT_QUERY = '''INSERT INTO pseudonyms
(serialno, alt_fname, alt_sname, comment) VALUES (%s, %s, %s, %s)'''

UPDATE_ALT_QUERY = \
    'UPDATE pseudonyms SET alt_fname=%s, alt_sname=%s, comment=%s WHERE ix=%s'

DELETE_QUERY = 'DELETE FROM pseudonyms WHERE ix=%s'

HTML = '''
<html>
<body>
<div align="center">
<h3>%%s %%s</h3>
</div>
<h4>%s</h4>
<ul><li>%%s</li></ul>
<h4>%s</h4>
<ul><li>%%s</li></ul>
''' % (_("Previous Surname(s)"), _("Alternative Name(s)"))

LINK = '''
%s %s
<a href='edit_name_%s'>
<img src='qrc:/icons/pencil.png' height='25' width='25'/>
</a>
%s%s'''

class AltNameEntryDialog(BaseDialog):

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("Alternative Name Dialog"))

        self.label = WarningLabel(_("Please enter an alternate name"))
        self.fname_le = UpperCaseLineEdit()
        self.sname_le = UpperCaseLineEdit()
        self.comment_le = QtWidgets.QLineEdit()
        self.comment_le.setText(_("Alternative Name"))

        frame = QtWidgets.QFrame()
        layout = QtWidgets.QFormLayout(frame)
        layout.addRow(_("Alternative First Name"), self.fname_le)
        layout.addRow(_("Alternative Surname"), self.sname_le)
        layout.addRow(_("Reason"), self.comment_le)

        self.insertWidget(self.label)
        self.insertWidget(frame)

        for le in (self.fname_le, self.sname_le, self.comment_le):
            le.textChanged.connect(self._enable)

    def _enable(self, text):
        self.enableApply(True)


class Pseudonym(object):
    def __init__(self, ix, fname, sname, comment, search_include):
        self.ix = ix
        self.fname = fname if fname else ""
        self.sname = sname if sname else ""
        self.comment = comment
        self.search_include = search_include

    def html(self):
        comment = "" if self.comment == "previous surname" else \
            "<br /><em>(%s)</em>" % self.comment
        inc = "<br />%s" % _("NOT included in searches") \
            if not self.search_include else ""
        return LINK % (self.fname, self.sname, self.ix, comment, inc)


class AdvancedNamesDialog(BaseDialog):
    pt = None
    pseudonyms = []

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)
        self.setWindowTitle(_("Advanced Names Dialog"))

        label = WarningLabel(_("Previous Surnames, Nicknames, and alternate "
            "spelling can help when searching for patients"))

        self.browser = OMWebView(self)
        self.browser.linkClicked.connect(self.link_clicked)

        self.insertWidget(label)
        self.insertWidget(self.browser)

        self.cancel_but.hide()
        self.enableApply()

    def link_clicked(self, url):
        url_text = url.toString()
        if url_text == "add_psn":
            self.add_previous_surname()
        elif url_text == "add_alt":
            self.add_alt_name()
        else:
            m = re.match(r"edit_name_(\d+)", url_text)
            if m:
                ix = int(m.groups()[0])
                self.edit_name(ix)

    def add_previous_surname(self, psn=""):
        LOGGER.info("add a surname")
        if psn == "":
            message = _("Please enter a previous surname")
        else:
            message = "%s '%s' %s" % (_("Save"),
                                    psn,
                                    _("as a previous surname?"))

        surname, result = \
            QtWidgets.QInputDialog.getText(self,
                                           _("Input required"),
                                           message,
                                           QtWidgets.QLineEdit.Normal,
                                           psn)
        if result:
            LOGGER.info("adding %s as a previous surname", surname)
            db = connect()
            cursor = db.cursor()
            cursor.execute(INSERT_PSN_QUERY,
                           (self.pt.serialno, surname.upper()))
            cursor.close()
            self.set_patient(self.pt)
            return True

    def add_alt_name(self):
        LOGGER.info("add an alternative name")
        dl = AltNameEntryDialog(self)
        if dl.exec_():
            fname = dl.fname_le.text()
            sname = dl.sname_le.text()
            comment = dl.comment_le.text()
            db = connect()
            cursor = db.cursor()

            cursor.execute(INSERT_ALT_QUERY, (self.pt.serialno,
                                              None if not fname else fname,
                                              None if not sname else sname,
                                              comment))
            cursor.close()
            self.set_patient(self.pt)

    def edit_name(self, ix):
        LOGGER.info("edit name %s", ix)
        for pseudonym in self.pseudonyms:
            if pseudonym.ix == ix:
                break
        dl = AltNameEntryDialog(self)
        dl.label.setText(_("Edit this name (or leave both name fields blank "
                           "to delete a reference to this name)"))
        dl.fname_le.setText(pseudonym.fname)
        dl.sname_le.setText(pseudonym.sname)
        dl.comment_le.setText(pseudonym.comment)
        dl.enableApply(False)
        if dl.exec_():
            fname = dl.fname_le.text()
            sname = dl.sname_le.text()
            comment = dl.comment_le.text()
            db = connect()
            cursor = db.cursor()
            if sname == "" and fname =="":
                cursor.execute(DELETE_QUERY, (ix,))
            else:
                cursor.execute(UPDATE_ALT_QUERY, (None if not fname else fname,
                                              None if not sname else sname,
                                              comment, ix))
            cursor.close()
            self.set_patient(self.pt)

    def set_patient(self, pt):
        '''
        pass a patient object to set the serialnumber and name fields.
        '''
        self.pt = pt
        db = connect()
        cursor = db.cursor()
        cursor.execute(PSEUDONYMS_QUERY, (pt.serialno,))
        alts = []
        for row in cursor.fetchall():
            pseudonym = Pseudonym(*row)
            alts.append(pseudonym)
        self.pseudonyms = alts

        previous = '</li><li>'.join(
            [p.html() for p in alts if p.comment=="previous surname"] +
            ['<a href="add_psn">%s</a>' % _("Add New")])
        alts = '</li><li>'.join(
            [p.html() for p in alts if p.comment!="previous surname"] +
            ['<a href="add_alt">%s</a>' % _("Add New")])
        self.browser.setHtml(HTML % (self.fname, self.sname, previous, alts))
        page = self.browser.page()
        page.setLinkDelegationPolicy(page.DelegateAllLinks)

    @property
    def sname(self):
        try:
            return self.pt.sname
        except AttributeError:
            pass

    @property
    def fname(self):
        try:
            return self.pt.fname
        except AttributeError:
            pass

    def check_save_previous_surname(self, surname):
        self.show()
        if self.add_previous_surname(surname):
            self.exec_()

    def sizeHint(self):
        return QtCore.QSize(400, 500)


if __name__ == "__main__":
    from openmolar.dbtools import patient_class

    LOGGER.setLevel(logging.DEBUG)
    app = QtWidgets.QApplication([])

    pt_ = patient_class.patient(32809)

    dl = AdvancedNamesDialog()
    dl.set_patient(pt_)
    if dl.exec_():
       LOGGER.info("changed advanced names for %s %s", dl.sname, dl.fname)
