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
    
def proceed(app):
    '''
    on to the main gui.
    '''
    from openmolar.qt4gui import maingui                
    sys.exit(maingui.main(app))

def logInAgainMessage():
    QtGui.QMessageBox.information(None, "Update Schema",
    "Success - Now please log in again to start openmolar")

def main(arg, app):
    '''
    main function
    '''
    #app = QtGui.QApplication(arg)
    pb = QtGui.QProgressDialog()
        
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
            print "failure -",message
            QtGui.QMessageBox.warning(pb, "Failure", message )
            sys.exit("FAILED TO UPGRADE SCHEMA")
            app.closeAllWindows()
        
    required = localsettings.CLIENT_SCHEMA_VERSION
    current = schema_version.getVersion()
    message = _('''<h3>Update required</h3>
Your Openmolar database schema is out of date for this version of the client.
<br /> 
Your database is at version %s, and %s is required.<br />
Would you like to Upgrade Now?<br />
WARNING - PLEASE ENSURE ALL OTHER STATIONS ARE LOGGED OFF''')% (
    current, required)
    
    result = QtGui.QMessageBox.question(None, "Update Schema",
    message, QtGui.QMessageBox.No | QtGui.QMessageBox.Yes,
    QtGui.QMessageBox.Yes )
    
    if result == QtGui.QMessageBox.Yes:
        pb.setWindowTitle("openMolar")
        pb.show()

        try:
            ###################################################################
            ## UPDATE TO SCHEMA 1.1
            
            next_version = "1.1"                            
            if current < next_version:
                updateProgress(1,
                _("upgrading to schema version")+" %s"% next_version)        

                from openmolar.schema_upgrades import schema1_0to1_1 as upmod
                dbu = upmod.dbUpdater(pb)
            
                QtCore.QObject.connect(dbu, QtCore.SIGNAL("progress"), 
                updateProgress)

                QtCore.QObject.connect(dbu, QtCore.SIGNAL("completed"), 
                completed)
            
                if dbu.run():
                    localsettings.DB_SCHEMA_VERSION = next_version
                else:
                    completed(False, 
                    _('Conversion to %s failed')% next_version)
            
            ###################################################################
            ## UPDATE TO SCHEMA 1.2
            next_version = "1.2"                            
            if current < next_version:
                updateProgress(1,
                _("upgrading to schema version")+" %s"% next_version)        

                from openmolar.schema_upgrades import schema1_1to1_2 as upmod
                dbu = upmod.dbUpdater(pb)
            
                QtCore.QObject.connect(dbu, QtCore.SIGNAL("progress"), 
                updateProgress)

                QtCore.QObject.connect(dbu, QtCore.SIGNAL("completed"), 
                completed)
            
                if dbu.run():
                    localsettings.DB_SCHEMA_VERSION = next_version
                else:
                    completed(False, 
                    _('Conversion to %s failed')% next_version)
            
            ###################################################################
            ## UPDATE TO SCHEMA 1.3
            next_version = "1.3"                            
            if current < next_version:
                updateProgress(1,
                _("upgrading to schema version")+" %s"% next_version)        

                from openmolar.schema_upgrades import schema1_2to1_3 as upmod
                dbu = upmod.dbUpdater(pb)
            
                QtCore.QObject.connect(dbu, QtCore.SIGNAL("progress"), 
                updateProgress)

                QtCore.QObject.connect(dbu, QtCore.SIGNAL("completed"), 
                completed)
            
                if dbu.run():
                    localsettings.DB_SCHEMA_VERSION = next_version
                else:
                    completed(False, 
                    _('Conversion to %s failed')% next_version)
            
            ###################################################################
            ## UPDATE TO SCHEMA 1.4
            next_version = "1.4"                            
            if current < next_version:
                updateProgress(1,
                _("upgrading to schema version")+" %s"% next_version)        

                from openmolar.schema_upgrades import schema1_3to1_4 as upmod
                dbu = upmod.dbUpdater(pb)
            
                QtCore.QObject.connect(dbu, QtCore.SIGNAL("progress"), 
                updateProgress)

                QtCore.QObject.connect(dbu, QtCore.SIGNAL("completed"), 
                completed)
            
                if dbu.run():
                    localsettings.DB_SCHEMA_VERSION = next_version
                else:
                    completed(False, 
                    _('Conversion to %s failed')% next_version)
            
            ###################################################################
            ## UPDATE TO SCHEMA 1.5
            next_version = "1.5"                            
            if current < next_version:
                updateProgress(1,
                _("upgrading to schema version")+" %s"% next_version)        

                from openmolar.schema_upgrades import schema1_4to1_5 as upmod
                dbu = upmod.dbUpdater(pb)
            
                QtCore.QObject.connect(dbu, QtCore.SIGNAL("progress"), 
                updateProgress)

                QtCore.QObject.connect(dbu, QtCore.SIGNAL("completed"), 
                completed)
            
                if dbu.run():
                    localsettings.DB_SCHEMA_VERSION = next_version
                else:
                    completed(False, 
                    _('Conversion to %s failed')% next_version)

            ###################################################################
            ## UPDATE TO SCHEMA 1.6
            next_version = "1.6"                            
            if current < next_version:
                updateProgress(1,
                _("upgrading to schema version")+" %s"% next_version)        

                from openmolar.schema_upgrades import schema1_5to1_6 as upmod
                dbu = upmod.dbUpdater(pb)
            
                QtCore.QObject.connect(dbu, QtCore.SIGNAL("progress"), 
                updateProgress)

                QtCore.QObject.connect(dbu, QtCore.SIGNAL("completed"), 
                completed)
            
                if dbu.run():
                    localsettings.DB_SCHEMA_VERSION = next_version
                else:
                    completed(False, 
                    _('Conversion to %s failed')% next_version)
                   
            ###################################################################
            ## UPDATE TO SCHEMA 1.7
            next_version = "1.7"                            
            if current < next_version:
                updateProgress(1,
                _("upgrading to schema version")+" %s"% next_version)        

                from openmolar.schema_upgrades import schema1_6to1_7 as upmod
                dbu = upmod.dbUpdater(pb)
            
                QtCore.QObject.connect(dbu, QtCore.SIGNAL("progress"), 
                updateProgress)

                QtCore.QObject.connect(dbu, QtCore.SIGNAL("completed"), 
                completed)
            
                if dbu.run():
                    localsettings.DB_SCHEMA_VERSION = next_version
                else:
                    completed(False, 
                    _('Conversion to %s failed')% next_version)
                    
            ###################################################################
            ## UPDATE TO SCHEMA 1.8
            next_version = "1.8"                            
            if current < next_version:
                updateProgress(1,
                _("upgrading to schema version")+" %s"% next_version)        

                from openmolar.schema_upgrades import schema1_7to1_8 as upmod
                dbu = upmod.dbUpdater(pb)
            
                QtCore.QObject.connect(dbu, QtCore.SIGNAL("progress"), 
                updateProgress)

                QtCore.QObject.connect(dbu, QtCore.SIGNAL("completed"), 
                completed)
            
                if dbu.run():
                    localsettings.DB_SCHEMA_VERSION = next_version
                else:
                    completed(False, 
                    _('Conversion to %s failed')% next_version)
                    
                    
            else:
                completed(False,_(
'''<p>Sorry, we seem unable to update your schema at this point,
Perhaps you have grabbed a development version of the program?</p>
If so, please revert to a release version.<br />
If this is not the case, something odd has happened,
please let the developers of openmolar know ASAP.</p>'''))        
            
            pb.destroy()
            proceed(app)          
        
        
        except Exception, e:
            #fatal error!
            completed(False, 
            "<p>"+_('Unexpected Error updating the schema') 
            + "<br><br><b>%s</b></p><br><br>"% e + 
            _('Please File A bug by visiting ') +
            '<br>https://bugs.launchpad.net/openmolar')
            
    else:
        completed(False,  _('''<p>Sorry, you cannot run this version of the 
openmolar client without updating your database schema.</p>'''))        
    app.closeAllWindows()
    
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
    app = QtGui.QApplication(sys.argv)
    main(sys.argv, app)
