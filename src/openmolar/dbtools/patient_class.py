#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2015 Neil Wallace <neil@openmolar.com>               # #
# #                                                                         # #
# # This file is part of OpenMolar.                                         # #
# #                                                                         # #
# # OpenMolar is free software: you can redistribute it and/or modify       # #
# # it under the terms of the GNU General Public License as published by    # #
# # the Free Software Foundation, either version 3 of the License, or       # #
# # (at your option) any later version.                                     # #
# #                                                                         # #
# # OpenMolar is distributed in the hope that it will be useful,            # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of          # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           # #
# # GNU General Public License for more details.                            # #
# #                                                                         # #
# # You should have received a copy of the GNU General Public License       # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.      # #
# #                                                                         # #
# ########################################################################### #

'''
patient_class.py
'''

from copy import deepcopy
import datetime
from gettext import gettext as _
import logging
import re
import sys

from openmolar import connect
from openmolar.ptModules import dec_perm, formatted_notes
from openmolar.settings import localsettings

from openmolar.dbtools.appt_prefs import ApptPrefs
from openmolar.dbtools.treatment_course import TreatmentCourse
from openmolar.dbtools.plan_data import PlanData
from openmolar.dbtools.est_logger import EstLogger
from openmolar.dbtools import estimates as db_estimates
from openmolar.dbtools import records_in_use

from openmolar.dbtools.queries import (
    PATIENT_QUERY_FIELDS, PATIENT_QUERY, FUTURE_EXAM_QUERY,
    PSN_QUERY, FAMILY_COUNT_QUERY, QUICK_MED_QUERY, SYNOPSIS_QUERY)

LOGGER = logging.getLogger("openmolar")

dateFields = (
    "dob", "pd0", "pd1", "pd2", "pd3", "pd4", "pd5", "pd6",
    "pd7", "pd8", "pd9", "pd10", "pd11", "pd12", "pd13", "pd14", "cnfd",
    "recd", "billdate", "enrolled", "initaccept", "lastreaccept", "lastclaim",
    "expiry", "transfer", "chartdate", "accd", "cmpd", "examd", "bpedate")

nullDate = None

patientTableAtts = (
    'sname', 'fname', 'title', 'sex', 'dob',
    'addr1', 'addr2', 'addr3', 'pcde', 'town', 'county',
    'tel1', 'tel2', 'mobile', 'fax', 'email1', 'email2',
    'occup', 'nhsno', 'cnfd', 'cset', 'dnt1', 'dnt2', 'courseno0',
    'billdate', 'billct', 'billtype', 'familyno', 'memo', 'status'
)

money_table_atts = (
    'money0', 'money1', 'money2', 'money3', 'money4', 'money5', 'money6',
    'money7', 'money8', 'money9', 'money10', 'money11'
)

nhs_table_atts = (
    'initaccept', 'lastreaccept', 'lastclaim', 'expiry',
    'cstatus', 'transfer', 'pstatus'
)

static_table_atts = (
    'ur8st', 'ur7st', 'ur6st', 'ur5st', 'ur4st', 'ur3st', 'ur2st', 'ur1st',
    'ul1st', 'ul2st', 'ul3st', 'ul4st', 'ul5st', 'ul6st', 'ul7st', 'ul8st',
    'll8st', 'll7st', 'll6st', 'll5st', 'll4st', 'll3st', 'll2st', 'll1st',
    'lr1st', 'lr2st', 'lr3st', 'lr4st', 'lr5st', 'lr6st', 'lr7st', 'lr8st',
    'dent0', 'dent1', 'dent2', 'dent3'
)

date_table_atts = (
    'pd0', 'pd1', 'pd2', 'pd3', 'pd4', 'pd5', 'pd6', 'pd7', 'pd8', 'pd9',
    'pd10', 'pd11', 'pd12', 'pd13', 'pd14'
)

exemptionTableAtts = ('exemption', 'exempttext')

bpeTableAtts = ('bpedate', 'bpe')
bpeTableVals = (nullDate, '', ())

mouth = ['ul8', 'ul7', 'ul6', 'ul5', 'ul4', 'ul3', 'ul2', 'ul1',
         'ur1', 'ur2', 'ur3', 'ur4', 'ur5', 'ur6', 'ur7', 'ur8',
         'lr8', 'lr7', 'lr6', 'lr5', 'lr4', 'lr3', 'lr2', 'lr1',
         'll1', 'll2', 'll3', 'll4', 'll5', 'll6', 'll7', 'll8']

decidmouth = ['***', '***', '***', 'ulE', 'ulD', 'ulC', 'ulB', 'ulA',
              'urA', 'urB', 'urC', 'urD', 'urE', '***', '***', '***',
              '***', '***', '***', 'lrE', 'lrD', 'lrC', 'lrB', 'lrA',
              'llA', 'llB', 'llC', 'llD', 'llE', '***', '***', '***']

clinical_memos = ("synopsis",)

_atts = []
for att in PATIENT_QUERY_FIELDS:
    if re.match(r"[ul][lr]\d$", att):
        _atts.append(att + "st")
    else:
        _atts.append(att)
patient_query_atts = tuple(_atts)


class patient(object):

    '''
    this class pulls information from the database into a python object.
    '''
    def __init__(self, sno):
        '''
        initiate the class with default variables, then load from database
        '''
        self.serialno = sno
        self.dbstate = None

        self.load_warnings = []

        # patient table atts
        self.courseno0 = None
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
        self.pd4 = None  # this field is no longer used (last treatment date)
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
        self.cset = ''
        self.dnt1 = 0
        self.dnt2 = 0
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
        self.billdate = None
        self.billct = 0
        self.billtype = None
        self.money11 = 0
        self.familyno = localsettings.last_family_no
        self.memo = ''
        self.town = ''
        self.county = ''
        self.mobile = ''
        self.fax = ''
        self.email1 = ''
        self.email2 = ''
        self.status = ''
        self.initaccept = 0
        self.lastreaccept = None
        self.lastclaim = None
        self.expiry = None
        self.cstatus = None
        self.transfer = 0
        self.pstatus = None

        self.estimates = []

        # from userdata
        self.plandata = PlanData(self.serialno)

        # NEIL'S STUFF####
        self.exemption = ""
        self.exempttext = ""
        self.bpe = []
        self.bpedate = nullDate
        self.chartdate = nullDate
        self.notes_dict = {}
        self.MEDALERT = False
        self.mh_chkdate = None
        self.HIDDENNOTES = []
        self.chartgrid = {}
        self._fee_table = None
        self.synopsis = ""
        self._n_family_members = None
        self._dayBookHistory = None
        self.treatment_course = None
        self.est_logger = None
        self._most_recent_daybook_entry = None
        self._first_note_date = None
        self._has_exam_booked = None
        self._previous_surnames = None
        self.monies_reset = False
        self._n_hyg_visits = None

        if self.serialno == 0:
            return

        #
        # now load stuff from the database ##
        #
        db = connect.connect()
        cursor = db.cursor()

        self.getSynopsis()

        cursor.execute(PATIENT_QUERY, (self.serialno,))
        values = cursor.fetchall()

        if values == ():
            raise localsettings.PatientNotFoundError

        for i, att_ in enumerate(patient_query_atts):
            value = values[0][i]
            if value is not None:
                self.__dict__[att_] = value
            elif att_ == "familyno":
                self.familyno = 0

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

        cursor.execute(QUICK_MED_QUERY, (self.serialno,))
        try:
            self.MEDALERT, self.mh_chkdate = cursor.fetchone()
        except TypeError:
            pass
        cursor.close()
        # db.close()

        # - load from plandata
        self.plandata.getFromDB()

        self.appt_prefs = ApptPrefs(self.serialno)

        self.updateChartgrid()

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
    def exam_due(self):
        return self.recall_active and self.recd < localsettings.currentDay()

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
            self._dayBookHistory = cursor.fetchall()
            cursor.close()
        return self._dayBookHistory

    @property
    def last_treatment_date(self):
        max_date = localsettings.currentDay()
        if self.treatment_course.cmp_txs != \
                self.dbstate.treatment_course.cmp_txs:
            return max_date
        if self._most_recent_daybook_entry is None:
            db = connect.connect()
            cursor = db.cursor()
            query = 'select max(date) from daybook where serialno=%s'
            if cursor.execute(query, self.serialno):
                max_date = cursor.fetchone()[0]
            cursor.close()
            self._most_recent_daybook_entry = max_date
        return self._most_recent_daybook_entry

    @property
    def first_note_date(self):
        '''
        returns teh first date found in the patient notes
        '''
        if self._first_note_date is None:
            min_date = localsettings.currentDay()
            db = connect.connect()
            cursor = db.cursor()
            query = 'select min(ndate) from formatted_notes where serialno=%s'
            if cursor.execute(query, (self.serialno,)):
                min_date = cursor.fetchone()[0]
            cursor.close()
            self._first_note_date = min_date
        return self._first_note_date

    @property
    def n_hyg_visits(self):
        if self._n_hyg_visits is None:
            self._n_hyg_visits = 0
            db = connect.connect()
            cursor = db.cursor()
            query = '''select count(*) from
            (select date from daybook where serialno=%s and
            trtid in %s group by date) as t;'''
            if cursor.execute(query, (self.serialno, localsettings.hyg_ixs)):
                self._n_hyg_visits = cursor.fetchone()[0]
            cursor.close()
        return self._n_hyg_visits

    def forget_exam_booked(self):
        self._has_exam_booked = None

    @property
    def has_exam_booked(self):
        if self._has_exam_booked is None:
            db = connect.connect()
            cursor = db.cursor()
            cursor.execute(FUTURE_EXAM_QUERY, self.serialno)
            self._has_exam_booked = bool(cursor.fetchone()[0])
            cursor.close()

        return self._has_exam_booked

    def __repr__(self):
        return "'Patient_class instance - serialno %d'" % self.serialno

    @property
    def address(self):
        '''
        a printable address
        '''
        address = ""
        for line in (self.addr1, self.addr2, self.addr3,
                     self.town, self.county, self.pcde):
            if line.strip(" ") != "":
                address += "%s\n" % line.strip(" ")
        return address

    def getAge(self, on_date=None):
        '''
        return the age in form (year(int), months(int), isToday(bool))
        '''
        if on_date is None:
            # use today
            on_date = localsettings.currentDay()

        try:
            nextbirthday = datetime.date(on_date.year, self.dob.month,
                                         self.dob.day)
        except ValueError:
            # catch leap years!!
            nextbirthday = datetime.date(on_date.year, self.dob.month,
                                         self.dob.day - 1)

        ageYears = on_date.year - self.dob.year

        if nextbirthday > on_date:
            ageYears -= 1
            months = (12 - self.dob.month) + on_date.month
        else:
            months = on_date.month - self.dob.month
        if self.dob.day > on_date.day:
            months -= 1

        isToday = nextbirthday == localsettings.currentDay()

        return (ageYears, months, isToday)

    @property
    def ageYears(self):
        return self.getAge()[0]

    @property
    def age_course_start(self):
        '''
        returns a tuple (year, months) for the patient at accd
        '''
        return self.getAge(self.treatment_course.accd)[:2]

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

    def forget_fee_table(self):
        self._fee_table = None

    @property
    def fee_table(self):
        '''
        logic to determine which feeTable should be used for standard items
        '''
        if self._fee_table is None:
            if self.treatment_course.accd is None:
                cse_accd = localsettings.currentDay()
            else:
                cse_accd = self.treatment_course.accd
            for table in reversed(localsettings.FEETABLES.tables.values()):
                LOGGER.debug(
                    "checking feescale %s to see if suitable a feetable",
                    table)

                start, end = table.startDate, table.endDate
                LOGGER.debug("categories, start, end = %s, %s, %s",
                             table.categories, start, end)
                if end is None:
                    end = localsettings.currentDay()

                if self.cset in table.categories and start <= cse_accd <= end:
                    self._fee_table = table

            if self._fee_table is None:
                # - no matching table found, use the default.
                LOGGER.warning("NO SUITABLE FEETABLE FOUND, RETURNING DEFAULT")
                self._fee_table = localsettings.FEETABLES.default_table

        return self._fee_table

    def getEsts(self):
        '''
        get estimate data
        '''
        self.estimates = db_estimates.get_ests(self.serialno, self.courseno0)
        self.est_logger = EstLogger(self.courseno0)

    def getSynopsis(self):
        '''
        the synopsis line is displayed on the clinical summary page
        '''
        db = connect.connect()
        cursor = db.cursor()
        try:
            if cursor.execute(SYNOPSIS_QUERY, (self.serialno,)):
                self.synopsis = cursor.fetchall()[-1][0]
        except connect.OperationalError:
            # - necessary because the column is missing is db schema 1.4
            LOGGER.warning("invalid schema for getSynopsis")

    @property
    def underTreatment(self):
        '''
        a boolean value stating whether the patient has a continuing treatment
        plan
        '''
        return (self.treatment_course is not None and
                self.treatment_course.underTreatment)

    @property
    def max_tx_courseno(self):
        '''
        a patient who has had many courses of treatment, this gets the
        latest
        '''
        return self.treatment_course.max_tx_courseno

    @property
    def newer_course_found(self):
        '''
        check for a newer course in the currtrtmt2 table than the one loaded
        at startup.
        '''
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
        quadrant = tooth[:2]
        pos = int(tooth[2]) - 1                 # will be 0-7
        if quadrant == "ul":
            var = self.dent1
            pos = 7 - pos
        elif quadrant == "ur":
            var = self.dent0
        elif quadrant == "ll":
            var = self.dent2
        else:  # lr
            var = self.dent3
            pos = 7 - pos
        existing = dec_perm.fromSignedByte(var)
        if existing[pos] == "1":
            existing = existing[:pos] + "0" + existing[pos + 1:]
        else:
            existing = existing[:pos] + "1" + existing[pos + 1:]
        if quadrant == "ul":
            self.dent1 = dec_perm.toSignedByte(existing)
        elif quadrant == "ur":
            self.dent0 = dec_perm.toSignedByte(existing)
        elif quadrant == "ll":
            self.dent2 = dec_perm.toSignedByte(existing)
        else:  # lr
            self.dent3 = dec_perm.toSignedByte(existing)
        self.updateChartgrid()

    def updateChartgrid(self):
        '''
        a legacy issue with openmolar is the way teeth are saved as present
        is as 4 bytes (32 bits = 32 teeth). very frugal storage, but requires
        a fair deal of client computation :(
        '''
        grid = ""
        for quad in (self.dent1, self.dent0, self.dent3, self.dent2):
            grid += dec_perm.fromSignedByte(quad)
        for pos in mouth:
            if grid[mouth.index(pos)] == "0":
                self.chartgrid[pos] = pos
            else:
                self.chartgrid[pos] = decidmouth[mouth.index(pos)]

    def apply_fees(self):
        '''
        update the money owed.
        '''
        LOGGER.debug("Applying Fees")
        if "N" in self.cset:
            self.money0 = self.dbstate.money0 + self.fees_accrued
        else:
            self.money1 = self.dbstate.money1 + self.fees_accrued

    @property
    def fees(self):
        '''
        calculate what money is due.
        '''
        return int(self.money0 + self.money1 + self.money9 + self.money10 +
                   self.money11 - self.money2 - self.money3 - self.money8)

    @property
    def fees_accrued(self):
        '''
        what fees have changed since load.
        '''
        old_estimate_charges = 0
        if self.courseno0 == self.dbstate.courseno0:
            old_estimate_charges = self.dbstate.estimate_charges

        accrued_fees = self.estimate_charges - old_estimate_charges
        LOGGER.debug("fees_accrued = (new-existing) = %d - %d = %d",
                     self.estimate_charges, old_estimate_charges, accrued_fees)
        return accrued_fees

    @property
    def estimate_charges(self):
        '''
        charges for all completed treatments.
        '''
        charges = 0
        for est in self.estimates:
            if est.completed == 2:
                charges += est.ptfee
            elif est.completed == 1:
                charges += est.interim_pt_fee
        return charges

    @property
    def est_logger_text(self):
        '''
        a summary of the estimate for use in the est_logger_table
        est_logger is unconcerned whether treatment is completed etc..
        '''
        text = ""
        total, p_total = 0, 0
        for estimate in sorted(self.estimates):
            text += estimate.log_text
            total += estimate.fee
            p_total += estimate.ptfee
        text += "TOTAL ||  ||  ||  ||  ||  || %s || %s" % (total, p_total)
        return text

    def resetAllMonies(self):
        '''
        gets money1 and money 0 from apply_fees,
        then equalises money3 and money2 accordingly.
        zero's everything else
        money11 (bad debt) is left unaltered.
        '''
        self.dbstate.money0 = 0
        self.dbstate.money1 = 0
        self.monies_reset = True

        self.money0 = 0
        self.money1 = 0
        self.apply_fees()
        self.money9 = 0
        self.money10 = 0
        self.money2 = self.money0
        self.money3 = self.money1
        self.money8 = 0

    def nhs_claims(self, completed_only=True):
        '''
        nhs items from the estimates.
        if completed_only is False, then include planned items.
        '''
        claims = []
        for est in self.estimates:
            if est.csetype.startswith("N") and \
                    (not completed_only or est.completed == 2):
                claims.append(est)
        return claims

    def addHiddenNote(self, ntype, note="", attempt_delete=False,
                      one_only=False):
        '''
        re-written for schema 1.9
        '''
        LOGGER.info(
            "addHiddenNote - ntype='%s',note='%s', attempt_delete='%s'",
            ntype, note, attempt_delete
        )

        HN = ()
        if ntype == "payment":
            HN = ("RECEIVED: ", note)
        elif ntype == "printed":
            HN = ("PRINTED: ", note)
        elif ntype == "exam":
            HN = ("TC: EXAM", note)
        elif ntype == "chart_treatment":
            HN = ("TC:", note)
        elif ntype == "perio_treatment":
            HN = ("TC: PERIO", note)
        elif ntype == "xray_treatment":
            HN = ("TC: XRAY", note)
        elif ntype == "treatment":
            HN = ("TC: OTHER", note)
        elif ntype == "mednotes":  # other treatment
            HN = ("UPDATED:Medical Notes", note)
        elif ntype == "close_course":
            HN = ("COURSE CLOSED", "=" * 10)
        elif ntype == "open_course":
            HN = ("COURSE OPENED", "= " * 5)
        elif ntype == "resume_course":
            HN = ("COURSE RE-OPENED", "= " * 5)
        elif ntype == "fee":
            HN = ("INTERIM: ", note)

        if not HN:
            LOGGER.warning(
                "unable to add Hidden Note notetype '%s' not found", ntype)
            return

        reversing_note = ("UNCOMPLETED", "{%s}" % note)

        if attempt_delete:
            try:
                self.HIDDENNOTES.remove(HN)
            except ValueError:
                LOGGER.debug("'%s' not in hiddenotes", HN)
                LOGGER.debug(self.HIDDENNOTES)
                self.HIDDENNOTES.append(reversing_note)
        else:
            try:
                self.HIDDENNOTES.remove(reversing_note)
            except ValueError:
                self.HIDDENNOTES.append(HN)

        if one_only:
            while self.HIDDENNOTES.count(HN) > 1:
                self.HIDDENNOTES.remove(HN)

    def clearHiddenNotes(self):
        '''
        reset self.HIDDENNOTES
        '''
        self.HIDDENNOTES = []

    def updateBilling(self, tone):
        '''
        update the last billdate and tone of invoice
        '''
        self.billdate = localsettings.currentDay()
        self.billct += 1
        self.billtype = tone

    def reset_billing(self):
        '''
        if patients account is now is order, reset all billing params
        '''
        if self.fees == 0:
            self.billdate = None
            self.billct = None
            self.billtype = None

    def treatmentOutstanding(self):
        '''
        does the patient have treatmentOutstanding?
        returns a boolean
        '''
        return (self.treatment_course and
                self.treatment_course.has_treatment_outstanding)

    def checkExemption(self):
        '''
        see if the patient's exemption requires removal.
        '''
        if (self.exemption == "S" and
                self.getAge(self.treatment_course.accd)[0] > 19):
            self.exemption = ""
            self.load_warnings.append(_("Student Exemption removed"))
        elif (self.exemption == "A" and
              self.getAge(self.treatment_course.accd)[0] > 18):
            self.exemption = ""
            self.load_warnings.append(_("Age Exemption removed"))
        else:
            return True

    @property
    def name_id(self):
        '''
        name and serialno
        '''
        return u"%s - %s" % (self.name, self.serialno)

    @property
    def name(self):
        '''
        patients name in a readable form
        '''
        return u"%s %s %s" % (self.title, self.fname, self.sname)

    @property
    def psn(self):
        '''
        previous surname
        '''
        try:
            return self.previous_surnames[0]
        except IndexError:
            return ""

    @property
    def previous_surnames(self):
        '''
        previous surnames are stored.
        ## TODO - check this is used.
        '''
        if self._previous_surnames is None:
            db = connect.connect()
            cursor = db.cursor()
            cursor.execute(PSN_QUERY, (self.serialno,))
            self._previous_surnames = [s[0] for s in cursor.fetchall()]
            cursor.close()
        return self._previous_surnames

    @property
    def n_family_members(self):
        '''
        how many members are linked to this patient's familyno
        '''
        if self._n_family_members is None:
            db = connect.connect()
            cursor = db.cursor()
            cursor.execute(FAMILY_COUNT_QUERY, (self.familyno,))
            self._n_family_members = cursor.fetchone()[0]

        return self._n_family_members

    @property
    def under_capitation(self):
        '''
        under capitation if regular NHS patient and under 18.
        '''
        if self.cset != "N":
            return False
        years, months = self.age_course_start

        return years < 17 or (years == 17 and months < 11)

    def new_tx_course(self, new_courseno):
        '''
        start a new treatment course
        '''
        self.courseno0 = new_courseno
        self.treatment_course = TreatmentCourse(self.serialno, new_courseno)

    @property
    def COPIED_ATTRIBUTES(self):
        '''
        these are what is copied over into pt.dbstate
        '''
        return (patient_query_atts + exemptionTableAtts + bpeTableAtts +
                clinical_memos + ("fees", "estimate_charges", "serialno",
                                  "estimates", "appt_prefs",
                                  "treatment_course", "chartgrid"))

    @property
    def USER_CHANGEABLE_ATTRIBUTES(self):
        '''
        the attributes, common to pt and the object copy pt.db_state
        which is generated during take_snapshot
        used to determine whether the patient has been edited.
        '''
        for att_ in self.COPIED_ATTRIBUTES:
            # if att_ not in ("treatment_course", "estimates", "chartgrid"):
            yield att_

    @property
    def changes(self):
        '''
        what has changed since the patient was loaded
        '''
        changes = []
        for att_ in self.USER_CHANGEABLE_ATTRIBUTES:
            new_value = self.__dict__.get(att_, "")
            db_value = self.dbstate.__dict__.get(att_, "")
            if new_value != db_value:
                message = "Altered pt.%s" % att_.ljust(20)
                if att_ not in ("treatment_course", "estimates"):
                    message += (
                        " ORIG = '%s' NEW = '%s'" % (db_value, new_value))
                LOGGER.debug(message)
                changes.append(att_)
        return changes

    def take_snapshot(self):
        '''
        create a snapshot of this class, copying all attributes that the
        user can change
        '''
        memo = {}
        cls = self.__class__
        snapshot = cls.__new__(cls)
        memo[id(self)] = snapshot
        for att_, val_ in self.__dict__.items():
            if att_ in self.COPIED_ATTRIBUTES:
                setattr(snapshot, att_, deepcopy(val_, memo))
        self.dbstate = snapshot

        LOGGER.debug("snapshot of %s taken" % self)

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
        '''
        if the initial state has no course, or a lower course number,
        this is true.
        '''
        if self.treatment_course and self.dbstate.treatment_course is None:
            return True
        return (self.treatment_course.courseno !=
                self.dbstate.treatment_course.courseno)

    @property
    def tx_hash_tups(self):
        '''
        a list of unique hashes of all treatment on the current treatment plan
        returns a tuple (unique hash, attribute, treatment)
        '''
        for hash_, att_, tx in self.treatment_course._get_tx_hashes():
            if re.match("[ul][lr][1-8]", att_):
                att_ = self.chartgrid.get(att_)
            yield hash_, att_, tx

    @property
    def completed_tx_hash_tups(self):
        for hash_, att_, tx in self.treatment_course.completed_tx_hash_tups:
            if re.match("[ul][lr][1-8]", att_):
                att_ = self.chartgrid.get(att_)
            yield hash_, att_, tx

    @property
    def completed_tx_hashes(self):
        return list(self.treatment_course.completed_tx_hashes)

    @property
    def planned_tx_hash_tups(self):
        return self.treatment_course.planned_tx_hash_tups

    @property
    def has_planned_perio_txs(self):
        for hash_, att_, tx in self.planned_tx_hash_tups:
            if att_ == "perio":
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

    @property
    def address_tuple(self):
        return (self.sname, self.addr1, self.addr2,
                self.addr3, self.town, self.county,
                self.pcde, self.tel1)

    def set_record_in_use(self):
        records_in_use.set_in_use(self.serialno)

    def lock_record_in_use(self):
        records_in_use.set_locked(self.serialno)

    def clear_lock(self):
        records_in_use.clear_lock(self.serialno)


if __name__ == "__main__":
    # testing stuff
    try:
        serialno = int(sys.argv[-1])
    except ValueError:
        serialno = 1

    LOGGER.setLevel(logging.DEBUG)

    if "-v" in sys.argv:
        verbose = True
    else:
        verbose = False

    pt = patient(serialno)
    if verbose:
        for att in sorted(pt.__dict__.keys()):
            print "%s '%s'" % (att.ljust(20), pt.__dict__[att])

    localsettings.loadFeeTables()
    print pt.fee_table

    pt.take_snapshot()
    print list(pt.tx_hash_tups)

    print pt.treatment_course
    print pt.ageYears
    print pt.age_course_start
    print pt.under_capitation
