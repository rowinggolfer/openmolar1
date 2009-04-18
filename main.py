#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.

'''this module puts "openmolar" onto the python path, and starts the gui'''

import sys,os,hashlib
from PyQt4 import QtGui,QtCore

__version__ = "0.0.5 - 15th April 2009"
__build__= "N/A dev_machine"

class LoginError(Exception):pass

def main(app):
    wkdir=os.path.dirname(os.getcwd())
    sys.path.append(wkdir)
    from openmolar.qt4gui import Ui_startscreen
    from openmolar.settings import localsettings
    localsettings.__version__ = __version__
    localsettings.__build__ = __build__
    uninitiated=True
    
    def autoreception(arg):    #arg is a QString
        if arg.toLower()=="rec":
            dl.reception_radioButton.setChecked(True)
    
    while True:        
        Dialog = QtGui.QDialog()
        dl = Ui_startscreen.Ui_Dialog()
        dl.setupUi(Dialog)
        QtCore.QObject.connect(dl.user1_lineEdit,QtCore.SIGNAL("textEdited (const QString&)"),autoreception)
        if Dialog.exec_():
            try:
                pword=str(dl.password_lineEdit.text())
                s=hashlib.md5(hashlib.sha1(pword).hexdigest()).hexdigest()
                if s != '800b28e2f8f456bc9d7b0bf98b7c32ab':##end password check##
                    raise LoginError 
                if uninitiated:
                    localsettings.initiate(False)                                                  #this will attempt to connect to mysql server
                    uninitiated=False
            
                u1=dl.user1_lineEdit.text().toUpper()                                              #toUpper is a method of QString
                u2=dl.user2_lineEdit.text().toUpper()
                if not u1 in localsettings.allowed_logins:
                    raise LoginError
                if u2!="" and not u2 in localsettings.allowed_logins:
                    raise LoginError

                localsettings.successful_login=True                                                #allow the main program to run
                if dl.reception_radioButton.isChecked():
                    localsettings.station="reception"
                if u2=="":
                    localsettings.operator=str(u1)
                else:
                    localsettings.operator=str(u1+"/"+u2)
                from openmolar.qt4gui import maingui
                sys.exit(maingui.main(sys.argv))

            except LoginError:
                QtGui.QMessageBox.warning(Dialog,"Login Error","Incorrect<br />User/password<br />combination!<br />Please Try Again.")
        else:
            break
    app.closeAllWindows()

if __name__=="__main__":
    print "starting openMolar",__version__
    app=QtGui.QApplication(sys.argv)
    main(app)
