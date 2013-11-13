# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

from __future__ import division
import copy
import logging
import re
import sys

from openmolar.settings import localsettings
from openmolar.ptModules import plan

LOGGER = logging.getLogger("openmolar")

class TXHash(object):
    def __init__(self, hash_, completed=False):
        self.hash = str(hash_)
        self.completed = completed

    def __eq__(self, other):
        '''
        compare the object with another hash
        note - completion state is irrelevant
        '''
        if type(other) == TXHash:
            return self.hash == other.hash
        return self.hash == other

    def __repr__(self):
        return ("TXHash %s completed=%s"% (self.hash, self.completed))

class Estimate(object):
    '''
    this class has attributes suitable for storing in the estimates table
    '''
    COMPLETED = 2
    PARTIALLY_COMPLETED = 1
    PLANNED = 0
    def __init__(self):
        self.ix = None
        self.serialno = None
        self.courseno = None
        self.number = 1
        self.itemcode = "-----"
        self.description = None
        self.fee = None
        self.ptfee = None
        self.feescale = None
        self.csetype = None
        self.dent = None

        self.tx_hashes = []

    def __cmp__(self, other):
        '''
        this function enables sorting for the estimate widget.
        the replacement of "-" with "Z" ensures that "other" items are last
        '''
        return cmp(
        self.itemcode.replace("-", "Z"), other.itemcode.replace("-", "Z"))

    @property
    def completed(self):
        '''
        returns a tri-state value.
        0 = nothing completed
        1 = some treatments completed
        2 = all related treatments completed
        '''
        all_planned, all_completed = True, True
        for tx_hash in self.tx_hashes:
            all_planned = all_planned and not tx_hash.completed
            all_completed = all_completed and tx_hash.completed

        if all_planned:
            return 0
        if all_completed:
            return 2
        return 1

    @property
    def interim_fee(self):
        if self.tx_hashes == []:
            return 0
        return self.fee//len(self.tx_hashes)

    @property
    def interim_pt_fee(self):
        if self.tx_hashes == []:
            return 0
        return self.ptfee//len(self.tx_hashes)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "\nEstimate\n        (%s %s %s %s %s %s %s %s %s %s %s %s)"% (
            self.ix,
            self.serialno,
            self.courseno,
            self.number,
            self.fee,
            self.ptfee,
            self.dent,
            self.tx_hashes,
            self.itemcode,
            self.description,
            self.csetype,
            self.feescale)

    @property
    def log_text(self):
        '''
        estimate data formatted so as to be useful in a log
        || can be used to separate values
        '''
        return "%s || %s || %s || %s || %s || %s || %s || %s||\n"% (
            self.number, self.itemcode, self.description, self.csetype,
            self.feescale, self.dent, self.fee, self.ptfee)

    def __eq__(self, other):
        return str(self) == str(other)

    def toHtmlRow(self):
        hash_string = ""
        for tx_hash in self.tx_hashes:
            hash_string += "<li>%s</li>"% tx_hash.hash
        if hash_string:
            hash_string = "<ul>%s</ul>"% hash_string
        else:
            hash_string = _("no treatments")

        if self.completed == 2:
            completed = _("Yes")
        elif self.completed == 1:
            completed = _("Partially")
        else:
            completed = _("No")
        return '''
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>
            '''%(
        localsettings.ops.get(self.dent),
        self.number,
        self.itemcode,
        self.description,
        localsettings.formatMoney(self.fee),
        localsettings.formatMoney(self.ptfee),
        self.feescale,
        self.csetype,
        completed,
        hash_string)

    def htmlHeader(self):
        return '''<tr><th>Dentist</th><th>number</th><th>code</th>
        <th>Description</th><th>fee</th>
        <th>pt fee</th><th>feescale</th><th>cset</th><th>completed</th>
        <th>Hashes</th></tr>'''

    def filteredDescription(self):
        '''
        removes {1 of 3} from the description
        '''
        retarg = copy.copy(self.description)
        gunks = re.findall(" {.*}", retarg)
        for gunk in gunks:
            retarg = retarg.replace(gunk, "")
        return retarg

    @property
    def is_exam(self):
        '''
        important that feescales use an itemcode that matches this!
        examples are 0101, 0111, 0121
        can also be prepended with a single character eg E0101
        '''
        try:
            return bool(re.match(".?01[012]1$", self.itemcode))
        except TypeError:
            return False

    @property
    def is_custom(self):
        return self.itemcode == "CUSTO"

    @property
    def has_one_tx(self):
        return len(self.tx_hashes) == 1

    @property
    def has_multi_txs(self):
        return len(self.tx_hashes) > 1

def strip_curlies(description):
    '''
    comments such as {2 of 2} are present in the estimates...
    this removes such stuff
    '''
    if re.search("{.*}", description):
        return description[:description.index("{")]
    else:
        return description

def sorted_estimates(ests):
    '''
    compresses a list of estimates down into number*itemcode
    '''
    def cmp1(a, b):
        'define how ests are sorted'
        return cmp(a.itemcode, b.itemcode)

    sortedEsts=[]
    def combineEsts(est):
        for se in sortedEsts:
            if se.itemcode == est.itemcode:
                if se.description == strip_curlies(est.description):
                    #--don't combine items where description has changed
                    if est.number != None and se.number != None:
                        se.number += est.number
                    se.fee += est.fee
                    se.ptfee += est.ptfee
                    se.type += "|" + est.type
                    return True
    for est in ests:
        if not combineEsts(est):
            ce = copy.copy(est)
            ce.description = strip_curlies(ce.description)
            sortedEsts.append(ce)
    sortedEsts.sort(cmp1)

    return sortedEsts

def apply_exemption(pt, maxCharge=0):
    '''
    apply an exemption
    '''
    total = 0
    for est in pt.estimates:
        if not "N" in est.csetype:
            continue

        if maxCharge - total >= est.ptfee:
            pass
        else:
            if maxCharge - total > 0:
                est.ptfee = maxCharge - total
            else:
                est.ptfee = 0
        total += est.ptfee

    return True


if __name__ == "__main__":
    from openmolar.dbtools import patient_class
    localsettings.initiate()
    try:
        serialno = int(sys.argv[len(sys.argv)-1])
    except:
        serialno = 23664

    pt = patient_class.patient(serialno)
    print str(pt.estimates)
    for estimate in pt.estimates:
        print estimate.toHtmlRow().encode("ascii", "replace")
