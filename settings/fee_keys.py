# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from openmolar.settings import localsettings
import re

class prvFee():
    '''this class handles the calculation of private fees
    part of the challenge is recognising the fact that 2x an item is not necessarily
   the same as double the fee for a single item etc.. '''
    def __init__(self):
        '''initiate the class with the default settings for a private fee'''
        self.description=""
        self.numberPerCourse=0
        self.fees=[]
        self.regulations=""
    def addFee(self, arg):
        '''add a fee to the list of fees contained by this class
        frequently this list will have only one item'''
        self.fees.append(int(arg))
    def setRegulations(self, arg):
        '''pass a string which sets the conditions for applying fees to this treatment item'''
        self.regulations=arg
    def getFee(self, no_items=1):
        '''get a fee for x items of this type'''
        if self.regulations=="":
            return self.fees[0]*no_items
        else:
            #-- this is the "regulation" for small xrays
            #--  n=1:A,n=2:B,n=3:C,n>3:C+(n-3)*D,max=E
            fee=0

            #-- check for a direct hit
            directMatch=re.findall("n=%d:."%no_items,self.regulations)
            if directMatch:
                column=directMatch[0][-1]
                fee=self.fees[ord(column)-65]

            #--check for a greater than
            greaterThan=re.findall("n>\d", self.regulations)
            if greaterThan:
                print "greater than found ", greaterThan
                limit=int(greaterThan[0][2:])
                print "limit", limit
                if no_items>limit:
                    formula=re.findall("n>\d:.*,", self.regulations)[0]
                    formula=formula.strip(greaterThan[0]+":")
                    formula=formula.strip(",")
                    print "formula", formula
                    #--get the base fee
                    column=formula[0]
                    fee=self.fees[ord(column)-65]
                    #--add additional items fees
                    a_items=re.findall("\(n-\d\)",formula)[0].strip("()")
                    n_a_items=no_items-int(a_items[2:])
                    column=formula[-1]
                    fee+=n_a_items*self.fees[ord(column)-65]

            #-- if fee is still zero
            if fee==0:
                print "returning linear fee (n* singleItem Fee)"
                fee=self.fees[0]*no_items

            #check for a max amount
            max= re.findall("max=.",self.regulations)
            if max:
                column=max[0][-1:]
                maxFee=self.fees[ord(column)-65]
                if maxFee<fee:
                    fee=maxFee

            return fee


def itemsPerTooth(tooth,props):
    '''
    usage itemsPerTooth("ul7","MOD,CO,PR ")
    returns (("ul7","MOD,CO"),("ul7","PR"))
    '''
    treats=[]
    items=props.strip(" ").split(" ")
    for item in items:
        if re.match(".*,PR.*",props):
            treats.append((tooth,"PR"),)
            item=item.replace(",PR","")

        treats.append((tooth, item), )
    return treats

def getKeyCode(arg):
    '''
    you pass a USERCODE (eg 'EX' for extraction... 
    and get returned the numeric code for this
    class of treatments
    '''
    try:
        return localsettings.treatmentCodes[arg]
    except Exception,e:
        #print "Caught error in fee_keys.getKeyCode with code '%s'"%arg
        return "4001" #other treatment!!


def getKeyCodeToothUserCode(tooth,arg):
    '''
    arg will be something like "CR,GO" or "MOD,CO"
    '''
    print "decrypting tooth code",arg


    if arg in ("PV","AP","RT","ST","EX","EX/S1","EX/S2"):
        return getKeyCode(arg)

    if arg in ("CR,GO","CR,V1","CR,A1","CR,RC","CR,OT","CR,V2"):
        return getKeyCode(arg)

        arg=arg.replace(",PR","")

    if "PI/" in arg:
        return getKeyCode("Porc")


    if re.match("BR/P.*",arg):
        return getKeyCode(arg)

    if re.match("BR/CR.*",arg):
        return getKeyCode(arg)

    if re.match("CR/.*",arg):
        return getKeyCode(arg)

    if re.match(".*GL.*",arg):
        return getKeyCode("GLfill")

    #-- ok... so it's probably a filling

    array=arg.split(",")

    #-- MOD
    #-- MOD,CO
    #-- MOD,PR
    #-- RT
    #-- PV


    if int(tooth[2])>3:
        default="AM"
    else:
        default="CO"

    if len(array)==1:
        surfaces=array[0]
        return getKeyCode("%s-%ssurf"%(default,len(surfaces)))   #-- AM-3surf etc..

    if len(array)==2:
        surfaces=array[0]
        material=array[1]
        return getKeyCode("%s-%ssurf"%(material,len(surfaces)))   #-- AM-3surf etc..


    print "no match in getKeyCodeToothUserCode for ",arg
    print "returning 4001"
    return "4001"


def toothSpecificCodesList(pt):
    '''
    cycles through the patient attriubutes,
    and brings up planned treatment on teeth only
    '''
    treats=[]
    for quadrant in ("ur","ul", "ll", "lr"):
        if "r" in quadrant:
            order=(8, 7, 6, 5, 4, 3, 2, 1)
        else:
            order=(1, 2, 3, 4, 5, 6, 7, 8)
        for tooth in order:
            att="%s%spl"%(quadrant, tooth)
            if pt.__dict__[att] != "":
                items=pt.__dict__[att].strip(" ").split(" ")
                for item in items:
                    treats.append(("%s%s"%(quadrant, tooth), item), )
    return treats

def getCode(tooth,fill):
    '''
    converts fillings into four digit codes used in the feescale
    eg "MOD" -> "1404" (both are strings)
    '''
    return getKeyCodeToothUserCode(tooth,fill)

def getFee(cset,itemcode):
    '''
    useage = getFee("P","4001")
    get the fee for itemcode "4001" for a private patient
    '''
    fee=0
    if "P" in cset:
        fee= localsettings.privateFees[itemcode].getFee()
    return fee

def getDescription(arg):
    '''
    usage=getDescription("4001")
    get a description for itemcode "4001"
    '''
    description=""
    try:
        description=localsettings.descriptions.get(arg)
    except:
        print "no description found for item %s"%arg
    return description


if __name__ == "__main__":
    #localsettings.initiate(False)
    #print localsettings.treatmentCodes
    #for arg in ("CE","MOD","PV"):
    #    print getKeyCode(arg)

    pf=prvFee()
    pf.description="small x-ray"
    for fee in (990, 1500,2000, 395, 2800) :
        pf.addFee(fee)
    pf.setRegulations("n=1:A,n=2:B,n=3:C,n>3:C+(n-3)*D,max=E")
    print pf.getFee(5)

