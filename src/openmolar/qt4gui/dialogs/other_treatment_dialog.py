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
This module provides a dialog for chosing "other" items of treatment for a
patient.
'''

from gettext import gettext as _

from PyQt5 import QtCore, QtWidgets

from openmolar.settings import localsettings
from openmolar.qt4gui.dialogs.base_dialogs import ExtendableDialog


class _TreatmentItemWidget(QtWidgets.QWidget):
    '''
    A simple widget to display a treatment item
    '''
    def __init__(self, shortcut, item, description, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.shortcut = shortcut
        layout = QtWidgets.QHBoxLayout(self)
        self.spinbox = QtWidgets.QSpinBox()
        self.spinbox.setFixedWidth(80)
        self.label = QtWidgets.QLabel(description)
        # layout.setMargin(0)
        layout.addWidget(self.spinbox)
        layout.addWidget(self.label)


class OtherTreatmentDialog(ExtendableDialog):
    '''
    Make it easy for "other" items of treatment to tbe added to a treatment
    plan.
    '''
    def __init__(self, parent):
        ExtendableDialog.__init__(self, parent, remove_stretch=True)
        self.setWindowTitle(_("Other Treatment Choice Dialog"))
        label = QtWidgets.QLabel(_("Add the following items to the treament plan"))
        self.tab_widget = QtWidgets.QTabWidget(self)

        self.insertWidget(label)
        self.insertWidget(self.tab_widget)
        default_feetable = parent.pt.fee_table
        layouts = []
        for tabname in (default_feetable.briefName,
                        _("Items from other feescales")):
            tab = QtWidgets.QWidget()
            layouts.append(QtWidgets.QVBoxLayout(tab))
            scroll_area = QtWidgets.QScrollArea()
            scroll_area.setWidget(tab)
            scroll_area.setWidgetResizable(True)

            self.tab_widget.addTab(scroll_area, tabname)

        default_shortcuts = tuple(default_feetable.other_shortcuts)
        self.item_widgets = []
        for table, (att, shortcut) in \
                localsettings.FEETABLES.all_other_shortcuts:
            if table == default_feetable:
                layout = layouts[0]
            else:
                if (att, shortcut) in default_shortcuts:
                    continue
                layout = layouts[1]
            item = table.getItemCodeFromUserCode("%s %s" % (att, shortcut))
            item_description = table.getItemDescription(item, shortcut)
            item_widget = _TreatmentItemWidget(shortcut, item,
                                               item_description)
            layout.addWidget(item_widget)
            self.item_widgets.append(item_widget)

        self.enableApply()

    def sizeHint(self):
        return QtCore.QSize(400, 500)

    @property
    def chosen_treatments(self):
        '''
        what the user has selected
        '''
        for item_widg in self.item_widgets:
            number = item_widg.spinbox.value()
            if number != 0:
                for n in range(number):
                    yield ("other", item_widg.shortcut)


if __name__ == "__main__":
    from openmolar.dbtools.patient_class import patient
    localsettings.loadFeeTables()

    app = QtWidgets.QApplication([])
    mw = QtWidgets.QWidget()
    mw.pt = patient(17322)

    dl = OtherTreatmentDialog(mw)
    if dl.exec_():
        print(list(dl.chosen_treatments))
