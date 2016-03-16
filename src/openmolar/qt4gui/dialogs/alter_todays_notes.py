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

from PyQt5 import QtCore, QtWidgets

from openmolar.settings import localsettings
from openmolar.qt4gui.dialogs.base_dialogs import BaseDialog
from openmolar.qt4gui.phrasebook.phrasebook_dialog import PhraseBookDialog

from openmolar import connect
from openmolar.dbtools import patient_write_changes
from openmolar.dbtools import db_patients

QUERY = '''select ix, note from formatted_notes
where serialno = %s and ndate=DATE(NOW()) and ntype ="newNOTE"
and op1 = %s and op2 = %s order by ix'''

UPDATE_QUERY = 'update formatted_notes set note=%s where ix=%s'

LOGGER = logging.getLogger("openmolar")


class AlterTodaysNotesDialog(BaseDialog):
    result = ""
    patient_loaded = True

    def __init__(self, sno, parent):
        BaseDialog.__init__(self, parent)
        self.sno = sno
        self.notes = []

        self.main_ui = parent
        QtCore.QTimer.singleShot(0, self.get_todays_notes)
        self.text_edit = QtWidgets.QTextEdit(self)

        self.patient_label = QtWidgets.QLabel("searching for patient...")

        phrasebook_button = QtWidgets.QPushButton(_("Open Phrasebook"))
        phrasebook_button.clicked.connect(self.show_phrasebook)

        self.insertWidget(self.patient_label)
        self.insertWidget(self.text_edit)
        self.insertWidget(phrasebook_button)
        # self.text_edit.setLineWrapMode(self.text_edit.FixedColumnWidth)
        # self.text_edit.setLineWrapColumnOrWidth(80)

        QtCore.QTimer.singleShot(0, self.get_patient_name)

    def sizeHint(self):
        return QtCore.QSize(800, 200)

    def get_patient_name(self):
        try:
            self.patient_label.setText(db_patients.name(self.sno))
        except localsettings.PatientNotFoundError as exc:
            QtWidgets.QMessageBox.warning(self, "Error", exc.message)

    def show_phrasebook(self):
        dl = PhraseBookDialog(self)
        if dl.exec_():
            note = "\n".join(dl.selectedPhrases)
            current = self.text_edit.toPlainText()
            pos = self.text_edit.textCursor().position()
            before = current[:pos]
            after = current[pos:]
            new_notes = "\n".join([s for s in (before.strip("\n"),
                                               note.strip("\n"),
                                               after.strip("\n")) if s])
            self.text_edit.setText(new_notes)

    def get_todays_notes(self):
        try:
            op1, op2 = localsettings.operator.split("/")
            query = QUERY
        except ValueError:
            op1 = localsettings.operator
            op2 = None
            query = QUERY.replace("op2 =", "op2 is")
        db = connect.connect()
        cursor = db.cursor()
        count = cursor.execute(query, (self.sno, op1, op2))
        rows = cursor.fetchall()
        cursor.close()

        if self.patient_loaded and not count:
            QtWidgets.QMessageBox.information(self, _("message"),
                                          _("No notes found for today!"))
            self.signals()
            return

        text = ""
        for ix, note in rows:
            self.notes.append((ix, note))
            if note.endswith("\n"):
                text += note
            else:
                text += "%s " % note.rstrip(" ")
        LOGGER.debug("'%s'", text)
        self.text_edit.setText(text.strip("\n "))
        self.signals()

    def signals(self):
        self.text_edit.textChanged.connect(self.item_edited)

    def item_edited(self):
        self.enableApply()

    def apply_changed(self):
        notes = str(self.text_edit.toPlainText()).rstrip(" \n")
        short_lines = list(patient_write_changes.note_splitter(notes, "\n"))

        LOGGER.debug(short_lines)
        values = []
        i = 0
        for ix, note in self.notes:
            try:
                values.append((short_lines[i], ix))
            except IndexError:  # a line has been deleted.
                values.append(("", ix))
            i += 1

        db = connect.connect()
        cursor = db.cursor()
        cursor.executemany(UPDATE_QUERY, values)
        cursor.close()

        if len(short_lines) > i:
            patient_write_changes.toNotes(
                self.sno,
                [("newNOTE", line) for line in short_lines[i:]]
                )

    def exec_(self):
        if BaseDialog.exec_(self):
            self.apply_changed()
            return True


if __name__ == "__main__":

    localsettings.initiate()
    localsettings.operator = "NW"
    app = QtWidgets.QApplication([])

    LOGGER.setLevel(logging.DEBUG)
    dl = AlterTodaysNotesDialog(11956, None)
    dl.exec_()
