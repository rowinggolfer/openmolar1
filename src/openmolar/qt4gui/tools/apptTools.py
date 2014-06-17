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

import datetime

from openmolar.settings import localsettings
from openmolar.qt4gui.compiled_uis import Ui_apptTools
from openmolar.qt4gui.dialogs import apptOpenDay, block_wizard
from openmolar.dbtools import extend_books, db_settings


class apptTools(Ui_apptTools.Ui_MainWindow):

    def __init__(self, parent=None):
        self.parent = parent
        self.setupUi(parent)
        self.signals()

    def advise(self, arg, warning_level=1):
        '''
        inform the user of events -
        warning level0 = status bar only.
        warning level 1 advisory
        warning level 2 critical (and logged)
        '''
        if warning_level == 0:
            self.statusbar.showMessage(arg, 5000)  # 5000 milliseconds=5secs
        elif warning_level == 1:
            QtGui.QMessageBox.information(self.parent, _("Advisory"), arg)
        elif warning_level == 2:
            now = QtCore.QTime.currentTime()
            QtGui.QMessageBox.warning(self.parent, _("Error"), arg)
            #--for logging purposes
            print "%d:%02d ERROR MESSAGE" % (now.hour(), now.minute()), arg

    def openDay(self):
        print "openDay called"
        Dialog = QtGui.QDialog(self.parent)
        dl = apptOpenDay.apptDialog(Dialog)
        if dl.exec_():
            print "openDay returned True"
        else:
            print "openDay returned False"

    def extendBooks(self):
        print "extending books"

        message = "%s %s %s %s" % (_("Books Currently end on"),
                                   localsettings.formatDate(
                                   localsettings.BOOKEND), "<br />",
                                   _("extend the books now?"))

        result = QtGui.QMessageBox.question(self.parent, _("Confirm"),
                                            message, QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
                                            QtGui.QMessageBox.Yes)

        if result == QtGui.QMessageBox.No:
            return
        else:
            months, result = QtGui.QInputDialog.getInteger(self.parent,
                                                           _("Extend Books"), _("How many months?"))

        if result:

            newBookEnd = QtCore.QDate(
                localsettings.BOOKEND).addMonths(months).toPyDate()

            if extend_books.extend(localsettings.apptix.values(),
                                   localsettings.BOOKEND, newBookEnd):
                # now put this date into the settings database.

                db_format = "%s,%s,%s" % newBookEnd.timetuple()[:3]
                db_settings.insertData(
                    "bookend", db_format, localsettings.operator)

    def removeOld(self):
        '''
        throw the old diaries away now?
        '''
        print "removing old weeks"
        self.advise(_("not yet implemented"))

    def editWeeks(self):
        '''
        edit the working hours for a standard week for a dentist/hygenist
        '''
        print "editing weeks"
        self.advise(_("not yet implemented"))

    def blocks(self):
        '''
        insert blocks and appointments
        '''
        print "blocks called"
        Dialog = QtGui.QDialog(self.parent)
        dl = block_wizard.blocker(Dialog)
        Dialog.exec_()

    def signals(self):
        '''
        connect signals
        '''
        QtCore.QObject.connect(self.openDay_pushButton,
                               QtCore.SIGNAL("clicked()"), self.openDay)

        QtCore.QObject.connect(self.extendBook_pushButton,
                               QtCore.SIGNAL("clicked()"), self.extendBooks)

        QtCore.QObject.connect(self.editWeeks_pushButton,
                               QtCore.SIGNAL("clicked()"), self.editWeeks)

        QtCore.QObject.connect(self.removeOld_pushButton,
                               QtCore.SIGNAL("clicked()"), self.removeOld)

        QtCore.QObject.connect(self.blocks_pushButton,
                               QtCore.SIGNAL("clicked()"), self.blocks)

if __name__ == "__main__":
    localsettings.initiate()
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = apptTools(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
