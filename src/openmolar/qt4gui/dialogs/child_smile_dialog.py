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
import socket
import urllib.request, urllib.error, urllib.parse
from xml.dom import minidom
from xml.parsers.expat import ExpatError

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar.settings import localsettings
from openmolar.qt4gui.customwidgets.upper_case_line_edit \
    import UpperCaseLineEdit
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

LOGGER = logging.getLogger("openmolar")

LOOKUP_URL = "http://www.psd.scot.nhs.uk/dev/simd/simdLookup.aspx"

# here is the result when using this

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

HEADERS = {
    'User-Agent': ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 '
                   '(KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'),
    'Accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'}

TODAYS_LOOKUPS = {}  # {"IV1 1PP": "SIMD Area: 1"}


class ChildSmileDialog(BaseDialog):
    result = ""
    is_checking_website = False

    def __init__(self, parent):
        BaseDialog.__init__(self, parent)

        self.main_ui = parent
        self.header_label = QtWidgets.QLabel()
        self.header_label.setAlignment(QtCore.Qt.AlignCenter)
        self.pcde_le = UpperCaseLineEdit()
        self.pcde_le.setText(self.main_ui.pt.pcde)
        self.simd_label = QtWidgets.QLabel()
        self.simd_label.setAlignment(QtCore.Qt.AlignCenter)

        self.tbi_checkbox = QtWidgets.QCheckBox(
            _("ToothBrushing Instruction Given"))
        self.tbi_checkbox.setChecked(True)

        self.di_checkbox = QtWidgets.QCheckBox(_("Dietary Advice Given"))
        self.di_checkbox.setChecked(True)

        self.fl_checkbox = QtWidgets.QCheckBox(_("Fluoride Varnish Applied"))
        self.fl_checkbox.setToolTip(
            _("Fee claimable for patients betwen 2 and 5"))
        self.fl_checkbox.setChecked(2 <= self.main_ui.pt.ageYears <= 5)

        self.insertWidget(self.header_label)
        self.insertWidget(self.pcde_le)
        self.insertWidget(self.simd_label)
        self.insertWidget(self.tbi_checkbox)
        self.insertWidget(self.di_checkbox)
        self.insertWidget(self.fl_checkbox)

        self.pcde_le.textEdited.connect(self.check_pcde)

        self._simd = None

    @property
    def pcde(self):
        try:
            return str(self.pcde_le.text())
        except:
            return ""

    @property
    def valid_postcode(self):
        return bool(re.match(r"[A-Z][A-Z]?(\d+) (\d+)[A-Z][A-Z]", self.pcde))

    def postcode_warning(self):
        if not self.valid_postcode:
            QtWidgets.QMessageBox.warning(self, "error",
                                          "Postcode is not valid")

    def check_pcde(self):
        if self.valid_postcode:
            QtCore.QTimer.singleShot(50, self.simd_lookup)
        else:
            self.header_label.setText(_("Please enter a valid postcode"))
            self.simd_label.setText("")
            self.enableApply(False)

    def simd_lookup(self):
        '''
        poll the server for a simd for a postcode
        '''
        QtWidgets.QApplication.instance().processEvents()
        global TODAYS_LOOKUPS
        try:
            self.result = TODAYS_LOOKUPS[self.pcde]
            self.simd_label.setText("%s %s" % (_("KNOWN SIMD"), self.result))
            self.enableApply(True)
            LOGGER.debug("simd_lookup unnecessary, value known")
            return
        except KeyError:
            pass

        self.header_label.setText(_("Polling website with Postcode"))

        pcde = self.pcde.replace(" ", "%20")

        url = "%s?pCode=%s" % (LOOKUP_URL, pcde)

        try:
            QtWidgets.QApplication.instance().setOverrideCursor(
                QtCore.Qt.WaitCursor)
            req = urllib.request.Request(url, headers=HEADERS)
            response = urllib.request.urlopen(req, timeout=20)
            result = response.read()
            self.result = self._parse_result(result)
            TODAYS_LOOKUPS[self.pcde] = "SIMD: %s" % self.simd_number
        except urllib.error.URLError:
            LOGGER.error("url error polling NHS website?")
            self.result = _("Error polling website")
        except socket.timeout:
            LOGGER.error("timeout error polling NHS website?")
            self.result = _("Timeout polling website")
        finally:
            QtWidgets.QApplication.instance().restoreOverrideCursor()

        self.simd_label.setText("%s = %s" % (_("RESULT"), self.result))
        QtWidgets.QApplication.instance().processEvents()

        self.enableApply(self.simd_number is not None)

        self.header_label.setText("SIMD %d" % self.simd_number)

    def _parse_result(self, result):
        try:
            dom = minidom.parseString(result)
            e = dom.getElementsByTagName("span")[0]
            return e.firstChild.data
        except ExpatError:
            return "UNDECIPHERABLE REPLY"

    def manual_entry(self):
        dl = QtWidgets.QInputDialog(self)
        dl.setWindowTitle(_("Manual Input Required"))
        dl.setInputMode(dl.IntInput)
        dl.setIntRange(1, 5)
        dl.setIntValue(4)
        dl.setLabelText(
            _("Online lookup has failed, please enter the SIMD manually"))
        self.rejected.connect(dl.reject)  # for Unittests
        if dl.exec_():
            self.reject()
            return
        simd = dl.intValue()
        self.result += " - Manually entered SIMD of %d" % simd
        return simd

    @property
    def simd_number(self):
        if self._simd is None:
            m = re.search("(\d+)", self.result)
            if m:
                self._simd = int(m.groups()[0])
            else:
                self._simd = 4
                self._simd = self.manual_entry()
        return self._simd

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
        is_dentist = \
            localsettings.clinicianNo in list(localsettings.dentDict.keys())
        LOGGER.debug("Performed by dentist = %s" % is_dentist)
        if age < 3:
            if self.simd_number < 4:
                yield ("other", "CS1")
            else:
                yield ("other", "CS2")
            if self.tbi_performed:
                code = "TB1" if is_dentist else "TB2"
                yield ("other", code)
            if self.di_performed:
                code = "DI1" if is_dentist else "DI2"
                yield ("other", code)
        else:
            if self.simd_number < 4:
                yield ("other", "CS3")
            if self.tbi_performed:
                code = "TB3" if is_dentist else "TB4"
                yield ("other", code)
            if self.di_performed:
                code = "DI3" if is_dentist else "DI4"
                yield ("other", code)

        if 2 <= age <= 5:
            if self.fl_applied:
                yield ("other", "CSFL")

    def exec_(self):
        QtCore.QTimer.singleShot(100, self.check_pcde)
        QtCore.QTimer.singleShot(500, self.postcode_warning)

        if BaseDialog.exec_(self):
            if self.valid_postcode:
                self.main_ui.pt.pcde = self.pcde
            self.main_ui.addNewNote(
                "CHILDSMILE (postcode '%s'): %s" % (self.pcde, self.result))
            return True
        return False


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)

    def _mock_function(*args):
        pass
    from collections import namedtuple

    localsettings.initiate()
    app = QtWidgets.QApplication([])

    ui = QtWidgets.QMainWindow()
    ui.pt = namedtuple("pt", ("pcde", "ageYears"))

    ui.pt.pcde = "Iv1 1P"
    ui.pt.ageYears = 3
    ui.addNewNote = _mock_function

    dl = ChildSmileDialog(ui)
    # print dl._parse_result(EXAMPLE_RESULT)
    if dl.exec_():
        print((dl.result))
        print((dl.simd_number))
        print(("toothbrush instruction = %s" % dl.tbi_performed))
        print(("dietary advice = %s" % dl.di_performed))

        for item in dl.tx_items:
            print(item)
