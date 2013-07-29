# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

from __future__ import division
import copy
import re
import sys

from openmolar.settings import localsettings
from openmolar.ptModules import plan

import struct

class Estimate(object):
    '''
    this class has attributes suitable for storing in the estimates table
    '''
    def __init__(self):
        self.ix = None
        self.serialno = None
        self.courseno = None
        self.number = None
        self.itemcode = "4001"
        self.description = None
        self.fee = None
        self.ptfee = None
        self.feescale = None
        self.csetype = None
        self.dent = None
        self.completed = None
        
        self.tx_hashes = []

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        retarg=u"("
        for att in ("ix","serialno","courseno","number","fee","ptfee","dent"):
            retarg+='%s ,'% self.__dict__[att]
        for att in ("tx_hashes","itemcode","description","csetype","feescale"):
            retarg+='"%s" ,'% self.__dict__[att]
        retarg += "%s"% self.__dict__["completed"]
        return "%s)"% retarg
    
    def __eq__(self, other):
        return str(self) == str(other)

    def toHtmlRow(self):
        return '''<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>
        <td>%s</td><td>%s</td><td>%s</td>
        <td>%s</td><td>%s</td></tr>'''%(
        localsettings.ops.get(self.dent), self.number, self.itemcode,
        self.description, localsettings.formatMoney(self.fee),
        localsettings.formatMoney(self.ptfee),self.feescale,
        self.csetype, self.completed, str(self.tx_hashes))

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
        return bool(re.match("01[012]1$", self.itemcode))

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
        if est.completed:
            pt.applyFee(est.ptfee * -1)

        if maxCharge - total >= est.ptfee:
            pass
        else:
            if maxCharge - total > 0:
                est.ptfee = maxCharge - total
            else:
                est.ptfee = 0
        total += est.ptfee

        if est.completed:
            pt.applyFee(est.ptfee)
    return True


def recalculate_estimate(pt):
    '''
    look up all the itemcodes in the patients feetable
    (which could have changed), and apply new fees
    '''
    dent = pt.dnt1
    if pt.dnt2 and pt.dnt2 != "":
        dent = pt.dnt2

    codeList=[]
    for est in pt.estimates:
        codeList.append((est.number, est.itemcode, est.csetype,
        est.category, est.type, est.description , est.completed))
        if est.completed:
            pt.applyFee(est.ptfee * -1)

    pt.estimates = []
    for number, itemcode, cset, category, type_, descrpt, complete \
    in codeList:
        est = pt.addToEstimate(number, itemcode, dent, cset, category, type_,
        descr = descrpt, completed=complete)
        if est.completed:
            pt.applyFee(est.ptfee)

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

    #recalculate_estimate(pt)