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

'''
this module is called when the schema is found to be out of date
'''

import sys
import time
from PyQt4 import QtGui, QtCore
from openmolar.settings import localsettings
from openmolar.dbtools import schema_version
    
    
def proceed():
    '''
    on to the main gui.
    '''
    from openmolar.qt4gui import maingui                
    sys.exit(maingui.main(sys.argv))

def logInAgainMessage():
    QtGui.QMessageBox.information(None, "Update Schema",
    "Success - Now please log in again to start openmolar")

def main(arg):
    '''
    main function
    '''
    app = QtGui.QApplication(arg)
    
    def updateProgress(arg, message):
        print message
        pb.setLabelText(message)
        pb.setValue(arg)
        app.processEvents()
        
    def completed(sucess, message):
        pb.hide()
        if sucess:
            QtGui.QMessageBox.information(pb, "Sucess", message)            
        else:
            QtGui.QMessageBox.warning(pb, "Failure",
            message +'''<br><br>
            Please File A bug by visiting<br>
            https://bugs.launchpad.net/openmolar''')
        
    required = localsettings.SCHEMA_VERSION
    current = schema_version.getVersion()
    message = '''<h3>Update required</h3>
    Your Schema is out of date.<br /> 
    You are at version %s, and %s is required.<br />
    Would you like to Upgrade Now?'''% (current, required)
    
    result = QtGui.QMessageBox.question(None, "Update Schema",
    message, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

    if result == QtGui.QMessageBox.Yes:
        pb = QtGui.QProgressDialog()
        pb.setWindowTitle("openMolar")
        pb.show()
        
        if current < "1.1":
            updateProgress(1,"upgrading to schema version 1.1")        
            from openmolar.schema_upgrades import schema1_0to1_1
            dbu = schema1_0to1_1.dbUpdater(pb)
        
            QtCore.QObject.connect(dbu, QtCore.SIGNAL("progress"), 
            updateProgress)

            QtCore.QObject.connect(dbu, QtCore.SIGNAL("completed"), 
            completed)
        
            if dbu.run():
                pb.hide()
                proceed()
            else:                
                completed(False, 'Conversion to 1.1 failed')
    else:
        QtGui.QMessageBox.warning(None, "Update Schema",
        "Please upgrade as soon as possible")        
        proceed()
    
if __name__ == "__main__":
    #-- put "openmolar" on the pyth path and go....
    print "starting schema_updater"
    
    def determine_path ():
        """Borrowed from wxglade.py"""
        try:
            root = __file__
            if os.path.islink (root):
                root = os.path.realpath (root)
            retarg = os.path.dirname (os.path.abspath (root))
            return retarg
        except:
            print "I'm sorry, but something is wrong."
            print "There is no __file__ variable. Please contact the author."
            sys.exit ()
            
    wkdir = determine_path()
    sys.path.append(os.path.dirname(wkdir))
    main(sys.argv)
