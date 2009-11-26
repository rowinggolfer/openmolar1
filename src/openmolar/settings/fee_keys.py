# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

from openmolar.settings import localsettings
import re

@localsettings.debug
def getKeyCode(arg):
    '''
    you pass a USERCODE (eg 'SP' for scale/polish...
    and get returned the numeric code for this
    class of treatments
    '''
    try:
        return localsettings.treatmentCodes[arg]
    except KeyError:
        #print "Caught error in fee_keys.getKeyCode with code '%s'"%arg
        return "4001" #other treatment!!

@localsettings.debug
def getItemFees(pt, itemcode, no_items=1):
    '''
    pass itemcode eg"0101", get a tuple (fee, ptfee)
    currently this gets the csetype from the pt coursetype.
    returns a tuple
    '''
    conditions = []
    if pt.cset == "N":
        if pt.exmpt != "":
            conditions.append("exempt=%s"% pt.exmpt)
    itemfee, ptfee = getFee(pt, itemcode, no_items, conditions)
    return itemfee, ptfee

@localsettings.debug
def getFee(pt, itemcode, no_items=1, conditions=[]):
    '''
    useage = getFee("P","4001")
    get the fee for itemcode "4001" for a private patient
    '''
    print "fee_keys.getFee called"
    fee,ptfee=0,0
    
    Exempt=False # this means pt doesn't get charged!!
    #-- presently conditions is just NHS stuff.
    for condition in conditions:
        if "exempt=" in condition:
            Exempt=True
            #print "Exemption - ",condition[condition.index("=")+1:]
            #print "Exmeption found warning - partial exemptions not handled"
            

    table = pt.getFeeTable()
    return table.getFees(itemcode, no_items, conditions)
    
    ### obsolete code for trimming
    '''
    if "N" in pt.cset:
        
        relevantNHSFeeDict = localsettings.getNHSFeescale(pt.accd)
        
        fee = relevantNHSFeeDict[itemcode].getFee(no_items, conditions)
        if not nhsExempt:
            ptfee = relevantNHSFeeDict[itemcode].getPtFee(no_items, conditions)
    
    elif "I" in pt.cset:
        fee = localsettings.FeesDict["P"][itemcode].getFee(no_items, conditions)
        ptfee = 0
    
    else:
        fee = localsettings.FeesDict["P"][itemcode].getFee(no_items, conditions)
        ptfee = fee
    
    return (fee, ptfee)
    '''

if __name__ == "__main__":
    localsettings.initiate(False)
    #for arg in ("CE","MOD","PV","Rt_upm"):
    #    print getKeyCode(arg)

    #pf=fee()
    #pf.description="small x-ray"
    #for fee in (990, 1500,2000, 395, 2800) :
    #    pf.addFee(fee)
    #pf.setRegulations("n=1:A,n=2:B,n=3:C,n>3:C+(n-3)*D,max=E")
    #print pf.getFee(5)

    #print getFee("P", "0101")
    #print getFee("N", "0101")
    
    
    ###########################this is to test tooth entry stuff
    while True:
        tooth=raw_input("Enter Tooth :")
        tooth=tooth.lower()
        input=raw_input("Enter Treatment for %s :"%tooth)
        if input=="exit":
            break
        items=itemsPerTooth(tooth, input)
        for item in items:
            code=getCode(item[0],item[1])
            description=getDescription(code)
            fee=getFee("P", code)
            print code,description,fee
