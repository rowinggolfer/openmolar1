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

import logging

from PyQt4 import QtCore
from openmolar import connect
from openmolar.dbtools import schema_version

LOGGER = logging.getLogger("openmolar")

class UpdateError(Exception):
    '''
    A custom exception. If this is thrown the db will be rolled back
    '''
    pass

class DatabaseUpdaterThread(QtCore.QThread):
    '''
    A class to update the openmolar database
    '''
    UpdateError = UpdateError
    progress_signal = QtCore.pyqtSignal(object, object)
    completed_signal = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super(DatabaseUpdaterThread, self).__init__(parent)
        self.message = "upating database"
        self.db = None
        self.cursor = None

    def run(self):
        '''
        function should be re-implemented
        '''
        raise self.update_error, \
        "DatabaseUpdateThread.run must be re-implemented"

    def completeSig(self, message):
        '''
        let the application know that the updater has finished
        '''
        self.completed_signal.emit(message)

    def progressSig(self, val, message=""):
        '''
        emits a signal showhing how we are proceeding.
        val is a number between 0 and 100
        '''
        if message != "":
            self.message = message
        self.progress_signal.emit(val, self.message)
        self.process_events()

    def process_events(self):
        '''
        if attached to a gui.. update the interface, else pass quietly
        '''
        try:
            QtCore.QCoreApplication.instance().processEvents()
        except AttributeError:
            pass

    def connect(self):
        if self.db is None:
            self.db = connect.connect()
            self.db.autocommit(False)
            self.cursor = self.db.cursor()

    def rollback(self):
        self.db.rollback()
        self.db.close()
        self.db=None

    def commit(self):
        self.db.commit()
        self.db.close()
        self.db=None

    def update_schema_version(self, compatible_versions, message):
        schema_version.update(compatible_versions, message)

    def execute_statements(self, sql_strings):
        '''
        execute the above commands
        NOTE - this function may fail depending on the mysql permissions
        in place
        '''
        self.connect()
        try:
            i, commandNo = 0, len(sql_strings)
            for sql_string in sql_strings:
                try:
                    self.cursor.execute(sql_string)
                except connect.GeneralError as exc:
                    if 1091 in exc.args:
                        LOGGER.warning(
                            "statement:'%s' threw column removal error - "
                            "continuing on assumption column is already "
                            "removed", sql_string.replace("\n", " "))
                    elif 1060 in exc.args:
                        LOGGER.warning(
                            "statement:'%s' threw column addition error - "
                            "continuing on assumption column is already "
                            "added", sql_string.replace("\n", " "))
                    elif 1061 in exc.args:
                        LOGGER.warning(
                            "statement:'%s' threw dupliacte key error - "
                            "continuing on assumption key is already "
                            "added", sql_string.replace("\n", " "))
                    else:
                        LOGGER.warning(
                            "FAILURE in executing sql statement \n%s",
                            sql_string)
                        raise exc
                self.progressSig(2 + 70 * i / commandNo,
                                "%s..." % sql_string[:10])
        except Exception:
            LOGGER.exception("FAILURE in executing sql statements")
            raise self.UpdateError("couldn't execute all statements!")

    def force_stop(self):
        LOGGER.warning("forcing DatabaseUpdaterThread stop")
        if self.isRunning() and self.cursor is not None:
            # by changing this attribute, execute statements
            # should die and rollback after an attribute error.
            self.cursor = None

if __name__ == "__main__":
    dbu = DatabaseUpdaterThread()
    dbu.run()
