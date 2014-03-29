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

def handle_ContractTab(om_gui):
    '''
    function to adjust gui depending on the tab viewable
    '''
    i = om_gui.ui.contract_tabWidget.currentIndex()
    if i == 0:
        pass
        #om_gui.advise("Private contract tab selected")
    if i == 1:
        om_gui.ui.contractHDP_label.setText(
        planDetails.toHtml(om_gui.pt.plandata))

    if i == 2:
        om_gui.ui.contractNHS_label.setText(
        nhsDetails.toHtml(om_gui.pt))
        om_gui.ui.exemption_lineEdit.setText(om_gui.pt.exemption)
        om_gui.ui.exempttext_lineEdit.setText(om_gui.pt.exempttext)

    if i == 3:
        pass
        #om_gui.advise("Other Dentist tab selected")

def changeContractedDentist(om_gui, inits):
    '''
    changes dnt1
    '''
    newdentist = localsettings.ops_reverse[str(inits)]
    if newdentist == om_gui.pt.dnt1:
        return
    if om_gui.pt.cset == "I":
        om_gui.advise("Let Highland Dental Plan know of this change", 1)
    elif om_gui.pt.cset == "N":
        om_gui.advise(
        "Get an NHS form signed to change the patients contract", 1)
    else:
        om_gui.advise("changed dentist to %s"% inits, 1)
    print "changing contracted dentist to ", inits
    om_gui.pt.dnt1 = newdentist
    om_gui.updateDetails()

def changeCourseDentist(om_gui, inits):
    '''
    changes dnt2
    '''
    newdentist = localsettings.ops_reverse[str(inits)]
    if newdentist == om_gui.pt.dnt2:
        return
    if om_gui.pt.dnt2 == 0 and newdentist == om_gui.pt.dnt1:
        return
    if om_gui.pt.cset == "N" and om_gui.pt.underTreatment:
        om_gui.advise(
        "think about getting some nhs forms signed for both dentists", 1)
    else:
        om_gui.advise("changed course dentist to %s"% inits, 1)

    print "changing course dentist to ", inits
    om_gui.pt.dnt2 = newdentist
    om_gui.updateDetails()

def changeCourseType(om_gui, cset):
    '''
    change cset
    '''
    om_gui.pt.cset = str(cset)
    om_gui.updateDetails()
    i = ["P", "I", "N"].index(om_gui.pt.cset[:1])
    om_gui.ui.contract_tabWidget.setCurrentIndex(i)
    #do this so that the table is reset at any lookup
    om_gui.pt.forget_fee_table()

def editNHScontract(om_gui):
    '''blank function which needs work'''
    om_gui.advise("edit NHS", 1)

def exemption_edited(om_gui):
    '''
    user has edited the exemption text fields
    '''
    om_gui.pt.exemption = str(om_gui.ui.exemption_lineEdit.text().toAscii())
    om_gui.pt.exempttext = str(
    om_gui.ui.exempttext_lineEdit.text().toAscii())
    if not om_gui.pt.checkExemption():
        om_gui.advise(_("erroneous exemption category entered"),1)
        om_gui.ui.exemption_lineEdit.setText(om_gui.pt.dbstate.exemption)
    om_gui.updateDetails()

def editPrivateContract(om_gui):
    '''blank function which needs work'''
    om_gui.advise("edit Private", 1)

def editHDPcontract(om_gui):
    '''blank function which needs work'''
    om_gui.advise("edit HDP", 1)

def editOtherContract(om_gui):
    '''blank function which needs work'''
    om_gui.advise("edit other Practitioner", 1)
