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
Provides a Class for printing the GP17s
Will raise dialogs etc to enable user choices.
'''
import os

from PyQt5 import QtWidgets

from openmolar.qt4gui.dialogs.gp17_printdialog import GP17PrintDialog
from openmolar.qt4gui.printing.om_printing import commitPDFtoDB


class GP17Printer(object):

    def __init__(self, om_gui):
        self.om_gui = om_gui

    def test_print(self):
        self.print_(test=True)

    def print_(self, final_paperwork=False, test=False):
        '''
        a GP17 is a scottish NHS form
        if test=True you also get boxes printed on the form
        (to check alignment)
        '''

        if final_paperwork and QtWidgets.QMessageBox.question(
                self.om_gui,
                _("Question"),
                _("Print an NHS form now?"),
                QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Yes,
                QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.No:
            return

        if test:  # self.om_gui.pt.serialno == 0:
            pt = None
        else:
            pt = self.om_gui.pt
        dl = GP17PrintDialog(pt, self.om_gui)

        dl.choose_form_widget.boxes_checkbox.setChecked(test)
        # chosenDent = str(dl.dents_comboBox.currentText())
        # dent = localsettings.ops_reverse.get(chosenDent)
        # form = GP17.gp17(self.om_gui.pt, dent, self.om_gui, test)
        if dl.exec_():
            for Form in dl.chosen_forms:
                form = Form()
                form.set_data(dl.data)
                form.printer.setDocName(form.NAME)
                form.set_testing_mode(dl.print_boxes)
                form.set_background_mode(dl.print_background)
                if form.controlled_print() and not test:
                    commitPDFtoDB(self.om_gui, form.NAME)

                    self.om_gui.pt.addHiddenNote(
                        "printed", "%s %s" % (form.NAME, dl.dent_inits))
                    self.om_gui.updateHiddenNotesLabel()


if __name__ == "__main__":
    from openmolar.settings import localsettings
    from openmolar.qt4gui import maingui
    from openmolar.dbtools import patient_class

    os.chdir(os.path.expanduser("~"))  # for save pdf

    localsettings.initiate()
    localsettings.station = "reception"  # prevent no clinician popup

    app = QtWidgets.QApplication([])

    om_gui = maingui.OpenmolarGui()

    om_gui.pt = patient_class.patient(2981)

    p = GP17Printer(om_gui)
    p.test_print()
