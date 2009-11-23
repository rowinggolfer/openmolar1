# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

from openmolar.settings import localsettings
import re

class fee():
    '''
    DEPRECATED - MOVED to openmolar.dbtools
    this class handles the calculation of fees
    part of the challenge is recognising the fact that
    2x an item is not necessarily
    the same as double the fee for a single item etc..
    '''
    def __init__(self):
        '''
        initiate the class with the default settings for a private fee
        '''
        self.description=""
        self.numberPerCourse=0
        self.fees=[]
        self.ptFees=[]
        self.regulations=""
        self.usercode = ""
        
    def addFee(self, arg):
        '''
        add a fee to the list of fees contained by this class
        frequently this list will have only one item
        '''
        try:
            self.fees.append(int(arg))
        except TypeError, e:
            print "error in your feetable, defaulting to zero fee!"
            self.fees.append(0)
        
    def addPtFee(self,arg):
        '''
        same again, but for the pt charge
        '''
        try:
            self.ptFees.append(int(arg))
        except TypeError, e:
            print "error in your feetable, defaulting to zero fee!"
            self.ptFees.append(0)
            
    def setRegulations(self, arg):
        '''
        pass a string which sets the conditions for
        applying fees to this treatment item
        '''
        self.regulations=arg

    def getPtFee(self,no_items=1, conditions=""):
        return self.getFee(no_items,conditions, True)

    def getFee(self, no_items=1,conditions="",patient=False):
        '''
        get a fee for x items of this type
        conditions allows some flexibility (eg conditions=lower premolar)
        '''

        if patient:
            feeList=self.ptFees
            print "using patient feelist=", feeList

        else:
            feeList=self.fees
            print "using feelist=", feeList
            
        
        if self.regulations=="":
            return feeList[0]*no_items
        else:
            #-- this is the "regulation" for small xrays
            #--  n=1:A,n=2:B,n=3:C,n>3:C+(n-3)*D,max=E
            fee=0

            #-- check for a direct hit
            directMatch=re.findall("n=%d:."%no_items,self.regulations)
            if directMatch:
                column=directMatch[0][-1]
                fee=feeList[ord(column)-65]

            #--check for a greater than
            greaterThan=re.findall("n>\d", self.regulations)
            if greaterThan:
                #print "greater than found ", greaterThan
                limit=int(greaterThan[0][2:])
                #print "limit", limit
                if no_items>limit:
                    formula=re.findall("n>\d:.*,", self.regulations)[0]
                    formula=formula.strip(greaterThan[0]+":")
                    formula=formula.strip(",")
                    #print "formula", formula
                    #--get the base fee
                    column=formula[0]
                    fee=feeList[ord(column)-65]
                    #--add additional items fees
                    a_items=re.findall("\(n-\d\)",formula)[0].strip("()")
                    n_a_items=no_items-int(a_items[2:])
                    column=formula[-1]
                    fee+=n_a_items*feeList[ord(column)-65]

            #-- if fee is still zero
            if fee==0:
                #print "returning linear fee (n* singleItem Fee)"
                fee=feeList[0]*no_items

            #check for a max amount
            max= re.findall("max=.",self.regulations)
            if max:
                column=max[0][-1:]
                maxFee=feeList[ord(column)-65]
                if maxFee<fee:
                    fee=maxFee

            return fee



def itemsPerTooth(tooth,props):
    '''
    usage itemsPerTooth("ul7","MOD,CO,PR ")
    returns (("ul7","MOD,CO"),("ul7","PR"))
    '''
    treats=[]
    items=props.strip("() ").split(" ")
    for item in items:
        #--look for pins and posts
        if re.match(".*,PR.*",item):
            #print "removing .pr"
            treats.append((tooth,",PR"),)
            item=item.replace(",PR","")
        if re.match("CR.*,C[1-4].*",item):
            posts=re.findall(",C[1-4]",item)
            #print "making Post a separate item"
            for post in posts:
                treats.append((tooth,"CR%s"%post),)
            item=item.replace(post,"")

        treats.append((tooth, item), )
    return treats

def getKeyCode(arg):
    '''
    you pass a USERCODE (eg 'SP' for scale/polish...
    and get returned the numeric code for this
    class of treatments
    '''
    try:
        return localsettings.treatmentCodes[arg]
    except Exception,e:
        #print "Caught error in fee_keys.getKeyCode with code '%s'"%arg
        return "4001" #other treatment!!

def getCode(tooth,arg):
    '''
    converts fillings into four digit codes used in the feescale
    eg "MOD" -> "1404" (both are strings)
    arg will be something like "CR,GO" or "MOD,CO"
    '''
    #print "decrypting tooth %s code %s "%(tooth, arg)

    if arg in ("PV","AP","ST","EX","EX/S1","EX/S2",",PR","DR","PX","PX+"):
        return getKeyCode(arg)

    if re.match("CR,..$", arg):
        #-- CR,V1 etc....
        return getKeyCode(arg)

    if re.match("RT",arg):
        if re.match("u.[45]",tooth):
            return getKeyCode("Rt_upm")
        if re.match("l.[45]",tooth):
            return getKeyCode("Rt_lpm")
        if re.match("..[123]",tooth):
            return getKeyCode("Rt_inc_can")
        if re.match("..[ABCDE]",tooth):
            return getKeyCode("dec_rct")            
        else:
            return getKeyCode("Rt_molar")

    if "PI/" in arg:
        return getKeyCode("Porc")

    if re.match("BR/P.*",arg):
        return getKeyCode(arg)

    if re.match("BR/CR,..$",arg):
        return getKeyCode(arg)

    if re.match("..[ABCDE]", tooth):
        return getKeyCode("dec_fill")            

    if re.match(".*GL.*",arg):
        return getKeyCode("Glfill")

    #-- ok... so it's probably a filling
    #-- split off the material, and if not present, add one.
    array=arg.split(",")

    #-- MOD
    #-- MOD,CO


    #SET DEFAULT MATERIALS
    if len (array)>1:
        material=array[1]
    else:
        material=""

    if re.match("u.[4-8]",tooth):
        #--upper back tooth
        if material=="":
            material="AM"
        no_of_surfaces=len(re.findall("M|O|D|B|P",array[0]))
    elif re.match("l.[4-8]",tooth):
        #--lower back tooth
        if material=="":
            material="AM"
        no_of_surfaces=len(re.findall("M|O|D|B|L",array[0]))
    elif re.match("u.[1-3]",tooth):
        #-- upper anterior
        if material=="":
            material="CO"
        no_of_surfaces=len(re.findall("M|I|D|B|P",array[0]))
    else:
        #--lower anterior
        if material=="":
            material="CO"
        no_of_surfaces=len(re.findall("M|I|D|B|L",array[0]))
    
    if no_of_surfaces==len(array[0]):
        #-- to stop "MOV" being classed as an "MO"
        if no_of_surfaces>3:
            no_of_surfaces=3
        return getKeyCode("%s-%ssurf"%(material,no_of_surfaces))
    else:
        print "no match in getKeyCodeToothUserCode for ",tooth,arg,
        print "returning 4001"
        return "4001"


def getItemFees(pt, itemcode, no_items=1):
    '''
    pass itemcode eg"0101", get a tuple (fee, ptfee)
    currently this gets the csetype from the pt coursetype.
    returns a tuple
    '''
    conditions = []
    if pt.cset == "N":
        if pt.exmpt != "":
            conditions.append("NHS exempt=%s"% pt.exmpt)
    itemfee, ptfee = getFee(pt, itemcode, no_items, conditions)
    return itemfee, ptfee


def getFee(pt,itemcode, no_items=1, conditions=[]):
    '''
    useage = getFee("P","4001")
    get the fee for itemcode "4001" for a private patient
    '''
    print "fee_keys.getFee called"
    fee,ptfee=0,0
    nhsExempt=False
    #-- presently conditions is just NHS stuff.
    for condition in conditions:
        if "NHS exempt=" in condition:
            nhsExempt=True
            #print "Exemption - ",condition[condition.index("=")+1:]
            #print "Exmeption found warning - partial exemptions not handled"
            
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

if __name__ == "__main__":
    localsettings.initiate(False)
    #print localsettings.treatmentCodes
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
