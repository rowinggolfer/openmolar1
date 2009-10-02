# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from PyQt4 import QtGui,QtCore
from openmolar.qt4gui.compiled_uis import Ui_payments

class paymentWidget(Ui_payments.Ui_Dialog,QtGui.QDialog):
    def __init__(self,parent=None):
        super(paymentWidget,self).__init__(parent)
        self.setupUi(self)
        self.defaultamount="0.00"
        QtCore.QObject.connect(self.buttonBox.button(QtGui.QDialogButtonBox.Apply),QtCore.SIGNAL("clicked()"),self.apply)
        QtCore.QObject.connect(self.cash_pushButton,QtCore.SIGNAL("clicked()"),self.defaultcash)
        QtCore.QObject.connect(self.cheque_pushButton,QtCore.SIGNAL("clicked()"),self.defaultcheque)
        QtCore.QObject.connect(self.debit_pushButton,QtCore.SIGNAL("clicked()"),self.defaultdebit)
        QtCore.QObject.connect(self.credit_pushButton,QtCore.SIGNAL("clicked()"),self.defaultcredit)

        for le in (self.cash_lineEdit,self.cheque_lineEdit,self.debitCard_lineEdit,self.creditCard_lineEdit,\
        self.sundries_lineEdit,self.annualHDP_lineEdit,self.misc_lineEdit):
            myValidator=QtGui.QDoubleValidator(0,8,2,le)
            #myValidator.setNotation(QtGui.QDoubleValidator.StandardNotation)                          #to disallow input like 1.00e76
            le.setValidator(myValidator)
            QtCore.QObject.connect(le,QtCore.SIGNAL("textEdited(QString)"),self.updateTotal)
            QtCore.QObject.connect(le,QtCore.SIGNAL("returnPressed()"),self.apply)                  ##todo - this isn't working becayse of the validator!!

    def setDefaultAmount(self,a):
        self.defaultamount="%d.%02d"%(a/100,a%100)

    def defaultcash(self):
        self.cash_lineEdit.setText(self.defaultamount)
        self.cheque_lineEdit.setText("")
        self.debitCard_lineEdit.setText("")
        self.creditCard_lineEdit.setText("")
        self.updateTotal("")
    def defaultcheque(self):
        self.cash_lineEdit.setText("")
        self.cheque_lineEdit.setText(self.defaultamount)
        self.debitCard_lineEdit.setText("")
        self.creditCard_lineEdit.setText("")
        self.updateTotal("")
    def defaultdebit(self):
        self.cash_lineEdit.setText("")
        self.cheque_lineEdit.setText("")
        self.debitCard_lineEdit.setText(self.defaultamount)
        self.creditCard_lineEdit.setText("")
        self.updateTotal("")
    def defaultcredit(self):
        self.cash_lineEdit.setText("")
        self.cheque_lineEdit.setText("")
        self.debitCard_lineEdit.setText("")
        self.creditCard_lineEdit.setText(self.defaultamount)
        self.updateTotal("")

    def updateTotal(self,a):
        '''updates the total box'''
        tot=float(0)
        try:
            for le in (self.cash_lineEdit,self.cheque_lineEdit,self.debitCard_lineEdit,self.creditCard_lineEdit):
                txt=le.text()
                if txt!="" and txt!="." :
                    tot += float(txt)
            self.paymentsForTreatment=tot
            tot2=float(0)
            for le in (self.sundries_lineEdit,self.annualHDP_lineEdit,self.misc_lineEdit):
                txt=le.text()
                if txt!="" and txt!="." :
                    tot2 += float(txt)
            self.otherPayments=tot2
            tot+=tot2
        except:
            print "whoops",
            tot=0
        self.total_doubleSpinBox.setValue(tot)

    def apply(self):
        '''check values'''
        self.updateTotal("")
        
        self.accept()
if __name__ == "__main__":
    def test(e):
        print e
    import sys
    app = QtGui.QApplication(sys.argv)
    
    if True:#to test the payment widget
        dl = paymentWidget()
        if dl.exec_():
            print "accepted treatment=%.02f, other=%.02f, total=%.02f"%(dl.paymentsForTreatment,dl.otherPayments,dl.total_doubleSpinBox.value())
        else:
            print "rejected"
    sys.exit(app.exec_())
