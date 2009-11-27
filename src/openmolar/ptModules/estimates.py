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

class est():
    '''
    this class has attributes suitable for storing in the estimates table
    '''
    def __init__(self):
        self.ix = None
        self.serialno = None
        self.courseno = None
        self.category = ""
        self.type = ""
        self.number = None
        self.itemcode = "4001"
        self.description = None
        self.fee = None
        self.ptfee = None
        self.feescale = None
        self.csetype = None
        self.dent = None
        self.completed = None
        self.carriedover = None
        self.linked = False
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        retarg=u"("
        for att in ("ix","serialno","courseno","number","fee","ptfee","dent"):
            retarg+='%s ,'%self.__dict__[att]
        for att in ("category","type","itemcode","description","csetype",
        "feescale"):
            retarg+='"%s" ,'%self.__dict__[att]
        for att in ("completed","carriedover"):
            retarg+="%s ,"%self.__dict__[att]
        return "%s)"% retarg.strip(",")

    def toHtmlRow(self):
        return '''<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>
        <td>%s</td><td>%s</td><td>%s</td>
        <td>%s</td><td>%s</td><td>%s</td></tr>'''%(
        localsettings.ops.get(self.dent),self.number,self.itemcode,
        self.category, self.type,
        self.description,localsettings.formatMoney(self.fee),
        localsettings.formatMoney(self.ptfee),self.feescale,
        self.csetype,self.completed)

    def htmlHeader(self):
        return '''<tr><th>Dentist</th><th>number</th><th>code</th>
        <th colspan="2">Type</th><th>Description</th><th>fee</th>
        <th>pt fee</th><th>feescale</th><th>cset</th><th>completed</th></tr>'''
        
    def filteredDescription(self):
        '''
        removes {1 of 3} from the description
        '''
        retarg = copy.copy(self.description)
        gunks = re.findall(" {.*}", retarg)        
        for gunk in gunks:
            retarg = retarg.replace(gunk, "") 
        return retarg
    

def strip_curlies(description):
    '''
    comments such as {2 of 2} are present in the estimates...
    this removes such stuff
    '''
    if re.search("{.*}", description):
        return description[:description.index("{")]
    else:
        return description
    
def sorted(ests):
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
    
def toothTreatDict(pt):
    '''
    cycles through the patient attriubutes,
    and brings up planned / completed treatment on teeth only
    '''
    treats={"pl":[], "cmp":[]}
    for quadrant in ("ur","ul", "ll", "lr"):
        if "r" in quadrant:
            order = (8, 7, 6, 5, 4, 3, 2, 1)
        else:
            order = (1, 2, 3, 4, 5, 6, 7, 8)
        for tooth in order:
            for type in ("pl", "cmp"):
                att="%s%s%s"%(quadrant, tooth,type)
                if pt.__dict__[att] != "":
                    items=pt.__dict__[att].strip(" ").split(" ")
                    for item in items:
                        treats[type].append(("%s%s"%(quadrant, tooth), item), )
    #print "toothTreatDict"
    #print "returning ",treats
    return treats

@localsettings.debug
def recalculate_estimate(pt):
    '''
    re look up all the itemcodes in the patients feetable 
    (which could have changed, or maybe we have been informed of an exemption?)
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
    for number, itemcode, cset, category, type, descrpt, complete \
    in codeList:
        est = pt.addToEstimate(number, itemcode, dent, cset, category, type,
        descr = descrpt, completed=complete)
        if est.completed:
            pt.applyFee(est.ptfee)
    
    return True
    
def estimateFromPlan(pt):
    '''
    the idea here is that this iterates through the plan and completed    
    and gets new itemcodes for estimates....
    '''
    planned = plan.plannedDict(pt)
    completed = plan.completedDict(pt)
    if pt.dnt2 != 0:
        dent = pt.dnt2
    else:
        dent = pt.dnt1
    
    for key in planned.keys():
        print key,planned[key]
    for key in completed.keys():
        print key,completed[key]
        
        
    #pt.addToEstimate(1, treat[1], treat[2], treat[3], treat[4],
    #                        dent, self.pt.cset, treat[0])


def toBriefHtml(pt):
    '''
    returns an HTML table showing the estimate in a receptionist friendly format
    '''
    retarg = u'<html><body>'
    if pt.underTreatment:
        retarg += _("<h1>Under Treatment - Current Estimate</h1>")
    else:
        retarg += _("<h1>Estimate from previous course</h1>")
        
    if not pt.estimates:
        retarg += _('No estimate data found</body></html>')
        return retarg
    
    retarg += _('''<table width ="100%" border="1">
    <tr><td colspan="7"><h3>ESTIMATE</h3></td></tr>
    <tr><th>No.</th><th>Description</th><th>Category</th>
    <th>Type</th><th>Course</th>
    <th>Fee</th><th>Pt Fee</th><th>Completed</th></tr>''')
    total=0
    pt_total=0
    for est in sorted(pt.estimates):
        total+=est.fee
        pt_total+=est.ptfee
        retarg+='<tr><td>%s</td><td>%s</td>'%(est.number ,est.description)
        retarg+='<td align="center">%s</td>'%est.category        
        retarg+='<td align="center">%s</td>'%est.type
        if est.csetype==None:
            retarg+='<td align="center">?</td>'
        else:
            retarg+='<td align="center">%s</td>'%est.csetype

        retarg+='<td align="right">%s</td>'% (
        localsettings.formatMoney(est.fee))
        
        retarg+='<td align="right"><b>%s</b></td>'%(
        localsettings.formatMoney(est.ptfee))
        
        retarg+='<td align="center">'
        if est.completed:
            retarg+='YES'
        else:
            retarg+='NO'
        retarg+="</td></tr>"

    retarg+='<tr><td colspan="5"></td>'
    retarg+='<td align="right">%s</td>'% localsettings.formatMoney(total)
    retarg+='<td align="right"><b>%s</b></td>'% (
    localsettings.formatMoney(pt_total))
    
    retarg+='<td></td></tr>'

    retarg+='</table></body></htsml>'

    return retarg

if __name__ == "__main__":
    from openmolar.dbtools import patient_class
    localsettings.initiate(False)
    try:
        serialno = int(sys.argv[len(sys.argv)-1])
    except:
        serialno = 23664

    pt = patient_class.patient(serialno)
    print str(pt.estimates)
    #print toHtml(pt.estimates,pt.tsfees)

    #print toBriefHtml(pt.estimates)
    
    #recalculate_estimate(pt)