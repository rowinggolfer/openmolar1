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

import re
import urllib2
from xml.dom import minidom
from PyQt4 import QtGui, QtCore

if __name__ == "__main__":
    import os, sys
    sys.path.insert(0, os.path.abspath("../../../"))

from openmolar.settings import localsettings
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog

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


class ChildSmileDialog(BaseDialog):
    result = ""
    def __init__(self, parent):
        BaseDialog.__init__(self, parent)

        self.main_ui = parent
        QtCore.QTimer.singleShot(0, self.simd_lookup)
        self.header_label = QtGui.QLabel()
        self.header_label.setAlignment(QtCore.Qt.AlignCenter)
        self.pcde_le = QtGui.QLineEdit(self.main_ui.pt.pcde)
        self.simd_label = QtGui.QLabel()
        self.header_label.setAlignment(QtCore.Qt.AlignCenter)

        self.insertWidget(self.header_label)
        self.insertWidget(self.pcde_le)
        self.insertWidget(self.simd_label)

        self.check_pcde()
        self.pcde_le.editingFinished.connect(self.simd_lookup)

    @property
    def pcde(self):
        try:
            return str(self.pcde_le.text())
        except:
            return ""

    def check_pcde(self):
        if not re.match("[A-Z][A-Z](\d+) (\d+)[A-Z][A-Z]", self.pcde):
            self.header_label.setText(_("Please enter a valid postcode"))
            return False

        return True

    def simd_lookup(self):
        '''
        poll the server for a simd for a postcode
        '''
        self.header_label.setText(_("Polling website with Postcode"))
        if self.check_pcde():
            pcde = self.pcde.replace(" ", "%20")

            url = "%s?pCode=%s" %(LOOKUP_URL, pcde)

            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            result = response.read()
            self.result = self._parse_result(result)
            self.simd_label.setText(self.result)

            self.enableApply(True)
        else:
            QtGui.QMessageBox.warning(self, "error",
            "Postcode is not valid")


    def _parse_result(self, result):
        dom = minidom.parseString(result)
        e=dom.getElementsByTagName("span")[0]
        return e.firstChild.data

    @property
    def simd_number(self):
        return int(re.search("(\d+)", self.result).groups()[0])

    def exec_(self):
        if BaseDialog.exec_(self):
            if self.check_pcde():
                self.main_ui.pt.pcde = self.pcde

            self.main_ui.addNewNote("CHILDSMILE (postcode '%s'): %s"%
                (self.pcde, self.result))

if __name__ == "__main__":

    def _mock_function(*args):
        pass
    from collections import namedtuple

    localsettings.initiate()
    app = QtGui.QApplication([])

    ui = QtGui.QMainWindow()
    ui.pt = namedtuple("pt",("pcde",))

    ui.pt.pcde = "IV1 1P"
    ui.addNewNote = _mock_function

    dl = ChildSmileDialog(ui)
    #print dl._parse_result(EXAMPLE_RESULT)
    dl.exec_()
    print (dl.result)
    print (dl.simd_number)