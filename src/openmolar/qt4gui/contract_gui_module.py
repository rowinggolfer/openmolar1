# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

'''
provides functions which act on the contract of the patient
at gui level
'''
from openmolar.settings import localsettings
from openmolar.ptModules import planDetails, nhsDetails

def handle_ContractTab(parent):
    '''
    function to adjust gui depending on the tab viewable
    '''
    i = parent.ui.contract_tabWidget.currentIndex()
    if i == 0:
        parent.advise("Private contract tab selected")
    if i == 1:
        parent.ui.contractHDP_label.setText(
        planDetails.toHtml(parent.pt.plandata))

    if i == 2:
        parent.ui.contractNHS_label.setText(
        nhsDetails.toHtml(parent.pt))

    if i == 3:
        parent.advise("Other Dentist tab selected")

def changeContractedDentist(parent, inits):
    '''
    changes dnt1
    '''
    newdentist = localsettings.ops_reverse[str(inits)]
    if newdentist == parent.pt.dnt1:
        return
    if parent.pt.cset == "I":
        parent.advise("Let Highland Dental Plan know of this change", 1)
    elif parent.pt.cset == "N":
        parent.advise(
        "Get an NHS form signed to change the patients contract", 1)
    else:
        parent.advise("changed dentist to %s"% inits, 1)
    print "changing contracted dentist to ", inits
    parent.pt.dnt1 = newdentist
    parent.updateDetails()

def changeCourseDentist(parent, inits):
    '''
    changes dnt2
    '''
    newdentist = localsettings.ops_reverse[str(inits)]
    if newdentist == parent.pt.dnt2:
        return 
    if parent.pt.dnt2 == 0 and newdentist == parent.pt.dnt1:
        return
    if parent.pt.cset == "N" and parent.pt.underTreatment:
        parent.advise(
        "think about getting some nhs forms signed for both dentists", 1)
    else: 
        parent.advise("changed course dentist to %s"% inits, 1)

    print "changing course dentist to ", inits
    parent.pt.dnt2 = newdentist
    parent.updateDetails()

def changeCourseType(parent, cset):
    '''
    change cset
    '''
    parent.pt.cset = str(cset)
    parent.updateDetails()
    i = ["P", "I", "N"].index(parent.pt.cset[:1])
    parent.ui.contract_tabWidget.setCurrentIndex(i)
    #do this so that the table is reset at any lookup
    parent.pt.feeTable = None 

def editNHScontract(parent):
    '''blank function which needs work'''
    parent.advise("edit NHS", 1)
    
def editPrivateContract(parent):
    '''blank function which needs work'''
    parent.advise("edit Private", 1)

def editHDPcontract(parent):
    '''blank function which needs work'''
    parent.advise("edit HDP", 1)

def editOtherContract(parent):
    '''blank function which needs work'''
    parent.advise("edit other Practitioner", 1)
