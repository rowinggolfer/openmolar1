# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License 
# for more details.

from xml.dom import minidom
from openmolar.settings import localsettings

def getShortCuts():
    try:
        d = minidom.parse(localsettings.appt_shortcut_file)
        shortcuts = d.getElementsByTagName("shortcut")
        retarg = []
        for shortcut in shortcuts:
            shortCutDict = {}
            description = shortcut.getElementsByTagName("description")
            if description:
                shortCutDict["description"] = description[0].firstChild.data
            shortCutDict["appointments"]=[]
            appointments = shortcut.getElementsByTagName("appointment")
            for appointment in appointments:
                apptDict = {}
                clinician = appointment.getElementsByTagName("clinician")
                if clinician:
                    clinician_ = int(clinician[0].firstChild.data)
                    apptDict["clinician"] = clinician_
                trt1 = appointment.getElementsByTagName("trt1")
                if trt1:
                    trt = trt1[0].firstChild.data
                    apptDict["trt1"] = trt
                trt2 = appointment.getElementsByTagName("trt2")
                if trt2:
                    trt = trt2[0].firstChild.data
                    apptDict["trt2"] = trt
                trt3 = appointment.getElementsByTagName("trt3")
                if trt3:
                    trt = trt3[0].firstChild.data
                    apptDict["trt3"] = trt
                length = appointment.getElementsByTagName("length")
                if length:
                        a_length=int(length[0].firstChild.data)
                        apptDict["length"] = a_length
                datespec = appointment.getElementsByTagName("datespec")
                if datespec:
                        d_spec=int(length[0].firstChild.data)
                        apptDict["datespec"] = d_spec
                memo = appointment.getElementsByTagName("memo")
                if memo:
                        memo_=int(length[0].firstChild.data)
                        apptDict["memo"] = memo_
                
                shortCutDict["appointments"].append(apptDict)
            retarg.append(shortCutDict)
        return retarg
    
    except IOError, e:
        print "error getting appointment shortcuts",
        print localsettings.appt_shortcut_file
        #-- return an iterable variable
        return ()
        
if __name__ == "__main__":
    localsettings.initiate()
    localsettings.appt_shortcut_file = \
    "/home/neil/openmolar/openmolar/resources/appointment_shortcuts.xml"
    print getShortCuts()
