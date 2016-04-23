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

'''
module provides one class - NewFeescaleDialog
'''

import os
import shutil

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from openmolar.settings.localsettings import RESOURCE_DIR
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog
from openmolar.dbtools.feescales import feescale_handler, FEESCALE_DIR
from openmolar.qt4gui.customwidgets.warning_label import WarningLabel

EXAMPLE_XML_PATH = os.path.join(
    RESOURCE_DIR, "feescales", "example_feescale.xml")


class NewFeescaleDialog(BaseDialog):
    '''
    A trivial dialog which gets the user to choose an item from a list
    '''

    def __init__(self, parent=None):
        BaseDialog.__init__(self, parent)
        self.ix = None
        self.setWindowTitle(_("New Feescale Dialog"))

        self.insertWidget(WarningLabel(
            _('Click Apply to create a new local feescale file'
              ' which can be modified and then inserted into the database')
        ))

        self.enableApply()

    def sizeHint(self):
        return QtCore.QSize(300, 300)

    @property
    def filename(self):
        assert self.ix is not None, "new feescale index not available"
        return "feescale_%d.xml" % self.ix

    @property
    def filepath(self):
        return os.path.join(FEESCALE_DIR(), self.filename)

    def exec_(self):
        if BaseDialog.exec_(self):
            self.ix = feescale_handler.next_insert_id
            shutil.copy(EXAMPLE_XML_PATH, self.filepath)
            return True
        return False


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    dl = NewFeescaleDialog()
    if dl.exec_():
        print(dl.ix)
        print(dl.filename)
