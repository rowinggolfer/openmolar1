# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import sys
from xml.dom import minidom

from openmolar.connect import connect
from openmolar.settings import localsettings
from openmolar.settings import fee_keys

class feeTables():
    def __init__(self):
        self.tables = {}
        self.getTables()
        self.loadTables()
        
    def __repr__(self):
        retarg = []
        for table in self.tables.values():
            retarg.append(table.tablename)
        return str(retarg)
    
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
        for row in rows:
            ft = feeTable(row[0], i)
            ft.setCategories(row[1])
            ft.setDescription(row[2])
            ft.setStartDate(row[3])
            ft.setEndDate(row[4])
            ft.setFeeColTypes(row[5])
            self.tables[i] = ft
            i += 1

    def loadTables(self):
        '''
        iterate through the child tables, and get them loaded
        '''
        for table in self.tables.values():
            table.loadFees()

class feeTable():
    def __init__(self, tablename, index):
        self.tablename = tablename
        self.index = index
        self.feeColNames = []
        self.columnQuery = ""
        self.feesDict = {}
        self.categories = []
        
    def setCategories(self, arg):
        '''
        the categories will be a list like "P", "PB" etc...
        '''
        cats = arg.split(",")
        self.categories = cats
        
    def setDescription(self, arg):
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
    
    def setFeeColTypes(self, arg):
        '''
        arg is some xml logic to let me know what columns to query
        '''
        dom = minidom.parseString(arg)
        #print dom.toxml()
        
        self.feeColNames = []  ##TODO - parse the xmlfor this...
        self.columnQuery = "" ##TODO - parse the xmlfor this...
        
    def loadFees(self):
        '''
        now load the fees
        '''
        # build a query
        query = "select section, code, USERCODE, regulation, "
        query += "description, brief_description, hide , fee %s " % self.columnQuery
        query += "from %s"% self.tablename
        
        db = connect()
        cursor = db.cursor() 
                
        if localsettings.logqueries:
            print query
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows:
            code = row[1]
            #itemCodes.append(code)
            if code != "":
                if self.feesDict.has_key(code):
                    self.feesDict[code].addFee(row[7])
                else:
                    newFee = fee_keys.fee()
                    newFee.usercode = row[2]
                    newFee.description = row[5]
                    newFee.setRegulations(row[3])
                    newFee.addFee(row[7])
                    self.feesDict[code] = newFee

            #if usercode != "" and usercode != None:
            #    treatmentCodes[usercode] = code
                

    ######## this is the main focus of development for the 0.1.8 version


##############################################################################
## below this line is old code. 
## NW - 2009_11_08


private_only = False
nhs_only = False

newfeetable_Headers = "section,code,oldcode,USERCODE,regulation," + \
"description,description1,NF08,NF08_pt,NF09,NF09_pt,PFA"


def getFeeHeaders():
    return newfeetable_Headers.split(",")[1:]

def getFeeDict():
    '''
    returns a dictionary of lists of tuples (!)
    dict[section]=feedict
    feedict=[(code1,desc1,fees1),(code2,desc2,fees2)]
    '''
    option=""
    if private_only:
        option += "where PFA>0"
    elif nhs_only:
        option += "where (NF08>0 or NF09>0)"

    db=connect()
    cursor=db.cursor()
    
    query = 'select %s from newfeetable %s' % (
    newfeetable_Headers,option)

    cursor.execute(query)
    feescales = cursor.fetchall()
    cursor.close()

    sections={}

    for row in feescales:
        if not sections.has_key(row[0]):
            sections[row[0]]=[]
        sections[row[0]].append(row[1:])
    return sections

def getFeeDictForModification():
    '''
    a comprehensive dictionary formed from the entire table in the database
    '''
    global feeDict_dbstate
    db = connect()
    cursor = db.cursor()
    cursor.execute('select ix,%s from newfeetable'% newfeetable_Headers)
    rows = cursor.fetchall()
    cursor.close()
    #db.close()

    feeDict = {}

    for row in rows:
        feeDict[row[0]] = row
    
    return feeDict

def updateFeeTable(feeDict, changes):
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
        
        delquery = "delete from newfeetable where ix = %s"
        query = "insert into newfeetable (ix,%s) values (%s)"% (
        newfeetable_Headers, valuesString) 
            
        for key in changes:
            cursor.execute(delquery, key)
            print query, feeDict[key]
            cursor.execute(query, feeDict[key])

        cursor.close()        
        db.commit()
        return True
    except Exception, e:
        print "exception",e
        return False
    
def decode(blob):
    '''
    decode in blocks of 4 bytes - this is a relic from the old database
    '''
    i=0
    retlist=[]
    for i in range(0,len(blob),4):
        cost=struct.unpack_from('H',blob,i)[0]
        retlist.append(cost)
    return retlist


def feesHtml():
    return toHtml(getFees())

if __name__ == "__main__":
    ft = feeTables()
    print ft