# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import datetime
import sys
from openmolar.settings import localsettings

CHART = { 
136:"UR8", 135:"UR7", 134:"UR6", 133:"UR5", 
132:"UR4", 131:"UR3", 130:"UR2", 129:"UR1", 
144:"UL1", 145:"UL2", 146:"UL3", 147:"UL4", 
148:"UL5", 149:"UL6", 150:"UL7", 151:"UL8", 
166:"LL8", 165:"LL7", 164:"LL6", 163:"LL5", 
162:"LL4", 161:"LL3", 160:"LL2", 159:"LL1", 
174:"LR1", 175:"LR2", 176:"LR3", 177:"LR4", 
178:"LR5", 179:"LR6", 180:"LR7", 181:"LR8", 
142:"URE", 141:"URD", 140:"URC", 139:"URB", 
138:"URA", 153:"ULA", 154:"ULB", 155:"ULC", 
156:"ULD", 157:"ULE", 172:"LLE", 171:"LLD", 
170:"LLC", 169:"LLB", 168:"LLA", 183:"LRA", 
184:"LRB", 185:"LRC", 186:"LRD", 187:"LRE"}


def notes(ptNotesTuple, verbosity=0):
    '''
    returns an html string of notes...
    if verbose=1 you get reception stuff too. 
    if verbose =2 you get full notes
    '''

    retarg = '''<html><head><link rel="stylesheet"
    href="%s" type="text/css"></head><body>'''% localsettings.stylesheet
    notes_dict = {}
    date = ""
    for line in ptNotesTuple:
        if len(line) > 0:
            notelist = decipher_noteline(line[1])
            if notelist[3] != "":
                date = notelist[3]
            if notes_dict.has_key(date):
                notes_dict[date].append(notelist[0:3])
            else:
                notes_dict[date] = [notelist[0:3]]
    dates = notes_dict.keys()
    dates.sort()
    retarg += '''<table width = "100%">
    <tr><th class = "date">Date</th><th class = "ops">ops</th>
    <th class = "tx">Tx</th><th class = "notes">Notes</th>'''
    
    if verbosity > 0:
        retarg += '<th class="reception">reception</th>'
    
    if verbosity == 2: #this is for development/debugging purposes
        retarg += '<th class="verbose">Detailed</th>'

    retarg += '</tr>'
    for key in dates:
        retarg += '''<tr><td class="date">%s</td><td class="ops">%s</td>
        <td class="tx">%s</td><td class="notes">%s</td>'''% (
        get_date_from_date(key), get_op_for_date(notes_dict[key]),
        get_codes_for_date(notes_dict[key]),
        get_notes_for_date(notes_dict[key]))

        ests = get_estimate_for_date(notes_dict[key])
        rec = get_reception_for_date(notes_dict[key])
        if verbosity > 0:
            retarg += '<td class="reception">'
            if rec != "" and ests == "":
                retarg += '%s</td>'% rec
            elif rec == "" and ests != "":
                retarg += '%s</td>'% ests
            else:
                retarg += "%s<br />%s</td>"% (ests, rec)
            
        if verbosity == 2:
            text = ""
            for item in notes_dict[key]:
                text += "%s<br />"% item
            retarg += "<td class=verbose>%s</td>"% text

        retarg += "</tr>"
        
    retarg += '</table></div>\n<a name="anchor"></a>END</body></html>'
    
    return retarg 

def get_date_from_date(key):
    '''
    converts to a readable date
    '''
    try:
        k = key.split('_')
        d = datetime.date(int(k[0]), int(k[1]), int(k[2]))
        return localsettings.formatDate(d)
        #return k[2]+"/"+k[1]+"/"+k[0]
    except IndexError:
        return "IndexERROR converting date %s" %key
    except ValueError:
        return "TypeERROR converting date %s" %key
        
def get_op_for_date(line):
    '''
    parse the line for an openerator
    '''
    op = ""
    for l in line:
        if l[2] != "" and not l[2] in op:
            op += "%s<br />"% l[2] 
    
    return op.strip("<br />")

def get_codes_for_date(line):
    code=""
    for l in line:
        if "TC" in l[0]:
            code+="<b>"
            tx=l[1]
            while len(tx)>8 and " " in tx[8:]:
                pos=tx.index(" ",8)
                code+="%s <br />"%tx[:pos]
                tx=tx[pos:]
            code+="%s </b>"%tx
    if code=="":
        return "-"
    else:
        return code
def get_notes_for_date(line):
    '''
    this is the actual user entered stuff!
    '''
    note=""
    for l in line:
        if "NOTE" in l[0]:
            mytext = l[1].replace("<","&lt;")
            mytext = mytext.replace(">","&gt;")
            note += "%s<br />"% mytext
    return note.strip("<br />")

def get_reception_for_date(line):
    '''
    was anything printed etc....
    '''
    recep = ""
    for l in line:
        if ("PRINT" in l[0]) or ("RECEIVED" in l[0]) or \
        ("FINAL" in l[0]) or ("UNKNOWN" in l[0]) or \
        ("UPDATE" in l[0]) or ("COURSE" in l[0]):
            recep+=l[0]+l[1]+"<br />"
    if recep=="":
        return "-"
    else:
        return recep.strip("<br />")
def get_estimate_for_date(line):
    est=""
    for l in line:
        if "ESTIMATE" in l[0]:
            est +="%s%s<br />"% (l[0],l[1])
    if est=="":
        return "-"
    else:
        return est.strip("<br />")

def decipher_noteline(noteline):
    '''
    returns a list.  ["type","note","operator","date"]
    '''        
    retarg=["","","",""]
    
    if len(noteline) == 0:  #sometimes a line is blank
       return retarg

    #important - this line give us operator and date.
    if noteline[0] == chr(1):
        retarg[0] = "opened"
        operator = ""
        i = 1
        while noteline[i] >= "A" or noteline[i] == "/":
            operator += noteline[i]
            i += 1

        ## arghh!!! 2 character year field!!!!!!
        workingdate = "%s_%02d_%02d"% (
        1900+char(noteline[i+2]),char(noteline[i+1]),char(noteline[i]))                                                                      

        retarg[2] = operator
        retarg[3] = workingdate
        try:
            systemdate = "%s/%s/%s"% (
            char(noteline[i+3]), char(noteline[i+4]), 
            1900 + char(noteline[i+5]))

            #systemdate includes time
            systemdate += " %02d:%02d"% (
            char(noteline[i+6]), char(noteline[i+7])) 

            retarg[1] += "System date - %s"% systemdate

        except IndexError, e:
            print "error getting system date for patient notes - %s", e
            retarg[1] += "System date - ERROR!!!!!"
            
    elif noteline[0] == "\x02":   #
        retarg[0] = "closed"
        operator = ""
        i = 1
        while noteline[i] >= "A" or noteline[i] == "/":
            operator += noteline[i]
            i += 1
        systemdate = "%s/%s/%s"%(
        char(noteline[i]), char(noteline[i+1]), 
        1900+char(noteline[i+2]))

        systemdate+=" %02d:%02d"%( 
        char(noteline[i+3]),char(noteline[i+4]))

        retarg[1] += "%s %s"% (operator, systemdate)
    
    elif noteline[0] == chr(3):        
        #-- hidden nodes start with chr(3) then another character
        if noteline[1]==chr(97):
            retarg[0]="COURSE CLOSED"
            retarg[1]="="*10
        elif noteline[1]==chr(100):
            retarg[0]="UPDATED:"
            retarg[1]="Medical Notes "+noteline[2:]
        elif noteline[1]==chr(101):
            retarg[0]="UPDATED:"
            retarg[1]="Perio Chart"
        elif noteline[1]==chr(104):
            retarg[0]="TC: XRAY"
            retarg[1]=noteline[2:]
        elif noteline[1]==chr(105):
            retarg[0]="TC: PERIO"
            retarg[1]=noteline[2:]
        elif noteline[1]==chr(107):
            retarg[0]="TC: OTHER"
            retarg[1]=noteline[2:]
        elif noteline[1]==chr(108):
            retarg[0]="TC: NEW Denture Upper"
            retarg[1]=noteline[2:]
        elif noteline[1]==chr(109):
            retarg[0]="TC: NEW Denture Lower"
            retarg[1]=noteline[2:]
        elif noteline[1]==chr(110):
            retarg[0]="TC: Existing Denture Upper"
            retarg[1]=noteline[2:]
        elif noteline[1]==chr(111):
            retarg[0]="TC: Existing Denture Lower"
            retarg[1]=noteline[2:]
        elif noteline[1]==chr(112):
            retarg[0]="TC: EXAM"
            retarg[1]=noteline[2:]
        elif noteline[1]==chr(113):
            retarg[0]="TC:"
            retarg[1]=tooth(noteline[2:])
        elif noteline[1]==chr(114):
            retarg[0]="STATIC: "                                    #(1st line):"
            retarg[1]=tooth(noteline[2:])
        elif noteline[1]==chr(115):
            retarg[0]="PRINTED: "
            retarg[1]="GP17(A)"
        elif noteline[1]==chr(116):
            retarg[0]="PRINTED: "
            retarg[1]="GP17(C)"
        elif noteline[1]==chr(117):
            retarg[0]="PRINTED: "
            retarg[1]="GP17(DC)"
        elif noteline[1]==chr(119):
            retarg[0]="RECEIVED: "
            retarg[1]=noteline[2:]
        elif noteline[1]==chr(120):
            retarg[0]="REVERSE PAYMENT:"
            retarg[1]=noteline[2:]
        elif noteline[1]==chr(121):
            retarg[0]="STATIC: "                                                                #(additional Line):"
            retarg[1]=tooth(noteline[2:])
        elif noteline[1]==chr(123):
            retarg[0]="PRINTED: "
            retarg[1]="GP17"
        elif noteline[1]==chr(124):
            retarg[0]="PRINTED: "
            retarg[1]="GP17PR"
        elif noteline[1]==chr(130):
            retarg[0]="ESTIMATE: "
            retarg[1]=noteline[2:]
        elif noteline[1]==chr(131):
            retarg[0]="INTERIM: "
            retarg[1]=noteline[2:]
        elif noteline[1]==chr(132):
            retarg[0]="FINAL: "
            retarg[1]=noteline[2:]
        elif noteline[1]==chr(133):
            retarg[0]="ACTUAL: "
            retarg[1]=tooth(noteline[2:])
        elif noteline[1]==chr(134):
            retarg[0]="FILED: "
            retarg[1]="Claim"
        elif noteline[1]==chr(136):
            retarg[0]="FILED: "
            retarg[1]="Registration"
        elif noteline[1]=="v":
            retarg[0]="PRINTED: "
            retarg[1]=noteline[2:]
        else:
            retarg[0]='<font color="red">UNKNOWN LINE</font> '
            retarg[1]+="%s  |  "%noteline[1:]
            for ch in noteline[1:]:
                retarg[1]+="'%s' "%str(char(ch))
        if "TC" in retarg[0]:
            retarg[1]="%s"%retarg[1]
    elif noteline[0]=="\t":                                                                     
        #this is the first character of any REAL line of old (pre MYSQL) notes
        retarg[0]= "oldNOTE"
        retarg[1]="%s"%noteline[1:]
    else:
        #new note lines don't have the tab
        retarg[0]="newNOTE"                                                                     
        retarg[1]+="%s"%noteline
    return retarg
       
def char(c):
    i=0
    while i < 256:
        if chr(i)==c:
            return i
            break
        i+=1

def tooth(data):
    #return str(data.split("\t"))
    retarg=""
    for c in data:
        i=char(c)
        if CHART.has_key(i):
            retarg += CHART[i]+" "
        else:
            retarg += c
    return retarg


if __name__ == "__main__":
    sys.path.append("/home/neil/openmolar")
    from openmolar.dbtools import patient_class
    try:
        serialno=int(sys.argv[len(sys.argv)-1])
    except:
        serialno=502
    if "-v" in sys.argv:
        verbose=True
    else:
         verbose=False
    print notes(patient_class.patient(serialno).notestuple)


