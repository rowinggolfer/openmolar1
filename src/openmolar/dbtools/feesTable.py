# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import re, sys
from xml.dom import minidom

from openmolar.connect import connect
from openmolar.settings import localsettings

class feeTables():
    '''
    a wrapper class to contain as many fee tables as the user has outlined.
    '''
    def __init__(self):
        self.tables = {}
        self.getTables()
        self.loadTables()
        
    def __repr__(self):
        '''
        a readable description of the object
        '''
        retarg = "%d Tables \n"% len(self.tables)
        for key in self.tables:
            table = self.tables[key]
            retarg += "===" * 12 + "\n"
            retarg += "   table %s - %s\n"% (key, table.briefName)
            retarg += "%s \n"% table.description
            retarg += "valid %s - %s\n"% (
            localsettings.formatDate(table.startDate),
            localsettings.formatDate(table.endDate))
        
            retarg += "       categories %s\n"% table.categories
            retarg += "       fee cols %s\n"% str(table.feeColNames)
            retarg += "    pt_fee cols %s\n"% str(table.pt_feeColNames)            
            retarg += "       query %s\n"% table.columnQuery
            retarg += "===" * 12 + "\n"
        return retarg
    
    def getTables(self):
        '''
        get the key to our tables
        '''
        db = connect()
        cursor = db.cursor() 
        
        query = ''' select tablename, categories, description, startdate, 
        enddate, feecoltypes from feetable_key 
        where in_use = True order by display_order'''

        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        
        i = 0
        for (tablename, categories, description, startdate, endate,
        feecoltypes) in rows:
            ft = feeTable(tablename, i)
            ft.setCategories(categories)
            ft.setTableDescription(description)
            ft.setStartDate(startdate)
            ft.setEndDate(endate)
            ft.setFeeCols(feecoltypes)
            self.tables[i] = ft
            i += 1

    def loadTables(self):
        '''
        iterate through the child tables, and get them loaded
        '''
        for table in self.tables.values():
            table.loadFees()

class feeTable():
    '''
    a class to contain and allow quick access to data stored in a fee table
    '''
    def __init__(self, tablename, index):
        self.tablename = tablename
        self.briefName = tablename.replace("feetable_","")
        self.index = index
        self.feeColNames = ()
        self.pt_feeColNames = ()
        self.columnQuery = ""
        self.feesDict = {}
        self.categories = []
        self.hasPtCols = False
        self.treatmentCodes = {}
        self.feeColCount = 0
        
    def __repr__(self):
        '''
        a readable description of the object
        '''
        return "Class feeTable %s - %s feeItems"% (self.tablename, 
        len(self.feesDict))
        
    def setCategories(self, arg):
        '''
        the categories will be a list like "P", "PB" etc...
        '''
        cats = arg.split(",")
        self.categories = cats
        
    def setTableDescription(self, arg):
        '''
        a user friendly description of the table
        '''
        self.description = arg
    
    def setStartDate(self, arg):
        '''
        the date the feetable started (can be in the future)
        '''
        self.startDate = arg
    
    def setEndDate(self, arg):
        '''
        the date the feetable became obsolete (can be in the past)
        '''
        self.endDate = arg
    
    def setFeeCols(self, arg):
        '''
        arg is some xml logic to let me know what columns to query
        '''
        dom = minidom.parseString(arg)
        
        cols = dom.getElementsByTagName("column")
        self.feeColCount = len(cols)
        feeCol_list = []
        ptfeeCol_list = []
        for col in cols:
            colname = col.firstChild.data
            self.columnQuery += ", %s"% colname 
            if col.getAttribute("type") == "fee":
                feeCol_list.append(colname)
            else:
                ptfeeCol_list.append(colname)
                
        self.feeColNames = tuple(feeCol_list)
        self.pt_feeColNames = tuple(ptfeeCol_list)

        self.hasPtCols = not(len(self.pt_feeColNames)==0)
    
    def loadFees(self):
        '''
        now load the fees
        '''
        # build a query
        query = '''select section, code, USERCODE, regulation, description, 
brief_description, pl_cmp, hide %s from %s''' % (
        self.columnQuery, self.tablename)
        
        db = connect()
        cursor = db.cursor() 
                
        if localsettings.logqueries:
            print query
        cursor.execute(query)
        rows = cursor.fetchall()

        #create some blank tuples of the correct length
        feeTup = (0,) * len(self.feeColNames)
        ptfeeTup = (0,) * len(self.pt_feeColNames)

        for row in rows:
            (section, code, USERCODE, regulation, description, 
            brief_description, pl_cmp, hide) = row[:8]
            #unpack the fees into the blank tuples
            start, end = 8, 8 + len(feeTup)
            feeTup = row[start:end]
            start, end = end, end + len(ptfeeTup)            
            ptfeeTup = row[start:end]
            if code != "":
                if self.feesDict.has_key(code):
                    feeItem = self.feesDict[code] 
                else:
                    feeItem = feeItemClass(self, code)
                    feeItem.setCategory(section)
                    feeItem.setPl_Cmp_Type(pl_cmp)
                    feeItem.usercode = USERCODE
                    feeItem.description = description
                    feeItem.setRegulations(regulation)
                    self.feesDict[code] = feeItem
                feeItem.addFees(feeTup)
                feeItem.addPtFees(ptfeeTup)
                feeItem.addBriefDescription(brief_description)
                
            if USERCODE != "" and USERCODE != None:
                self.treatmentCodes[USERCODE] = code
    
    @localsettings.debug
    def getToothCode(self, tooth, arg):
        '''
        converts fillings into four digit codes used in the feescale
        eg "MOD" -> "1404" (both are strings)
        arg will be something like "CR,GO" or "MOD,CO"
        '''
        #print "decrypting tooth %s code %s "%(tooth, arg)

        if arg in ("PV","AP","ST","EX","EX/S1","EX/S2",",PR","DR","PX","PX+"):
            return self.getItemCodeFromUserCode(arg)

        if re.match("CR,..$", arg):
            #-- CR,V1 etc....
            return self.getItemCodeFromUserCode(arg)

        if re.match("RT",arg):
            if re.match("u.[45]",tooth):
                return self.getItemCodeFromUserCode("Rt_upm")
            if re.match("l.[45]",tooth):
                return self.getItemCodeFromUserCode("Rt_lpm")
            if re.match("..[123]",tooth):
                return self.getItemCodeFromUserCode("Rt_inc_can")
            if re.match("..[ABCDE]",tooth):
                return self.getItemCodeFromUserCode("dec_rct")            
            else:
                return self.getItemCodeFromUserCode("Rt_molar")

        if "PI/" in arg:
            return self.getItemCodeFromUserCode("Porc")

        if re.match("BR/P.*",arg):
            return self.getItemCodeFromUserCode(arg)

        if re.match("BR/CR,..$",arg):
            return self.getItemCodeFromUserCode(arg)

        if re.match("..[ABCDE]", tooth):
            return self.getItemCodeFromUserCode("dec_fill")            

        if re.match(".*GL.*",arg):
            return self.getItemCodeFromUserCode("Glfill")

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
            #return self.getItemCodeFromUserCode("%s-%ssurf"%(material,no_of_surfaces))
            return self.getItemCodeFromUserCode(
            "%s-%ssurf"%(material, no_of_surfaces))
        else:
            print '''no match in %s getToothCode for %s - %s"
            RETURNING '4001' '''% (self.tablename, tooth, arg)
            return "4001"
        
    @localsettings.debug
    def getItemCodeFromUserCode(self, arg):
        '''
        the table stores it's own usercodes now.
        return the itemcode associated with it, otherwise, return "4001"
        '''
        return self.treatmentCodes.get(arg,"4001")
    
    @localsettings.debug
    def hasItemCode(self, arg):
        '''
        check to see if the table contains a data about itemcode "arg"
        '''
        return arg in self.feesDict.keys()
    
    @localsettings.debug
    def getFees(self, itemcode, no_items=1, conditions=[], 
    no_already_in_estimate=0):
        '''
        returns a tuple of (fee, ptfee) for an item
        '''
        if self.hasItemCode(itemcode):
            if no_already_in_estimate == 0:
                return self.feesDict[itemcode].getFees(no_items, conditions)
            else:
                fee, ptfee = self.feesDict[itemcode].getFees(
                no_items+no_already_in_estimate, conditions) 
                
                offset, ptoffset = self.feesDict[itemcode].getFees(
                no_already_in_estimate, conditions) 
                
                return (fee - offset, ptfee - ptoffset) 
        else:
            print "itemcode %s not found in %s"% (itemcode, self.tablename)
            return (0,0)
    
    @localsettings.debug
    def getItemDescription(self, itemcode):
        '''
        returns the patient readable (ie. estimate ready) description of the
        item
        '''
        if self.hasItemCode(itemcode):
            return self.feesDict[itemcode].description
        else:
            return "No description for this item!"
    
    def getTxCategory(self, itemcode):
        '''
        tries to categorise the treatment (BETA FOR NOW)
        '''
        i = 0
        if self.hasItemCode(itemcode):
            i = self.feesDict[itemcode].category
        
        try:
            return ("other","exam", "diagnosis", "perio", 
            "tooth", "surgery", "prosthetics", "ortho") [i]
        except IndexError:
            return "other"
    
    @localsettings.debug    
    def userCodeWizard(self, usercode, n_items=1):
        '''
        send a usercode, get a results set
        (item (string), fee (int), ptfee (int), description (string))
        where description is the estimate ready description of the item
        '''
        item = self.getItemCodeFromUserCode(usercode)
        fee, ptfee = self.getFees(item, n_items)
        description = self.getItemDescription(item)
    
        return (item, fee, ptfee, description)
    
    @localsettings.debug        
    def toothCodeWizard(self, tooth, usercode):
        '''
        send a usercode, get a results set
        (item (string), fee (int), ptfee (int), description (string))
        where description is the estimate ready description of the item
        '''
        item = self.getToothCode(tooth, usercode)
        fee, ptfee = self.getFees(item)
        description = "%s - %s"% (self.getItemDescription(item), tooth)
    
        return (item, fee, ptfee, description)
    
    
class feeItemClass(object):
    '''
    this class handles the calculation of fees
    part of the challenge is recognising the fact that
    2x an item is not necessarily
    the same as double the fee for a single item etc..
    '''
    def __init__(self, table, itemcode):
        '''
        initiate the class with the default settings for a private fee
        '''
        self.table = table
        self.itemcode = itemcode
        self.category = 0
        self.pl_cmp_type = "other"
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
        return '''
feesTable.feeItem object
table, Item           =  %s   %s 
category, usercode    =  %s, '%s'
pl_cmp_type           =  %s,
brief description(s)  = '%s'
estimate phrase       = '%s'
regulations           = '%s'
fees                  =  %s
ptFees                =  %s'''% (self.table.tablename, 
        self.itemcode, self.category, self.usercode, self.pl_cmp_type, 
        self.brief_descriptions, self.description, self.regulations, 
        self.fees, self.ptFees)
        
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
        
    def setCategory(self, arg):
        '''
        add a numeric category, which is later translated into diagnosis, 
        perio, chart etc...
        '''
        self.category = arg
        
    def setPl_Cmp_Type(self,arg):
        '''
        the fee needs to know where it would belong in the treatment plan,
        if added via an indirect method. default is "other"
        this is where the item would be inserted into the pt class
        eg "ul7pl" or "otherpl"
        use 'CHART' to indicate that a tooth needs to be specified.
        '''
        if arg:
            self.pl_cmp_type = arg
    
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

    def getFees(self, no_items=1, conditions=""):
        '''
        convenience wrapper for getFee function
        returns a tuple fee,ptfee
        '''
        fee = self.getFee(no_items,conditions)
        if "no_charge" in conditions:
            return (fee, 0)
                
        ptFee = self.getFee(no_items,conditions, True)
        
        if ptFee == None:
            return (fee, fee)
        else:
            return (fee, ptFee)
    
    def getFee(self, no_items=1,conditions="",patient=False):
        '''
        get a fee for x items of this type
        conditions allows some flexibility (eg conditions=lower premolar)
        '''

        ##todo - this is a holder for when I include multi column fee dicts
        KEY = 0

        if patient:
            if self.ptFees == {}:
                return None
            else:
                feeList=self.ptFees[KEY]
                #print "using patient feelist=", feeList
        else:
            feeList=self.fees[KEY]
            #print "using feelist=", feeList
        
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


##############################################################################
## below this line is code utilised by the adjuster.

def getTableNames():
    '''
    get table names to load into the feescale adjuster
    '''
    db = connect()
    cursor = db.cursor() 
    
    query = ''' select ix, tablename, categories, description, startdate, 
    enddate, feecoltypes from feetable_key order by ix'''

    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    
    return rows

def getFeeDictForModification(table):
    '''
    a comprehensive dictionary formed from the entire table in the database
    '''
    
    query = '''select column_name from information_schema.columns where  
    table_name = "%s"'''% table
    
    db = connect()
    cursor = db.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    header = []
    for row in rows:
        header.append(row[0])

    query = 'select * from %s'%table
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    
    return (header, rows)
    
def updateFeeTable(table, feeDict, changes, deletions):
    '''
    pass a feeDict, and update the existing table with it.
    '''
    print "applying changes to feeTable", changes
    try:
        db = connect()
        cursor = db.cursor()
        columnNo = len(feeDict[feeDict.keys()[0]])
        valuesString = "%s," * columnNo
        valuesString = valuesString.strip(",")
        
        delquery = "delete from %s"%table + " where ix = %s"
        
        query = "insert into %s values (%s)"% (table, valuesString)
            
        for key in changes:
            cursor.execute(delquery, key)
            print query, feeDict[key]
            cursor.execute(query, feeDict[key])

        for key in deletions:
            cursor.execute(delquery, key)
            
        cursor.close()        
        db.commit()
        return True
    except Exception, e:
        print "exception",e
        return False

if __name__ == "__main__":
    fts = feeTables()

    for table in fts.tables.values():
        print table.tablename
        for tx in ("CE","SP","SP+","SR F/F"):
            print "looking up %s"%tx
            code = table.getItemCodeFromUserCode(tx)
            print "got code %s, fee %s"% (code, table.getFees(code))
