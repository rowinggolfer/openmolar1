# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

from copy import deepcopy
import logging
import re

from openmolar import connect
from openmolar.settings import localsettings

LOGGER = logging.getLogger("openmolar")

CURRTRT_NON_TOOTH_ATTS = ('xray', 'perio', 'anaes',
'other', 'ndu', 'ndl', 'odu', 'odl', 'custom')

CURRTRT_ROOT_ATTS = CURRTRT_NON_TOOTH_ATTS + (
'ur8', 'ur7', 'ur6', 'ur5', 'ur4', 'ur3', 'ur2', 'ur1', 'ul1',
'ul2', 'ul3', 'ul4', 'ul5', 'ul6', 'ul7', 'ul8', 'll8', 'll7', 'll6', 'll5',
'll4', 'll3', 'll2', 'll1', 'lr1', 'lr2', 'lr3', 'lr4', 'lr5', 'lr6', 'lr7',
'lr8')

CURRTRT_ATTS=('courseno','xraypl','periopl','anaespl','otherpl',
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

QUERY = "SELECT "
for field in CURRTRT_ATTS:
    QUERY += "%s, "% field
QUERY = QUERY.rstrip(", ")
QUERY += " from currtrtmt2 where serialno=%s and courseno=%s"


class TreatmentCourse(object):
    def __init__(self, sno, courseno):
        '''
        initiate the class with default variables, then load from database
        '''
        self.dbstate = None
        self.serialno = sno
        self.courseno = courseno
        self.xraypl = ''
        self.periopl = ''
        self.anaespl = ''
        self.otherpl = ''
        self.ndupl = ''
        self.ndlpl = ''
        self.odupl = ''
        self.odlpl = ''
        self.custompl = ''
        self.xraycmp = ''
        self.periocmp = ''
        self.anaescmp = ''
        self.othercmp = ''
        self.nducmp = ''
        self.ndlcmp = ''
        self.oducmp = ''
        self.odlcmp = ''
        self.customcmp = ''
        self.ur8pl = ''
        self.ur7pl = ''
        self.ur6pl = ''
        self.ur5pl = ''
        self.ur4pl = ''
        self.ur3pl = ''
        self.ur2pl = ''
        self.ur1pl = ''
        self.ul1pl = ''
        self.ul2pl = ''
        self.ul3pl = ''
        self.ul4pl = ''
        self.ul5pl = ''
        self.ul6pl = ''
        self.ul7pl = ''
        self.ul8pl = ''
        self.ll8pl = ''
        self.ll7pl = ''
        self.ll6pl = ''
        self.ll5pl = ''
        self.ll4pl = ''
        self.ll3pl = ''
        self.ll2pl = ''
        self.ll1pl = ''
        self.lr1pl = ''
        self.lr2pl = ''
        self.lr3pl = ''
        self.lr4pl = ''
        self.lr5pl = ''
        self.lr6pl = ''
        self.lr7pl = ''
        self.lr8pl = ''
        self.ur8cmp = ''
        self.ur7cmp = ''
        self.ur6cmp = ''
        self.ur5cmp = ''
        self.ur4cmp = ''
        self.ur3cmp = ''
        self.ur2cmp = ''
        self.ur1cmp = ''
        self.ul1cmp = ''
        self.ul2cmp = ''
        self.ul3cmp = ''
        self.ul4cmp = ''
        self.ul5cmp = ''
        self.ul6cmp = ''
        self.ul7cmp = ''
        self.ul8cmp = ''
        self.ll8cmp = ''
        self.ll7cmp = ''
        self.ll6cmp = ''
        self.ll5cmp = ''
        self.ll4cmp = ''
        self.ll3cmp = ''
        self.ll2cmp = ''
        self.ll1cmp = ''
        self.lr1cmp = ''
        self.lr2cmp = ''
        self.lr3cmp = ''
        self.lr4cmp = ''
        self.lr5cmp = ''
        self.lr6cmp = ''
        self.lr7cmp = ''
        self.lr8cmp = ''
        self.examt = ''
        self.examd = ''
        self.accd = None
        self.cmpd = None

        if self.courseno == 0:
            return

        db = connect.connect()
        cursor = db.cursor()
        self.getCurrtrt()
        cursor.close()

    def __repr__(self):
        message = "TreatmentCourse for patient %s courseno %s\n"% (
            self.serialno, self.courseno)

        for att in CURRTRT_ATTS:
            value = self.__dict__.get(att, "")
            if value != "":
                message += "   %s,%s\n"% (att, value)
        return message

    def __cmp__(self, other):
        return cmp(unicode(self), unicode(other))

    def _non_tooth_items(self, suffix="pl"):
        for att in CURRTRT_NON_TOOTH_ATTS:
            value = self.__dict__.get(att+suffix, "")
            if value != "":
                txs = value.split(" ")
                for tx in set(txs):
                    if tx != "":
                        n = txs.count(tx)
                        if n != 1:
                            tx = "%d%s"% (n, tx)
                        yield att, tx

    @property
    def non_tooth_plan_items(self):
        return list(self._non_tooth_items("pl"))

    @property
    def non_tooth_cmp_items(self):
        items = []
        if self.examt != "" and self.examd:
            items.append(("exam", self.examt))
        return items + list(self._non_tooth_items("cmp"))

    def getCurrtrt(self):
        db = connect.connect()
        cursor = db.cursor()

        cursor.execute(QUERY, (self.serialno, self.courseno))

        for value in cursor.fetchall():
            for i, field in enumerate(CURRTRT_ATTS):
                self.__dict__[field] = value[i]
                #LOGGER.debug("getCurrtrt '%s' = '%s'"% (field, value[i]))
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

    @property
    def has_exam(self):
        return self.examt != "" and self.examd

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

    @property
    def has_treatment_outstanding(self):
        for att in CURRTRT_ATTS:
            if att[-2:] == "pl":
                if self.__dict__[att] != "":
                    return True
        return False

    @property
    def tx_hashes(self):
        return self._get_tx_hashes()

    @property
    def completed_tx_hashes(self):
        return self._get_tx_hashes(True)

    @property
    def planned_tx_hashes(self):
        for tup in self._get_tx_hashes():
            if not tup in self.completed_tx_hashes:
                yield tup

    def _get_tx_hashes(self, completed_only=False):
        '''
        returns a tuple (unique hash, attribute, treatment)
        hashes will be unique as multiple identical items are indexed
        eg. eg "perio SP AC SP " is hashed as follows
        "%sperio1SP"% courseno
        "%sperio2SP"% courseno
        "%sperio1AC"% courseno
        '''
        if self.examt != "":
            hash_ = hash("%sexam1%s"% (self.courseno, self.examt))
            yield (str(hash_), "exam", self.examt)
        else:
            LOGGER.debug(
            "no exam to be yielded as TreatmentCourse.examt='%s'" % self.examt)

        for att in CURRTRT_ROOT_ATTS:
            treats = self.__dict__[att+"cmp"]
            if not completed_only:
                treats += " " + self.__dict__[att+"pl"]
            treat_list = sorted(treats.split(" "))
            prev_tx, count = None, 1
            for tx in treat_list:
                if tx == "":
                    continue
                if tx != prev_tx:
                    count = 1
                    prev_tx = tx
                else:
                    count += 1
                hash_ = hash("%s%s%s%s"% (self.courseno, att, count, tx))
                yield (str(hash_), att, tx+" ")

    def get_tx_from_hash(self, hash_):
        '''
        example
        imput a hash 039480284098
        get back ("ur1", "M")
        '''
        for tx_hash in self.tx_hashes:
            if tx_hash[0] == hash_:
                return tx_hash[1], tx_hash[2]
        LOGGER.warning("couldn't find treatment %s"% hash_)
        LOGGER.debug("listing existing hashes")
        for tx_hash in self.tx_hashes:
            LOGGER.debug(tx_hash)
        return None, None

    def pl_txs(self, att):
        '''
        returns the list of treatments currently planned for this attribute.
        eg pl_txs("ul8") may return ["O", "B,CO"]
        '''
        txs = self.__dict__["%spl"%att].split(" ")
        while "" in txs:
            txs.remove("")
        return txs

    def cmp_txs(self, att):
        '''
        returns the list of treatments currently planned for this attribute.
        eg pl_txs("ul8") may return ["O", "B,CO"]
        '''
        txs = self.__dict__["%scmp"%att].split(" ")
        while "" in txs:
            txs.remove("")
        return txs

    def all_txs(self, att):
        '''
        returns the list of treatments currently associated with an attribute.
        eg all_txs("ul8") may return ["O", "B,CO"]
        '''
        return self.cmp_txs(att) + self.pl_txs(att)

if __name__ =="__main__":
    '''
    testing stuff
    '''

    TEST_SNO = 11956
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute("select courseno0 from patients where serialno = %s",
        (TEST_SNO,))
    courseno = cursor.fetchone()[0]
    cursor.close()

    tc = TreatmentCourse(TEST_SNO, 0)
    print tc
    print tc.underTreatment

    tc = TreatmentCourse(TEST_SNO, courseno)
    print tc

    print tc.non_tooth_plan_items
    print tc.non_tooth_cmp_items
    print tc.all_txs("ur5")

