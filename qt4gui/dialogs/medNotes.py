# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui, QtCore

from openmolar.settings import localsettings

from openmolar.qt4gui.dialogs import Ui_medhist

def showDialog(Dialog,data):
    dl = Ui_medhist.Ui_Dialog()
    dl.setupUi(Dialog)
    if data!=():
        item=0
        for lineEdit in (
        dl.doctor_lineEdit,
        dl.doctorAddy_lineEdit,
        dl.curMeds_lineEdit,
        dl.pastMeds_lineEdit,
        dl.allergies_lineEdit,
        dl.heart_lineEdit,
        dl.lungs_lineEdit,
        dl.liver_lineEdit,
        dl.bleeding_lineEdit,
        dl.kidneys_lineEdit,
        dl.anaesthetic_lineEdit,
        dl.other_lineEdit
        ):
            lineEdit.setText(data[-1][item])
            item+=1
    if Dialog.exec_():
        return True


if __name__=="__main__":
    app=QtGui.QApplication([])
    Dialog = QtGui.QDialog()
    showDialog(Dialog,(("doctor","address","curmeds","pastmeds","allergies","heart","lungs","liver","bleeding","Kidneys",
    "ops","other"),))