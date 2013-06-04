# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the GNU General Public License for more details.

import inspect
import logging
import re
import sys
from xml.dom import minidom

from openmolar import connect
from openmolar.settings import localsettings
from openmolar.ptModules import plan

try:
    from collections import OrderedDict
except ImportError:
    #OrderedDict only came in python 2.7
    print "using openmolar.backports for OrderedDict"
    from openmolar.backports import OrderedDict


logging.basicConfig(level=logging.DEBUG)

def getData():
    '''
    connects and get the data from feetable_key
    '''
    db = connect.connect()
    cursor = db.cursor()

    query = ''' select tablename, categories, description, startdate,
    enddate, feecoltypes, data from feetable_key
    where in_use = True order by display_order'''

    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    return rows

def saveData(tablename, data):
    '''
    update the database with the new xml data
    '''
    db = connect.connect()
    cursor = db.cursor()
    query = "update feetable_key set data=%s where tablename = %s"

    values = (data, tablename)
    if localsettings.logqueries:
        print query
        print values[0][:30]
        print values[1]
    result = cursor.execute(query, values)
    if result:
        db.commit()
    return result

def isParseable(data):
    '''
    takes a string, tries to parse it.
    '''
    try:
        d = minidom.parseString(data)
        d.toxml()
        d.unlink
    except Exception, e:
        return (False, str(e))
    return (True, "")

def getListFromNode(node, id):
    '''
    get the text data from the first child of any such nodes
    '''
    nlist = node.getElementsByTagName(id)
    values = []
    for n in nlist:
        children = n.childNodes
        for child in children:
            values.append(child.data.strip())
    return values

def getFeesFromNode(node, id):
    '''
    get the text data from the first child of any such nodes
    '''
    nlist = node.getElementsByTagName(id)
    values = []
    for n in nlist:
        sublist=[]
        children = n.childNodes
        for child in children:
            for n in child.data.split(","):
                sublist.append(int(n))
        values.append(tuple(sublist))
    return tuple(values)

def getTextFromNode(node, id):
    '''
    get the text data from the first child of any such nodes
    '''
    nlist = node.getElementsByTagName(id)
    value = ""
    for n in nlist:
        children = n.childNodes
        for child in children:
            value += child.data.strip()
    return value

def getBoolFromNode(node, id):
    '''
    get the text data from the first child of any such nodes
    '''
    return getTextFromNode(node, id) == "True"

class feeTables():
    '''
    a wrapper class to contain as many fee tables as the user has outlined.
    '''
    
    def __init__(self):
        self.tables = {}
        self.warnings = []
        self.default_table = None
        defaulttableno = self.getTables()
        self.default_table = self.tables[defaulttableno]
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
        rows = getData()
        i = 0
        defaulttableno = -1
        for (tablename, categories, description, startdate, enddate,
        feecoltypes, data) in rows:
            ft = feeTable(tablename, i)
            ft.setCategories(categories)
            ft.setTableDescription(description)
            ft.setStartDate(startdate)
            ft.setEndDate(enddate)
            ft.setFeeCols(feecoltypes)
            ft.setData(data)
            self.tables[i] = ft

            if defaulttableno == -1:
                if ("P" in ft.categories and
                startdate <= localsettings.currentDay() and
                (enddate == None or enddate > localsettings.currentDay())):
                    defaulttableno = i
            i += 1
        if defaulttableno == -1:
            print "WARNING - NO DEFAULT FEE TABLE FOUND!"
            defaulttableno = 0
        return defaulttableno

    def loadTables(self):
        '''
        iterate through the child tables, and get them loaded
        '''
        for table in self.tables.values():
            try:
                table.loadFees()
            except Exception,e:
                message = (table.tablename + _("Failed to Load") + 
                "<br /><pre>%s</pre>"% e)

                print message
                self.warnings.append(message)
    
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
        self.chartTreatmentCodes = OrderedDict()
        self.feeColCount = 0
        self.data = ""
        self.pl_cmp_Categories = plan.tup_Atts + ("CHART",)
        self.dirty = False  # a boolean which indicates whether the table
                            #is in db state

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

    def setData(self, data):
        '''
        data is the xml string pulled from the database.
        '''
        self.data = data

    def getData(self, data):
        return self.data

    def saveDataToDB(self):
        '''
        if the feetable has been altered, this will save the changes
        '''
        dom = minidom.parseString(self.data)
        newdata = dom.toxml()
        dom.unlink()

        result = saveData (self.tablename, newdata)
        if result:
            self.dirty = False
        return result

    def alterItem(self, item, nodexml):
        '''
        update an Item
        '''
        dom = minidom.parseString(self.data)
        nodeList = dom.getElementsByTagName("item")

        newnode = minidom.parseString(nodexml)
        for node in nodeList:
            codes = node.getElementsByTagName("code")
            for code in codes:
                if code.firstChild.data.strip() == item.itemcode:
                    node.parentNode.replaceChild(newnode.firstChild, node)
                    newdata = dom.toxml()
                    if self.data != newdata:
                        self.dirty = True
                        self.data = newdata
                    dom.unlink()
                    return True

    def alterUserCodeOnly(self, foreign_item):
        '''
        the user has edited the usercode of an item with the same key
        but from a different table
        '''
        dom = minidom.parseString(self.data)
        nodeList = dom.getElementsByTagName("item")
        result = False
        for node in nodeList:
            codes = node.getElementsByTagName("code")
            for code in codes:
                if code.firstChild.data.strip() == foreign_item.itemcode:
                    uc_node = node.getElementsByTagName("USERCODE")[0]
                    if uc_node.firstChild:
                        uc_node.firstChild.replaceWholeText(
                        foreign_item.usercode)
                    else:
                        uc_node.appendChild(
                        dom.createTextNode(foreign_item.usercode))

                    newdata = dom.toxml().encode("utf-8")

                    if self.data != newdata:
                        self.data = newdata
                        self.dirty = True
                        result = True
                    dom.unlink()
                    return result
        dom.unlink()

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

        dom.unlink()

    def loadFees(self):
        '''
        now load the fees
        '''
        dom = minidom.parseString(self.data)

        items = dom.getElementsByTagName("item")
        for item in items:
            code = getTextFromNode(item, "code")
            feeItem = feeItemClass(self, code)
            feeItem.from_xml(item)

            if feeItem.usercode != "":
                self.treatmentCodes[feeItem.usercode] = code
                if feeItem.pl_cmp_type == "CHART":
                    self.chartTreatmentCodes[feeItem.usercode] = code

            self.feesDict[code] = feeItem

        dom.unlink()

    def getToothCode(self, tooth, arg):
        '''
        converts fillings into four digit codes used in the feescale
        eg "MOD" -> "1404" (both are strings)
        arg will be something like "CR,GO" or "MOD,CO"
        '''

        if arg in self.chartTreatmentCodes.keys(): #direct match!!
            return self.getItemCodeFromUserCode(arg)

        try:
            for key in self.chartTreatmentCodes:
                match = key == arg
                if key.startswith("reg "):
                    match = re.match(key[4:], tooth+arg)
                if key.startswith("multireg "):
                    regexes = key[9:].split(" _AND_ ")
                    match = bool(regexes)
                    for regex in regexes:
                        if not re.match(regex, tooth+arg):
                            match = False
                            break
                if match:
                    return self.chartTreatmentCodes[key]
        except Exception, e:
            print e
            print key, self.chartTreatmentCodes[key]

        logging.warning(
            'no match in %s getToothCode for %s - %s RETURNING 4001'% (
            self.tablename, tooth, arg))

        return ""


    def getItemCodeFromUserCode(self, arg):
        '''
        the table stores it's own usercodes now.
        return the itemcode associated with it, otherwise, return "4001"
        '''
        return self.treatmentCodes.get(arg,"4001")


    def hasItemCode(self, arg):
        '''
        check to see if the table contains a data about itemcode "arg"
        '''
        return arg in self.feesDict.keys()


    def getFees(self, itemcode, no_items=1, conditions=[],
    no_already_in_estimate=None):
        '''
        returns a tuple of (fee, ptfee) for an item
        '''
        logging.debug('''looking up a fee for %d item(s) of code %s
where conditions are %s and %s similar items already in the estimate'''% (
        no_items, itemcode, conditions, no_already_in_estimate))

        if no_already_in_estimate is None:
            logging.warning("deprecated call to getFees")
            caller = inspect.stack()[1]
            logging.debug("module %s line %s\n   function %s\n    %s"% (
                caller[1], caller[2], caller[3], caller[4][0]))
            no_already_in_estimate = 0
            
        if self.hasItemCode(itemcode):
            if no_already_in_estimate ==0 :
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
            return self.pl_cmp_Categories[i]
        except IndexError:
            return "other"


    def userCodeWizard(self, usercode):
        '''
        send a usercode, get a results set
        (item (string), description (string))
        where description is the estimate ready description of the item
        '''
        item = self.getItemCodeFromUserCode(usercode)
        description = self.getItemDescription(item)

        return (item, description)

    def toothCodeWizard(self, tooth, usercode):
        '''
        send a usercode, get a results set
        (item (string), description (string))
        where description is the estimate ready description of the item
        '''
        item = self.getToothCode(tooth, usercode)
        if item != "":
            description = "%s - %s"% (self.getItemDescription(item), tooth)
        else:
            description = "other treatment"
        return (item, description)


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
        self.oldcode = ""
        self.category = 0
        self.pl_cmp_type = "other"
        self.description = ""
        self.depth = 1  # depth will be > 1 if a non-linear regulation
        self.brief_descriptions = ()
        self.fees = ()
        self.ptFees = ()
        self.multiples = False # is there complex fee logic behind this item?
        self.regulations = ""
        self.usercode = ""
        self.hide = False

    def get_stored_xml(self):
        '''
        get the xml node the feeitem represents
        '''
        dom = minidom.parseString(self.table.data)
        nodeList = dom.getElementsByTagName("item")
        for node in nodeList:
            codes = node.getElementsByTagName("code")
            for code in codes:
                if code.firstChild.data.strip() == self.itemcode:
                    retarg = node.toxml()
                    dom.unlink()
                    return retarg
        return _("not found")

    def from_xml(self, item):
        section = getTextFromNode(item, "section")
        oldcode = getTextFromNode(item, "oldcode")
        USERCODE = getTextFromNode(item, "USERCODE")
        
        for reg in item.getElementsByTagName("regulation"):
            self.multiples = reg.getAttribute("type")=="multiple"
            regulation = getTextFromNode(item, "regulation")
            self.setRegulations(regulation)
        
        description = getTextFromNode(item, "description")
        brief_descriptions = getListFromNode(item, "brief_description")
        pl_cmp = getTextFromNode(item, "pl_cmp")
        hide = getBoolFromNode(item, "hide")

        fees = getFeesFromNode(item, "fee")
        if self.table.hasPtCols:
            ptfees = getFeesFromNode(item, "pt_fee")
        else:
            ptfees = ()

        self.setCategory(int(section))
        self.setPl_Cmp_Type(pl_cmp)
        self.usercode = USERCODE
        self.oldcode = oldcode
        self.description = description
        self.hide = hide
        self.addFees(fees)
        self.addPtFees(ptfees)
        self.depth = len(fees)
        for bd in brief_descriptions:
            self.addBriefDescription(bd)


    def to_xml(self, pretty=False):
        '''
        convert the current object to an xml representation
        '''
        dom = minidom.Document()
        item = dom.createElement("item")

        n = dom.createElement("section")
        n.appendChild(dom.createTextNode(str(self.category)))
        item.appendChild(n)

        n = dom.createElement("code")
        n.appendChild(dom.createTextNode(self.itemcode))
        item.appendChild(n)

        n = dom.createElement("oldcode")
        n.appendChild(dom.createTextNode(self.oldcode))
        item.appendChild(n)

        n = dom.createElement("USERCODE")
        n.appendChild(dom.createTextNode(self.usercode))
        item.appendChild(n)

        n = dom.createElement("regulation")
        n.appendChild(dom.createTextNode(self.regulations))
        item.appendChild(n)

        n = dom.createElement("description")
        n.appendChild(dom.createTextNode(self.description))
        item.appendChild(n)

        for bdesc in self.brief_descriptions:
            n = dom.createElement("brief_description")
            n.appendChild(dom.createTextNode(bdesc))
            item.appendChild(n)

        n = dom.createElement("hide")
        val = "1" if self.hide else "0"
        n.appendChild(dom.createTextNode(val))
        item.appendChild(n)

        n = dom.createElement("pl_cmp")
        n.appendChild(dom.createTextNode(self.pl_cmp_type))
        item.appendChild(n)

        for fee in self.fees:
            f_string = str(fee).strip("(),")
            n = dom.createElement("fee")
            n.appendChild(dom.createTextNode(f_string))
            item.appendChild(n)

        for fee in self.ptFees:
            f_string = str(fee).strip("(),")
            n = dom.createElement("pt_fee")
            n.appendChild(dom.createTextNode(f_string))
            item.appendChild(n)

        dom.appendChild(item)

        if pretty:
            retarg = dom.toprettyxml()
            retarg = retarg.replace("\t", "    ")
        else:
            retarg = dom.toxml()
        dom.unlink()
        return retarg

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
        self.fees = arg

    def addPtFees(self,arg):
        '''
        same again, but for the pt charge
        '''
        self.ptFees = arg

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
        self.regulations = arg

    def getFees(self, no_items=1, conditions=""):
        '''
        convenience wrapper for getFee function
        returns a tuple fee,ptfee
        '''
        fee = self.getFee(no_items,conditions)
        if "no_charge" in conditions:
            return (fee, 0)

        ptFee = self.getFee(no_items, conditions, True)

        if ptFee == None:
            return (fee, fee)
        else:
            return (fee, ptFee)

    def getFee(self, no_items=1, conditions="", patient=False):
        '''
        get a fee for x items of this type
        conditions allows some flexibility (eg conditions=lower premolar)
        patient = True when you using a feescale with distinctly different
        patient values to the true fee (eg nhs)
        '''

        ##todo - this is a holder for when I include multi column fee dicts
        KEY = 0

        def getFeeList(fees):
            '''
            get a list of the KEYth column of fees
            '''
            retarg = []
            for feetuple in fees:
                retarg.append(feetuple[KEY])
            return retarg

        if patient:
            if self.ptFees == ():
                return None
            else:
                feeList = getFeeList(self.ptFees)
        else:
            feeList = getFeeList(self.fees)

        if self.regulations and not self.multiples:
            logging.warning(
            "TODO - apply regulation '%s'"% self.regulations)

        if not self.multiples:
            #linear charging x items = x * fee.
            return feeList[0] * no_items
        

        #-- this is the "regulation" for small xrays
        #--  n=1:A,n=2:B,n=3:C,n>3:C+(n-3)*D,max=E

        #--and here is the new one for the 2012 feescale
        #-- n=1:A,n=2:B,n=3:C,n>4:E

        logging.debug("applying multiple regulation '%s'"% self.regulations)

        regulations = self.regulations.split(',')
        max_fee = None
        found = False
        for regulation in regulations:

            m = re.match("max=([A-Z])", regulation)
            if m:
                max_fee = feeList[ord(m.groups()[0])-65]
                continue

            if found:
                continue

            logic, value = regulation.split(":")

            if re.search("[^>^<]=[^=]", logic):
                #can't simply use eval because n=5 is not n==5
                logic = logic.replace("=", "==")

            if eval(logic.replace("n", str(no_items))):
                logging.debug("match found with %s"% logic)
                if re.match("[A-Z]$", value):
                    fee = feeList[ord(value)-65]
                else:
                    eval_string = value.replace("n", str(no_items))
                    for cap in re.findall("[A-Z]", value):
                        eval_string = eval_string.replace(
                            cap, str(feeList[ord(cap)-65]))

                    logging.debug("Fee logic is '%s', evaluating '%s'"% (
                        value, eval_string))
                    fee = eval(eval_string)

                found = True

        if not found:
            logging.warning(
                "no match for fee regulations '%s'"% self.regulations)
            fee = feeList[0] * no_items

        if max_fee and max_fee < fee:
            logging.info("max fee reached for this fee code")
            fee = max_fee
        logging.debug("returning a fee of %s"% fee)
        return fee

if __name__ == "__main__":

    def check_codes():
        tx = str(dl.lineEdit.text().toAscii())
        print "checking",tx

        dl.dec_listWidget.clear()
        dl.adult_listWidget.clear()
        for tooth in decidmouth:
            if tooth != "***":
                code, desc = table.toothCodeWizard(tooth, tx.upper())
                result = "%s - %s %s"% (tooth.upper(), code, desc)
                dl.dec_listWidget.addItem(result)
        for tooth in mouth:
            code, desc = table.toothCodeWizard(tooth, tx.upper())
            result = "%s - %s %s"% (tooth.upper(), code, desc)
            dl.adult_listWidget.addItem(result)

    def showTable():
        dialog2 = QtGui.QDialog(Dialog)
        te = QtGui.QPlainTextEdit(dialog2)
        te.setMinimumSize(800,600)

        text = table.data.replace("</item>","</item>\n")
        text = text.replace("<item>","\n<item>")
        text = text.replace("><","> <")
        te.setPlainText(text)
        dialog2.show()

    def reloadTables():
        global table
        fts = feeTables()
        table = fts.tables[dl.comboBox.currentIndex()]

    def change_table(i):
        global table
        table = fts.tables[i]
        print "changed to ", table.tablename
        check_codes()

    fts = feeTables()

    table_list = []
    for table in fts.tables.values():
        print table.tablename
        table_list.append(table.tablename)

    def checkCommonItems():
        ## not called
        for tx in ("CE","S", "SP","SP+","SR F/F"):
            print "looking up %s"%tx
            code = table.getItemCodeFromUserCode(tx)
            print "got code %s, fee %s"% (
                code, table.getFees(code, no_already_in_estimate=0))

    checkCommonItems()

    from PyQt4 import QtGui, QtCore
    from openmolar.dbtools.patient_class import mouth, decidmouth
    from openmolar.qt4gui.compiled_uis import Ui_codeChecker
    app = QtGui.QApplication([])
    Dialog = QtGui.QDialog()
    dl = Ui_codeChecker.Ui_Dialog()
    dl.setupUi(Dialog)
    dl.comboBox.addItems(table_list)

    table = fts.tables[dl.comboBox.currentIndex()]

    Dialog.setWindowTitle(table.tablename)
    Dialog.connect(dl.pushButton, QtCore.SIGNAL("clicked()"), check_codes)
    Dialog.connect(dl.lineEdit, QtCore.SIGNAL("returnPressed()"), check_codes)
    Dialog.connect(dl.comboBox, QtCore.SIGNAL("currentIndexChanged (int)"),
        change_table)

    Dialog.exec_()
    app.closeAllWindows()
