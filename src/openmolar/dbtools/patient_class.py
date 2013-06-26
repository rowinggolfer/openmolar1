# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

from copy import deepcopy
import datetime
import sys

from openmolar import connect
from openmolar.ptModules import perio, dec_perm, estimates, notes, formatted_notes
from openmolar.settings import localsettings

from openmolar.dbtools.appt_prefs import ApptPrefs

dateFields = ("dob", "pd0", "pd1", "pd2", "pd3", "pd4", "pd5", "pd6",
"pd7", "pd8", "pd9", "pd10", "pd11", "pd12", "pd13", "pd14", "cnfd",
"recd", "billdate", "enrolled", "initaccept", "lastreaccept", "lastclaim",
"expiry", "transfer", "chartdate", "accd", "cmpd", "examd", "bpedate")

nullDate = None

patientTableAtts = (
'pf0','pf1','pf2','pf3','pf4','pf5','pf6','pf7','pf8','pf9','pf10','pf11',
'pf12','pf14','pf15','pf16','pf17','pf18','pf19',
'money0','money1','money2','money3','money4','money5','money6','money7',
'money8','money9','money10',
'pd0','pd1','pd2','pd3','pd4','pd5','pd6','pd7','pd8','pd9','pd10','pd11',
'pd12','pd13','pd14',
'sname','fname','title','sex','dob', 'addr1','addr2','addr3','pcde','tel1',
'tel2','occup',
'nhsno','cnfd','psn','cset','dnt1','dnt2','courseno0','courseno1',
'ur8st','ur7st','ur6st','ur5st','ur4st','ur3st','ur2st','ur1st',
'ul1st','ul2st','ul3st','ul4st','ul5st','ul6st','ul7st','ul8st',
'll8st','ll7st','ll6st','ll5st','ll4st','ll3st','ll2st','ll1st',
'lr1st','lr2st','lr3st','lr4st','lr5st','lr6st','lr7st','lr8st',
'dent0','dent1','dent2','dent3',
'dmask','minstart','maxend','billdate','billct',
'billtype','pf20','money11','pf13','familyno','memo',
'town','county','mobile','fax','email1','email2','status','source',
'enrolled','archived',
'initaccept','lastreaccept','lastclaim','expiry','cstatus','transfer',
'pstatus','courseno2')

exemptionTableAtts = ('exemption','exempttext')

patientTableVals=(
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,
nullDate, nullDate, nullDate, nullDate, nullDate, nullDate, nullDate,
nullDate, nullDate, nullDate, nullDate, nullDate, nullDate, nullDate,nullDate,
'','','','',nullDate,'','', '','', '','', '',
'',nullDate, '','',0,0,0,0,
'','', '','', '','', '','',
'','', '','', '','', '','',
'','', '','', '','', '','',
'','', '','', '','', '','',
0,0,0,0,
'YYYYYYY',0,0,nullDate,0,None,
0,0,0,0,'','',
'','','','','','','','',
nullDate,0,
nullDate,nullDate,nullDate,nullDate,0,nullDate,
0,0)

bpeTableAtts=('bpedate','bpe')
bpeTableVals=(nullDate,'',())

currtrtmtTableAtts=('courseno','xraypl','periopl','anaespl','otherpl',
'ndupl','ndlpl','odupl','odlpl',"custompl",
'xraycmp','periocmp','anaescmp','othercmp','nducmp','ndlcmp',
'oducmp','odlcmp',"customcmp",'ur8pl','ur7pl',
'ur6pl','ur5pl','ur4pl','ur3pl','ur2pl','ur1pl','ul1pl','ul2pl','ul3pl',
'ul4pl','ul5pl','ul6pl','ul7pl',
'ul8pl','ll8pl','ll7pl','ll6pl','ll5pl','ll4pl','ll3pl','ll2pl','ll1pl',
'lr1pl','lr2pl','lr3pl','lr4pl',
'lr5pl','lr6pl','lr7pl','lr8pl','ur8cmp','ur7cmp','ur6cmp','ur5cmp',
'ur4cmp','ur3cmp','ur2cmp','ur1cmp',
'ul1cmp','ul2cmp','ul3cmp','ul4cmp','ul5cmp','ul6cmp','ul7cmp','ul8cmp',
'll8cmp','ll7cmp','ll6cmp','ll5cmp',
'll4cmp','ll3cmp','ll2cmp','ll1cmp','lr1cmp','lr2cmp','lr3cmp','lr4cmp',
'lr5cmp','lr6cmp','lr7cmp','lr8cmp',
'examt','examd','accd','cmpd')

perioTableAtts=('chartdate','bpe','chartdata','flag')

mnhistTableAtts=('chgdate','ix','note')

notesTableAtts=('lineno','line')

mouth= ['ul8','ul7','ul6','ul5','ul4','ul3','ul2','ul1',
'ur1','ur2','ur3','ur4','ur5','ur6','ur7','ur8',
'lr8','lr7','lr6','lr5','lr4','lr3','lr2','lr1',
'll1','ll2','ll3','ll4','ll5','ll6','ll7','ll8']

decidmouth= ['***','***','***','ulE','ulD','ulC','ulB','ulA',
'urA','urB','urC','urD','urE','***','***','***',
'***','***','***','lrE','lrD','lrC','lrB','lrA',
'llA','llB','llC','llD','llE','***','***','***']

planDBAtts=("serialno", "plantype","band", "grosschg","discount","netchg",
"catcode", "planjoin","regno")

clinical_memos = ("synopsis",)


#################### sub classes ##############################################
class planData(object):
    '''
    a custom class to hold data about the patient's maintenance plan
    '''
    def __init__(self, sno):
        self.serialno = sno
        self.plantype = None
        self.band = None
        self.grosschg = 0
        self.discount = 0
        self.netchg = 0
        self.catcode = None
        self.planjoin = None
        self.regno = None
        #-- a variable to indicate if getFromDbhas been run
        self.retrieved=False

    def __repr__(self):
        return "%d,%s,%s,%s,%s,%s,%s,%s,%s"%(
        self.serialno, self.plantype, self.band, self.grosschg, self.discount,
        self.netchg, self.catcode, self.planjoin,self.regno)

    def getFromDB(self):
        try:
            db=connect.connect()
            cursor=db.cursor()

            query='''SELECT %s,%s,%s,%s,%s,%s,%s,%s from plandata
            where serialno=%s'''%(planDBAtts[1:]+(self.serialno,))
            if localsettings.logqueries:
                print query
            cursor.execute(query)
            row=cursor.fetchone()
            cursor.close()
            i=1
            if row:
                for val in row:
                    if val:
                        att=planDBAtts[i]
                        if att=="planjoin":
                            self.planjoin=localsettings.formatDate(val)
                        else:
                            self.__dict__[att]=val
                    i+=1
            self.retrieved=True
        except Exception,e:
            print "error loading from plandata",e

class patient(object):
    def __init__(self, sno):
        '''
        initiate the class with default variables, then load from database
        '''
        self.serialno = sno
        self.dbstate = None

        self.load_warnings = []
        self.courseno = None
        
        for i, att in enumerate(patientTableAtts):
            self.__dict__[att] = patientTableVals[i]

        ######TABLE 'mnhist'#######
        self.chgdate = nullDate   # date 	YES 	 	None
        self.ix = 0               #tinyint(3) unsigned 	YES 	 	None
        self.note = ''            #varchar(60) 	YES 	 	None

        ######data from the completed table#########
        self.blankCurrtrt()

        self.estimates = []

        ##from userdata
        self.plandata = planData(self.serialno)

        ###NEIL'S STUFF####
        self.exemption = ""
        self.exempttext = ""
        self.perioData = {}
        self.bpe = []
        self.bpedate = nullDate
        self.chartdate = nullDate
        self.notes_dict = {}
        self.MH = ()
        self.MEDALERT = False
        self.HIDDENNOTES = []
        self.chartgrid = {}
        #self.underTreatment = False
        self.feeTable = None
        self.synopsis = ""
        self._n_family_members = None
        self._dayBookHistory = None

        if self.serialno != 0:
            #load stuff from the database
            db = connect.connect()
            cursor = db.cursor()

            self.getSynopsis()

            fields = patientTableAtts
            query = ""
            for field in fields:
                query += field + ","

            query = 'SELECT %s from patients where serialno ='% (
            query.strip(","))

            cursor.execute(query + "%s", self.serialno)
            values= cursor.fetchall()

            if values == ():
                raise localsettings.PatientNotFoundError

            for i, field in enumerate(fields):
                if values[0][i] !=None:
                    self.__dict__[field]=values[0][i]

            query = '''select exemption, exempttext from exemptions
            where serialno=%s'''
            cursor.execute(query, self.serialno)

            values = cursor.fetchall()

            for value in values:
                self.exemption, self.exempttext = value

            query = '''select bpedate, bpe from bpe where serialno=%s 
            order by bpedate'''
            cursor.execute(query, self.serialno)

            values = cursor.fetchall()

            for value in values:
                self.bpe.append(value)

            if self.courseno0 != 0:
                self.getCurrtrt()
                self.getEsts()

            self.getNotesTuple()

            query = 'select chartdate,chartdata from perio where serialno=%s'
            cursor.execute(query, self.serialno)
            perioData=cursor.fetchall()

            for data in perioData:
                self.perioData[localsettings.formatDate(data[0])] = (
                perio.get_perioData(data[1]))
                #--perioData is
                #--a dictionary (keys=dates) of dictionaries with keys
                #--like "ur8" and containing 7 tuples of data

            query = 'select drnm,adrtel,curmed,oldmed,allerg,heart,lungs,'+\
            'liver,kidney,bleed,anaes,other,alert,chkdate from mednotes'+\
            ' where serialno=%s'
            cursor.execute(query, (self.serialno,))

            self.MH=cursor.fetchone()
            if self.MH!=None:
                self.MEDALERT=self.MH[12]

            cursor.close()
            #db.close()

            #-- load from plandata
            self.plandata.getFromDB()

            self.appt_prefs = ApptPrefs(self.serialno)

            self.updateChartgrid()
            #self.setCurrentEstimate()
            
            self.take_snapshot()


    @property
    def appt_memo(self):
        return self.appt_prefs.note

    def set_appt_memo(self, memo):
        self.appt_prefs.note = memo

    @property
    def recall_active(self):
        return self.appt_prefs.recall_active

    @property
    def recd(self):
        return self.appt_prefs.recdent

    @property
    def dayBookHistory(self):
        if self._dayBookHistory is None:
            db = connect.connect()
            cursor = db.cursor()
            query = 'select date, trtid, chart from daybook where serialno=%s'
            cursor.execute(query, self.serialno)
            self._dayBookHistory=cursor.fetchall()
            cursor.close()
        return self._dayBookHistory

    def __repr__(self):
        return "'Patient_class instance - serialno %d'"% self.serialno

    @property
    def address(self):
        '''
        a printable address
        '''
        address = ""
        for line in (self.addr1, self.addr2, self.addr3,
        self.town, self.county, self.pcde):
            if line.strip(" ") != "":
                address += "%s\n"% line.strip(" ")
        return address

    def getAge(self):
        '''
        return the age in form (year(int), months(int), isToday(bool))
        '''
        try:
            today = localsettings.currentDay()

            day = self.dob.day

            try:
                nextbirthday = datetime.date(today.year, self.dob.month,
                self.dob.day)
            except ValueError:
                #catch leap years!!
                nextbirthday = datetime.date(today.year, self.dob.month,
                self.dob.day-1)

            ageYears = today.year - self.dob.year

            if nextbirthday > today:
                ageYears -= 1
                months = (12 - self.dob.month) + today.month
            else:
                months = today.month - self.dob.month
            if self.dob.day > today.day:
                months -= 1

            isToday =  nextbirthday == today

            return (ageYears, months, isToday)

        except Exception, e:
            print "error calculating patient's age", e
            return (0,0,False)
    
    @property
    def ageYears(self):
        return self.getAge()[0]
    
    @property
    def under_6(self):
        '''
        returns a bool "is patient under 6?".
        '''
        return self.ageYears < 6

    @property
    def under_18(self):
        '''
        returns a bool "is patient under 18?".
        '''
        return self.ageYears < 18

    def getFeeTable(self):
        '''
        logic to determine which feeTable should be used for standard items
        '''
        if self.feeTable == None:
            feecat = self.cset
            if self.cset == "N":
                if self.getAge()[0] < 18:
                    feecat = "C"
            if self.accd is None:
                cse_accd = localsettings.currentDay()
            else:
                cse_accd = self.accd
            for table in localsettings.FEETABLES.tables.values():
                start, end = table.startDate, table.endDate
                if end == None:
                    end = localsettings.currentDay()

                if feecat in table.categories and start <= cse_accd <=end:
                    self.feeTable = table

            if self.feeTable == None:
                #-- no matching table found, use the default.
                print "WARNING - NO SUITABLE FEETABLE FOUND, RETURNING DEFAULT"
                self.feeTable = localsettings.FEETABLES.default_table

        return self.feeTable

    def getEsts(self):
        '''
        get estimate data
        '''
        db = connect.connect()
        cursor = db.cursor()

        cursor.execute('''SELECT ix, number, itemcode, description, category,
type, fee, ptfee, feescale, csetype, dent, completed, carriedover from
newestimates where serialno=%s and courseno=%s order by itemcode desc''', (
self.serialno, self.courseno0))

        rows = cursor.fetchall()
        self.estimates = []
        for row in rows:
            #initiate a custom data class
            est = estimates.Estimate()
            est.ix = row[0]
            est.number = row[1]
            est.itemcode = row[2]
            est.description = row[3]
            est.category = row[4]
            est.type = row[5]
            est.fee = row[6]
            est.ptfee = row[7]
            est.feescale = row[8]
            est.csetype = row[9]
            est.dent = row[10]
            est.completed = bool(row[11])
            est.carriedover = bool(row[12])
            self.estimates.append(est)

        cursor.close()

    def blankCurrtrt(self):
        for att in currtrtmtTableAtts:
            if att == 'courseno':
                pass
            elif att in ('examd', 'cmpd', 'accd'):
                self.__dict__[att] = nullDate
            else:
                self.__dict__[att] = ""

    def getSynopsis(self):
        db = connect.connect()
        cursor = db.cursor()
        fields = clinical_memos
        query=""
        for field in fields:
            query += field+","
        query=query.strip(",")
        try:
            if cursor.execute(
            'SELECT %s from clinical_memos where serialno=%d'% ( query,
            self.serialno)):
                self.synopsis = cursor.fetchall()[-1][0]
        except connect.OperationalError, e:
            'necessary because the column is missing is db schema 1.4'
            print "WARNING -", e

    def getCurrtrt(self):
        fields = currtrtmtTableAtts
        query = "SELECT "
        for field in fields:
            query += "%s, "% field
        query = query.rstrip(", ")
        query += " from currtrtmt2 where serialno=%s and courseno=%s"
        
        db = connect.connect()
        cursor = db.cursor()
        
        cursor.execute(query, (self.serialno, self.courseno0))

        for value in cursor.fetchall():
            for i, field in enumerate(fields):
                self.__dict__[field] = value[i]
        
        cursor.close()

    @property
    def underTreatment(self):
        return (not self.accd in ("", None) and self.cmpd in ("", None))
        
    @property
    def max_tx_courseno(self):
        db = connect.connect()
        cursor = db.cursor()
        if cursor.execute( 
        "select max(courseno) from currtrtmt2 where serialno=%s", 
        (self.serialno,)):
            cno = cursor.fetchone()[0]
        else:
            cno = 0
        cursor.close()
        return cno
    
    @property
    def newer_course_found(self):
        return self.max_tx_courseno > self.courseno
    
    def getNotesTuple(self):
        '''
        connect and poll the formatted_notes table
        '''
        self.notes_dict = formatted_notes.get_notes_dict(self.serialno)

    def flipDec_Perm(self, tooth):
        '''
        switches a deciduous tooth to a permanent one,
        and viceVersa pass a variable like "ur5"
        '''
        quadrant=tooth[:2]
        pos=int(tooth[2])-1                 # will be 0-7
        if quadrant=="ul":
            var=self.dent1
            pos=7-pos
        elif quadrant=="ur":
            var=self.dent0
        elif quadrant=="ll":
            var=self.dent2
        else: #lr
            var=self.dent3
            pos=7-pos
        existing=dec_perm.fromSignedByte(var)
        if existing[pos]=="1":
            existing=existing[:pos]+"0"+existing[pos+1:]
        else:
            existing=existing[:pos]+"1"+existing[pos+1:]
        if quadrant=="ul":
            self.dent1=dec_perm.toSignedByte(existing)
        elif quadrant=="ur":
            self.dent0=dec_perm.toSignedByte(existing)
        elif quadrant=="ll":
            self.dent2=dec_perm.toSignedByte(existing)
        else: #lr
            self.dent3=dec_perm.toSignedByte(existing)
        self.updateChartgrid()

    def updateChartgrid(self):
        grid=""
        for quad in (self.dent1,self.dent0,self.dent3,self.dent2):
            grid+=dec_perm.fromSignedByte(quad)
        for pos in mouth:
            if grid[mouth.index(pos)]=="0":
                self.chartgrid[pos]=pos
            else:
                self.chartgrid[pos]=decidmouth[mouth.index(pos)]

    def applyFee(self, arg, cset=None):
        '''
        raise a charge
        '''
        if cset == None:
            cset = self.cset
        if "N" in cset:
            self.money0 += arg
        else:
            self.money1 += arg

    @property
    def fees(self):
        return int(self.money0 + self.money1 + self.money9 + self.money10 +
        self.money11 - self.money2 - self.money3 - self.money8)

    def setAccd(self, accd):
        '''
        set the acceptance date (with a pydate)
        '''
        if accd is None:
            accd = localsettings.currentDay()
        self.accd = accd

    def setCmpd(self, cmpd):
        '''
        set the completion date (with a pydate)
        '''
        self.cmpd = cmpd

    def resetAllMonies(self):
        '''
        zero's everything except money11 (bad debt)
        '''
        self.money0=0
        self.money1=0
        self.money9=0
        self.money10=0
        self.money2=0
        self.money3=0
        self.money8=0

    def removeKnownEstimate(self, est):
        try:
            self.estimates.remove(est)
            return True
        except ValueError:
            print "unable to find known est in estimates"

    def removeFromEstimate(self, tooth, item):
        if item !="":
            type="%s %s"%(tooth,item)
            for est in self.estimates:
                if est.category==tooth and \
                est.type==item and est.completed==False:
                    self.estimates.remove(est)
                    break #-- only remove 1 occurrence??

    def addToEstimate(self, number, itemcode, dent, csetype="",
    category="", type="", descr=None, fee=None, ptfee=None,
    completed=False, feescale=None, carriedover=False):
        '''
        add an item to the patient's estimate
        '''
        if type.strip(" ") =="":
            return
        est = estimates.Estimate()
        est.ix = None #-- this will be generated by autoincrement on commit
        est.serialno = self.serialno
        est.courseno = self.courseno0
        est.number = number
        est.itemcode = itemcode

        if feescale == None:
            table = self.getFeeTable()
        else:
            table = localsettings.FEETABLES.tables[feescale]

        est.feescale = table.index
        if csetype == "":
            csetype = table.categories[0]
        est.csetype = csetype

        #handle the case where there are more than one item of the same code
        existing_no = 0
        for existing_est in self.estimates:
            if existing_est.itemcode == est.itemcode and \
            est.csetype == existing_est.csetype:
                existing_no += 1
        linked = existing_no > 0
        for existing_est in self.estimates:
            if existing_est.itemcode == est.itemcode:
                existing_est.linked = linked
        est.linked = linked

        est.type = type
        if descr == None:
            est.description = table.getItemDescription(itemcode)
        else:
            est.description = descr
        if fee == None:
            est.fee, est.ptfee = table.getFees(
            itemcode, number, no_already_in_estimate=existing_no)
        else:
            est.fee, est.ptfee = fee, ptfee

        if category != "":
            est.category = category
        else:
            est.category = table.getTxCategory(itemcode)

        est.dent = dent
        est.completed = completed
        est.carriedover = carriedover

        self.estimates.append(est)

        return est

    @property
    def nhs_claims(self):
        claims = []
        for est in self.estimates:
            if est.csetype == "N" and est.completed:
                #yield est
                claims.append(est)
        return claims

    def addHiddenNote(self,ntype,note="",deleteIfPossible=False):
        '''
        re-written for schema 1.9
        '''
        print(
        "patient.addHiddenNote(ntype='%s',note='%s',deleteIfPossible='%s'"% (
        ntype, note, deleteIfPossible)
        )
        HN = ()
        if ntype=="payment":
            HN=("RECEIVED: ", note)
        elif ntype=="printed":
            HN=("PRINTED: ", note)
        elif ntype=="exam":
            HN=("TC: EXAM", note)
        elif ntype=="chart_treatment":
            HN=("TC:", note)
        elif ntype=="perio_treatment":
            HN=("TC: PERIO", note)
        elif ntype=="xray_treatment":
            HN=("TC: XRAY", note)
        elif ntype=="treatment":
            HN=("TC: OTHER", note)
        elif ntype=="mednotes":               #other treatment
            HN=("UPDATED:Medical Notes", note)
        elif ntype=="close_course":
            HN=("COURSE CLOSED", "="*10)
        elif ntype=="open_course":
            HN=("COURSE OPENED", "= "*5)
        elif ntype=="resume_course":
            HN=("COURSE RE-OPENED", "= "*5)
        elif ntype=="fee":
            HN=("INTERIM: ", note)

        if not HN:
            print "unable to add Hidden Note notetype '%s' not found"% ntype
            return

        if deleteIfPossible:
            if HN in self.HIDDENNOTES:
                self.HIDDENNOTES.remove(HN)
            else:
                self.HIDDENNOTES.append(
                    ("UNCOMPLETED", "{%s, %s}"% (ntype,note)))
        else:
            self.HIDDENNOTES.append(HN)
        #print self.HIDDENNOTES

    def clearHiddenNotes(self):
        self.HIDDENNOTES=[]

    def updateBilling(self,tone):
        self.billdate = localsettings.currentDay()
        self.billct += 1
        self.billtype = tone

    def treatmentOutstanding(self):
        for att in currtrtmtTableAtts:
            if att[-2:] == "pl":
                if self.__dict__[att] != "":
                    return True

    def checkExemption(self):
        if self.exemption == "A" and self.getAge()[0] > 17:
            self.exemption = ""
            self.load_warnings.append(_("Age Exemption removed"))
        else:
            return True

    @property
    def name_id(self):
        return u"%s - %s"% (
            self.name, self.serialno)

    @property
    def name(self):
        return u"%s %s %s"% (
            self.title, self.fname, self.sname)

    @property
    def n_family_members(self):
        if self._n_family_members is None:
            db = connect.connect()
            cursor = db.cursor()
            cursor.execute("select count(*) from patients where familyno=%s", 
                (self.familyno,))
            self._n_family_members = cursor.fetchone()[0]
        
        return self._n_family_members

    @property
    def under_capitation(self):
        if self.cset != "N":
            return False
        if self.accd is None:
            return self.ageYears < 19
        eighteenth = self.dob + datetime.timedelta(days = 18 * 365.24)
        return self.accd < eighteenth

    
    @property
    def user_changeable_attributes(self):
        '''
        the attributes used to determine whether the patient has been edited.
        '''        
        return (patientTableAtts + 
            exemptionTableAtts + bpeTableAtts + 
            currtrtmtTableAtts + mnhistTableAtts + 
            perioTableAtts + planDBAtts + 
            clinical_memos + ("estimates", "appt_prefs"))
    
    @property
    def changes(self):
        changes = []
        for att in self.user_changeable_attributes:
            new_value = self.__dict__.get(att, "")
            db_value = self.dbstate.__dict__.get(att, "")
            if  new_value != db_value:
                changes.append(att)
        return changes
 
    def take_snapshot(self):
        # create a snapshot of this class, copying all attributes that the 
        # user can change 
        memo = {}
        cls = self.__class__
        snapshot = cls.__new__(cls)
        memo[id(self)] = snapshot
        for att, v in self.__dict__.items():
            if att in self.user_changeable_attributes + ("blankCurrtrt",):
                setattr(snapshot, att, deepcopy(v, memo))
        self.dbstate = snapshot
    
if __name__ =="__main__":
    '''testing stuff'''
    try:
        serialno = int(sys.argv[len(sys.argv)-1])
    except:
        serialno = 1
    
    if "-v" in sys.argv:
        verbose = True
    else:
         verbose = False

    pt = patient(serialno)
    if verbose:
      for att in sorted(pt.__dict__.keys()):
            print "%s '%s'"% (att.ljust(20), pt.__dict__[att])
    
    localsettings.loadFeeTables()
    pt.getFeeTable()
    
    pt.take_snapshot() 
    pt.dob = datetime.date(1969,12,9)
    print pt.changes