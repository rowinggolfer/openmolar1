#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011-2012,  Neil Wallace <neil@openmolar.com>                  ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

import logging
import re
import urllib2
from xml.dom import minidom
from PyQt4 import QtGui, QtCore

if __name__ == "__main__":
    import os, sys
    sys.path.insert(0, os.path.abspath("../../../"))

from openmolar.settings import localsettings
from openmolar.qt4gui.customwidgets.upper_case_line_edit import UpperCaseLineEdit
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

LOGGER = logging.getLogger("openmolar")

LOOKUP_URL = "http://www.psd.scot.nhs.uk/dev/simd/simdLookup.aspx"

## here is the result when using this

EXAMPLE_RESULT = '''
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>
 SIMD Lookup for PSD
</title></head>
<body>
    <form method="post" action="simdLookup.aspx?_=1348071532912&amp;pCode=IV2+5XQ" id="form1">
<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="/wEPDwUJODExMDE5NzY5D2QWAgIDD2QWAgIBDw8WAh4EVGV4dAUMU0lNRCBBcmVhOiA0ZGRkXUm1+PLLKbrXDulhPdHkxpJgof6hEmrnSC3uCZiOeQ0=" />
    <div>
        <span id="simd">SIMD Area: 4</span>
    </div>
    </form>
</body>
</html>
'''

TODAYS_LOOKUPS = {} #{"IV1 1PP": "SIMD Area: 1"}

class ChildSmileDialog(BaseDialog):
    result = ""
    is_checking_website = False
    def __init__(self, parent):
        BaseDialog.__init__(self, parent)

        self.main_ui = parent
        self.header_label = QtGui.QLabel()
        self.header_label.setAlignment(QtCore.Qt.AlignCenter)
        self.pcde_le = UpperCaseLineEdit()
        self.pcde_le.setText(self.main_ui.pt.pcde)
        self.simd_label = QtGui.QLabel()
        self.header_label.setAlignment(QtCore.Qt.AlignCenter)

        self.tbi_checkbox = QtGui.QCheckBox(
            _("ToothBrushing Instruction Given"))
        self.tbi_checkbox.setChecked(True)

        self.di_checkbox = QtGui.QCheckBox(_("Dietary Advice Given"))
        self.di_checkbox.setChecked(True)

        self.fl_checkbox = QtGui.QCheckBox(_("Fluoride Varnish Applied"))
        self.fl_checkbox.setToolTip(
            _("Fee claimable for patients betwen 2 and 5"))
        self.fl_checkbox.setChecked(2 <= self.main_ui.pt.ageYears <=5)

        self.insertWidget(self.header_label)
        self.insertWidget(self.pcde_le)
        self.insertWidget(self.simd_label)
        self.insertWidget(self.tbi_checkbox)
        self.insertWidget(self.di_checkbox)
        self.insertWidget(self.fl_checkbox)

        self.pcde_le.textEdited.connect(self.check_pcde)

    @property
    def pcde(self):
        try:
            return str(self.pcde_le.text())
        except:
            return ""

    @property
    def valid_postcode(self):
        return bool(re.match("[A-Z][A-Z](\d+) (\d+)[A-Z][A-Z]", self.pcde))

    def postcode_warning(self):
        if not self.valid_postcode:
            QtGui.QMessageBox.warning(self, "error", "Postcode is not valid")

    def check_pcde(self):
        if self.valid_postcode:
            QtCore.QTimer.singleShot(50, self.simd_lookup)
        else:
            self.header_label.setText(_("Please enter a valid postcode"))
            self.simd_label.setText("")
            self.enableApply(False)

    def check_hung(self):
        '''
        this is called by a timout of the web polling
        '''
        if self.is_checking_website:
            QtGui.QApplication.instance().restoreOverrideCursor()
            QtGui.QMessageBox.warning(self, "error",
                "unable to poll NHS website")
            self.reject()
            return


    def simd_lookup(self):
        '''
        poll the server for a simd for a postcode
        '''
        global TODAYS_LOOKUPS
        try:
            self.result = TODAYS_LOOKUPS[self.pcde]
            self.simd_label.setText(self.result)
            self.enableApply(True)
            LOGGER.debug("simd_lookup unnecessary, value known")
            return
        except KeyError:
            pass
        try:
            self.is_checking_website = True
            QtCore.QTimer.singleShot(15000, self.check_hung)

            self.header_label.setText(_("Polling website with Postcode"))
            QtGui.QApplication.instance().setOverrideCursor(
                QtCore.Qt.WaitCursor)

            pcde = self.pcde.replace(" ", "%20")

            url = "%s?pCode=%s" %(LOOKUP_URL, pcde)

            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            result = response.read()
            self.result = self._parse_result(result)
            TODAYS_LOOKUPS[self.pcde] = self.result
            self.simd_label.setText(self.result)

            self.enableApply(True)
            self.is_checking_website = False
            QtGui.QApplication.instance().restoreOverrideCursor()
        except Exception as exc:
            LOGGER.exception("error polling NHS website?")
            QtGui.QApplication.instance().restoreOverrideCursor()
            QtGui.QMessageBox.warning(self, "error",
                "unable to poll NHS website")
            self.reject()

    def _parse_result(self, result):
        dom = minidom.parseString(result)
        e=dom.getElementsByTagName("span")[0]
        return e.firstChild.data

    @property
    def simd_number(self):
        return int(re.search("(\d+)", self.result).groups()[0])

    @property
    def tbi_performed(self):
        return self.tbi_checkbox.isChecked()

    @property
    def di_performed(self):
        return self.di_checkbox.isChecked()

    @property
    def fl_applied(self):
        return self.fl_checkbox.isChecked()

    @property
    def tx_items(self):
        age = self.main_ui.pt.ageYears
        dentist = localsettings.clinicianNo in localsettings.dentDict.keys()
        LOGGER.debug("Performed by dentist = %s"% dentist)
        if age < 3:
            if self.simd_number < 4:
                yield ("other", "CS1")
            else:
                yield ("other", "CS2")
            if self.tbi_performed:
                code = "TB1" if dentist else "TB2"
                yield ("other", code)
            if self.di_performed:
                code = "DI1" if dentist else "DI2"
                yield ("other", code)
        else:
            if self.simd_number < 4:
                yield ("other", "CS3")
            if self.tbi_performed:
                code = "TB3" if dentist else "TB4"
                yield ("other", code)
            if self.di_performed:
                code = "DI3" if dentist else "DI4"
                yield ("other", code)

        if 2 <= age <= 5:
            if self.fl_applied:
                yield ("other", "CSFL")


    def exec_(self):
        self.check_pcde()
        QtCore.QTimer.singleShot(100, self.postcode_warning)

        if BaseDialog.exec_(self):
            if self.valid_postcode:
                self.main_ui.pt.pcde = self.pcde

            self.main_ui.addNewNote("CHILDSMILE (postcode '%s'): %s"%
                (self.pcde, self.result))

            return True


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    def _mock_function(*args):
        pass
    from collections import namedtuple

    localsettings.initiate()
    app = QtGui.QApplication([])

    ui = QtGui.QMainWindow()
    ui.pt = namedtuple("pt",("pcde","ageYears"))

    ui.pt.pcde = "Iv1 1P"
    ui.pt.ageYears = 3
    ui.addNewNote = _mock_function

    dl = ChildSmileDialog(ui)
    #print dl._parse_result(EXAMPLE_RESULT)
    if dl.exec_():
        print (dl.result)
        print (dl.simd_number)
        print ("toothbrush instruction = %s"% dl.tbi_performed)
        print ("dietary advice = %s"% dl.di_performed)

        for item in dl.tx_items:
            print item