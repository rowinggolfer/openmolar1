1# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from openmolar.settings import localsettings
import re

class fee():
    '''
    this class handles the calculation of fees
    part of the challenge is recognising the fact that
    2x an item is not necessarily
    the same as double the fee for a single item etc..
    '''
    def __init__(self):
        '''
        initiate the class with the default settings for a private fee
        '''
        self.description = ""
        self.brief_descriptions = ()
        self.fees = {}
        self.ptFees = {}
        self.regulations = ""
        self.usercode = ""
    
    def __repr__(self):
        '''
        a readable version of the instance
        '''
        return '''feeitem - Usercode    = '%s'
    brief description  = '%s'
    estimate phrase    = '%s'
    regulations        = '%s'
    fees               =  %s
    ptFees             =  %s'''% (self.usercode, self.brief_descriptions,
    self.description, self.regulations, self.fees, self.ptFees)
        
    def addFees(self, arg):
        '''
        add a fee to the list of fees contained by this class
        frequently this list will have only one item
        '''
        for i in range(len(arg)):
            try:
                val = int(arg[i])
            except TypeError, e:
                #print "error in your feetable, defaulting to zero fee!"
                val =0
            
            if self.fees.has_key(i):
                self.fees[i] += (val,)
            else:
                self.fees[i] = (val,)
                
    def addPtFees(self,arg):
        '''
        same again, but for the pt charge
        '''
        for i in range(len(arg)):
            try:
                val = int(arg[i])
            except TypeError, e:
                #print "error in your feetable, defaulting to zero fee!"
                val =0
            
            if self.ptFees.has_key(i):
                self.ptFees[i] += (val,)
            else:
                self.ptFees[i] = (val,)
        
    def addBriefDescription(self, arg):
        '''
        add a brief description
        '''
        self.brief_descriptions += (arg,)
            
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
