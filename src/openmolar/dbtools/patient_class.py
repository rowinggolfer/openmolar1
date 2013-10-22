# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

from copy import deepcopy
import datetime
import logging
import re
import sys

from openmolar import connect
from openmolar.ptModules import perio, dec_perm, estimates, notes, formatted_notes
from openmolar.settings import localsettings

from openmolar.dbtools.appt_prefs import ApptPrefs
from openmolar.dbtools.treatment_course import TreatmentCourse
from openmolar.dbtools.plan_data import PlanData

from openmolar.dbtools.queries import ESTS_QUERY, PATIENT_QUERY

LOGGER = logging.getLogger("openmolar")

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

clinical_memos = ("synopsis",)

class patient(object):
    def __init__(self, sno):
        '''
        initiate the class with default variables, then load from database
        '''
        self.serialno = sno
        self.dbstate = None

        self.load_warnings = []

        ## patient table atts
        self.courseno0 = None
        self.pf0 = 0
        self.pf1 = 0
        self.pf2 = 0
        self.pf3 = 0
        self.pf4 = 0
        self.pf5 = 0
        self.pf6 = 0
        self.pf7 = 0
        self.pf8 = 0
        self.pf9 = 0
        self.pf10 = 0
        self.pf11 = 0
        self.pf12 = 0
        self.pf14 = 0
        self.pf15 = 0
        self.pf16 = 0
        self.pf17 = 0
        self.pf18 = 0
        self.pf19 = 0
        self.money0 = 0
        self.money1 = 0
        self.money2 = 0
        self.money3 = 0
        self.money4 = 0
        self.money5 = 0
        self.money6 = 0
        self.money7 = 0
        self.money8 = 0
        self.money9 = 0
        self.money10 = 0
        self.pd0 = None
        self.pd1 = None
        self.pd2 = None
        self.pd3 = None
        self.pd4 = None
        self.pd5 = None
        self.pd6 = None
        self.pd7 = None
        self.pd8 = None
        self.pd9 = None
        self.pd10 = None
        self.pd11 = None
        self.pd12 = None
        self.pd13 = None
        self.pd14 = None
        self.sname = ''
        self.fname = ''
        self.title = ''
        self.sex = ''
        self.dob = None
        self.addr1 = ''
        self.addr2 = ''
        self.addr3 = ''
        self.pcde = ''
        self.tel1 = ''
        self.tel2 = ''
        self.occup = ''
        self.nhsno = ''
        self.cnfd = None
        self.psn = ''
        self.cset = ''
        self.dnt1 = 0
        self.dnt2 = 0
        self.courseno1 = 0
        self.ur8st = ''
        self.ur7st = ''
        self.ur6st = ''
        self.ur5st = ''
        self.ur4st = ''
        self.ur3st = ''
        self.ur2st = ''
        self.ur1st = ''
        self.ul1st = ''
        self.ul2st = ''
        self.ul3st = ''
        self.ul4st = ''
        self.ul5st = ''
        self.ul6st = ''
        self.ul7st = ''
        self.ul8st = ''
        self.ll8st = ''
        self.ll7st = ''
        self.ll6st = ''
        self.ll5st = ''
        self.ll4st = ''
        self.ll3st = ''
        self.ll2st = ''
        self.ll1st = ''
        self.lr1st = ''
        self.lr2st = ''
        self.lr3st = ''
        self.lr4st = ''
        self.lr5st = ''
        self.lr6st = ''
        self.lr7st = ''
        self.lr8st = ''
        self.dent0 = 0
        self.dent1 = 0
        self.dent2 = 0
        self.dent3 = 0
        self.dmask = "YYYYYYY"
        self.minstart = 0
        self.maxend = 0
        self.billdate = None
        self.billct = 0
        self.billtype = None
        self.pf20 = 0
        self.money11 = 0
        self.pf13 = 0
        self.familyno = 0
        self.memo = ''
        self.town = ''
        self.county = ''
        self.mobile = ''
        self.fax = ''
        self.email1 = ''
        self.email2 = ''
        self.status = ''
        self.source = ''
        self.enrolled = ''
        self.archived = None
        self.initaccept = 0
        self.lastreaccept = None
        self.lastclaim = None
        self.expiry = None
        self.cstatus = None
        self.transfer = 0
        self.pstatus = None
        self.courseno2 = 0

        ######TABLE 'mnhist'#######
        self.chgdate = nullDate   # date 	YES 	 	None
        self.ix = 0               #tinyint(3) unsigned 	YES 	 	None
        self.note = ''            #varchar(60) 	YES 	 	None

        self.estimates = []

        ##from userdata
        self.plandata = PlanData(self.serialno)

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
        self.feeTable = None
        self.synopsis = ""
        self._n_family_members = None
        self._dayBookHistory = None
        self.treatment_course = None

        if self.serialno != 0:
            #load stuff from the database
            db = connect.connect()
            cursor = db.cursor()

            self.getSynopsis()

            cursor.execute(PATIENT_QUERY, (self.serialno,))
            values= cursor.fetchall()

            if values == ():
                raise localsettings.PatientNotFoundError

            for i, att in enumerate(patientTableAtts):
                value = values[0][i]
                if value is not None:
                    self.__dict__[att] = value

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
                self.getEsts()

            self.treatment_course = TreatmentCourse(
                self.serialno, self.courseno0)

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
            if self.treatment_course.accd is None:
                cse_accd = localsettings.currentDay()
            else:
                cse_accd = self.treatment_course.accd
            for table in localsettings.FEETABLES.tables.values():

                LOGGER.debug(
                "checking feescale %s to see if suitable a feetable"% (
                table))

                start, end = table.startDate, table.endDate
                LOGGER.debug("categories, start, end = %s, %s, %s"% (
                    table.categories, start, end))
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

        cursor.execute(ESTS_QUERY, (self.serialno, self.courseno0))

        rows = cursor.fetchall()
        self.estimates = []

        for row in rows:
            hash_ = row[10]
            completed = bool(row[9])

            tx_hash = estimates.TXHash(hash_, completed)

            ix = row[0]

            found = False
            #use existing est if one relates to multiple treatments
            for existing_est in self.estimates:
                if existing_est.ix == ix:
                    existing_est.tx_hashes.append(tx_hash)
                    found = True
                    break
            if found:
                continue

            #initiate a custom data class
            est = estimates.Estimate()

            est.ix = ix
            est.number = row[1]
            est.itemcode = row[2]
            est.description = row[3]
            est.fee = row[4]
            est.ptfee = row[5]
            est.feescale = row[6]
            est.csetype = row[7]
            est.dent = row[8]

            #est.category = "TODO"
            #est.type_ = "TODO"

            est.tx_hashes = [tx_hash]
            self.estimates.append(est)

        cursor.close()



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

    @property
    def underTreatment(self):
        return (self.treatment_course is not None and
        self.treatment_course.underTreatment)

    @property
    def max_tx_courseno(self):
        return self.treatment_course.max_tx_courseno

    @property
    def newer_course_found(self):
        return self.treatment_course.newer_course_found

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

    def apply_fees(self):
        if "N" in self.cset:
            self.money0 = self.dbstate.money0 + self.fees_accrued
        else:
            self.money1 = self.dbstate.money1 + self.fees_accrued

    @property
    def fees(self):
        return int(self.money0 + self.money1 + self.money9 + self.money10 +
        self.money11 - self.money2 - self.money3 - self.money8)

    @property
    def fees_accrued(self):
        old_estimate_charges = 0
        if self.courseno0 == self.dbstate.courseno0:
            old_estimate_charges = self.dbstate.estimate_charges

        accrued_fees = self.estimate_charges - old_estimate_charges
        LOGGER.debug("fees_accrued = (new-existing) = %d - %d = %d"%(
                self.estimate_charges,
                old_estimate_charges,
                accrued_fees)
                )
        return accrued_fees

    @property
    def estimate_charges(self):
        charges = 0
        for est in self.estimates:
            if est.completed == 2:
                charges += est.ptfee
            elif est.completed == 1:
                charges += est.interim_pt_fee
        return charges

    def resetAllMonies(self):
        '''
        zero's everything except money11 (bad debt)
        '''
        self.money0 = 0
        self.money1 = 0
        self.money9 = 0
        self.money10 = 0
        self.money2 = 0
        self.money3 = 0
        self.money8 = 0

    @property
    def nhs_claims(self):
        claims = []
        for est in self.estimates:
            if est.csetype == "N" and est.completed:
                #yield est
                claims.append(est)
        return claims

    def addHiddenNote(self, ntype, note="", attempt_delete=False):
        '''
        re-written for schema 1.9
        '''
        LOGGER.info(
        "patient.addHiddenNote(ntype='%s',note='%s', attempt_delete='%s'"% (
        ntype, note, attempt_delete))

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

        reversing_note = ("UNCOMPLETED", "{%s}"% note)

        if attempt_delete:
            try:
                self.HIDDENNOTES.remove(HN)
            except ValueError:
                self.HIDDENNOTES.append(reversing_note)
        else:
            try:
                self.HIDDENNOTES.remove(reversing_note)
            except ValueError:
                self.HIDDENNOTES.append(HN)

    def clearHiddenNotes(self):
        self.HIDDENNOTES=[]

    def updateBilling(self,tone):
        self.billdate = localsettings.currentDay()
        self.billct += 1
        self.billtype = tone

    def treatmentOutstanding(self):
        return (self.treatment_course and
        self.treatment_course.has_treatment_outstanding)

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
        if self.treatment_course.accd is None:
            return self.ageYears < 19
        eighteenth = self.dob + datetime.timedelta(days = 18 * 365.24)
        return self.treatment_course.accd < eighteenth

    def new_tx_course(self, new_courseno):
        self.courseno0 = new_courseno
        self.treatment_course = TreatmentCourse(self.serialno, new_courseno)

    @property
    def user_changeable_attributes(self):
        '''
        the attributes used to determine whether the patient has been edited.
        '''
        return (patientTableAtts +
            exemptionTableAtts + bpeTableAtts + mnhistTableAtts +
            perioTableAtts + clinical_memos + ("fees", "estimate_charges",
            "serialno", "estimates", "appt_prefs", "treatment_course"))

    @property
    def changes(self):
        changes = []
        for att in self.user_changeable_attributes:
            new_value = self.__dict__.get(att, "")
            db_value = self.dbstate.__dict__.get(att, "")
            if  new_value != db_value:
                LOGGER.debug("PT DBSTATE ALTERED - %s"% att)
                if att != "treatment_course":
                    LOGGER.debug(
                    "  OLD '%s' NEW - '%s'"% (db_value, new_value))

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
            if att in self.user_changeable_attributes:
                setattr(snapshot, att, deepcopy(v, memo))
        self.dbstate = snapshot

        LOGGER.debug("snapshot of %s taken"% self)

    @property
    def course_dentist(self):
        '''
        returns the course dentist for NHS and private courses, but the
        contracted dentist otherwise.
        this is used in the daybook for "work done for lists".
        '''
        if self.cset == "I":
            return self.dnt1
        if self.dnt2 not in (0, None):
            return self.dnt2
        return self.dnt1

    @property
    def has_new_course(self):
        if self.treatment_course and self.dbstate.treatment_course is None:
            return True
        return (self.treatment_course.courseno !=
                        self.dbstate.treatment_course.courseno)

    @property
    def tx_hashes(self):
        '''
        a list of unique hashes of all treatment on the current treatment plan
        '''
        for tup in self.treatment_course._get_tx_hashes():
            yield tup

    @property
    def completed_tx_hashes(self):
        return self.treatment_course.completed_tx_hashes

    @property
    def planned_tx_hashes(self):
        return self.treatment_course.planned_tx_hashes

    @property
    def has_planned_perio_txs(self):
        for hash_, att, tx in self.planned_tx_hashes:
            if att == "perio":
                return True
        return False

    def get_tx_from_hash(self, hash_):
        return self.treatment_course.get_tx_from_hash(hash_)

    def ests_from_hash(self, hash_):
        '''
        return all estimate items associated with a unique tx_hash
        '''
        for est in self.estimates:
            for tx_hash in est.tx_hashes:
                if tx_hash == hash_:
                    yield est

    def add_to_estimate(self, usercode, dentid, tx_hashes,
    itemcode=None, csetype=None, descr=None,
    fee=None, ptfee=None, chosen_feescale=None):
        '''
        add an item to the patient's estimate
        usercode unnecessary if itemcode is provided.
        '''
        LOGGER.debug("patient.add_to_estimate %s %s %s %s %s %s %s %s %s"%(
            usercode, dentid, tx_hashes,
            itemcode, csetype, descr,
            fee, ptfee, chosen_feescale)
            )

        for tx_hash in tx_hashes:
            assert type(tx_hash) == estimates.TXHash, "bad form Neil"

        est = estimates.Estimate()
        est.ix = None #-- this will be generated by autoincrement on commit
        est.serialno = self.serialno
        est.courseno = self.courseno0

        if chosen_feescale == None:
            table = self.getFeeTable()
        else:
            table = localsettings.FEETABLES.tables[feescale]

        if csetype is None:
            est.csetype = self.cset
        else:
            est.csetype = csetype

        if itemcode is None:
            itemcode, descr = table.userCodeWizard(usercode)

        est.itemcode = itemcode

        if descr == None:
            est.description = table.getItemDescription(itemcode)
        else:
            est.description = descr

        if fee is None and ptfee is None:
            #look up the fee here
            est.fee, est.ptfee = table.getFees(itemcode, self, est.csetype)
        else:
            est.fee, est.ptfee = fee, ptfee

        est.tx_hashes = tx_hashes

        est.dent = dentid

        inserted = False
        for i, existing_est in enumerate(self.estimates):
            if existing_est.itemcode == est.itemcode:
                try:
                    if self.estimates[i+1].itemcode != est.itemcode:
                        self.estimates.insert(i, est)
                        inserted = True
                        break
                except IndexError:
                    pass

        if not inserted:
            self.estimates.append(est)

        return est

if __name__ =="__main__":
    '''testing stuff'''
    try:
        serialno = int(sys.argv[len(sys.argv)-1])
    except:
        serialno = 1

    LOGGER.setLevel(logging.DEBUG)

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
    print list(pt.tx_hashes)

    print pt.treatment_course