# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

'''
This module replaces notes.py with schema version 1.9
'''

import re
import sys
from openmolar.settings import localsettings

try:
    from collections import OrderedDict
except ImportError:
    #OrderedDict only came in python 2.7
    print "using openmolar.backports for OrderedDict"
    from openmolar.backports import OrderedDict

## some user variables which determine the verbosity of the notes

show_printed = False
show_payments =  False
show_timestamps = False


def get_notes_dict(results_tuple):
    '''
    '''
    notes_dict = OrderedDict()
    for ndate, op1, op2, ntype, note in results_tuple:

        ops = op1
        if op2:
            ops += "/%s"% op2

        key = (ndate, ops)
        if notes_dict.has_key(key):
            notes_dict[key].append((ntype,note))
        else:
            notes_dict[key] = [(ntype,note)]
    return notes_dict

def get_notes_for_date(lines):
    '''
    this is the actual user clinically relevant stuff!
    '''
    tx, note, metadata = "", "", ""
    for ntype, noteline in lines:
        if "NOTE" in ntype:
            note += "%s "% noteline.replace("<","&lt;").replace(">","&gt;")
        else:
            if "TC" in ntype:
                tx += "<b>%s</b><br />"% noteline
            elif show_payments and "RECEIVED" in ntype:
                note += "%s %s<br />"% (ntype, noteline)
            elif show_printed and "PRINT" in ntype:
                note += "%s %s<br />"% (ntype, noteline)
            elif show_timestamps and "COURSE" in ntype:
                note += "%s %s<br />"% (ntype, noteline)
            else:
                metadata += "<b>%s</b>%s<br />"% (ntype, noteline)

    note = note.rstrip("\n")

    return tx, note.replace("\n","<br />"), metadata

def get_rec_summary(lines):
    '''
    this is the reception summary (what has been charged and/or printed)
    '''
    note = ""
    for ntype, noteline in lines:
        if "PRINTED" in ntype:
            note += '<img src=%s height="12" align="right"> %s<br />'% (
                localsettings.printer_png, noteline)
        elif "RECEIVED:" in ntype:
            noteline = noteline.replace("sundries 0.00", "")
            noteline = noteline.replace("treatment 0.00", "")
            note += '<img src=%s height="12" align="right"> %s<br />'% (
                localsettings.money_png, noteline)

    return re.sub("(<br />)*$", "", note)


def rec_notes(notes_dict):
    '''
    returns an html string of notes, designed to fit into the
    reception notes panel (ie. vertical)
    '''

    retarg = '''<html><head><link rel="stylesheet"
    href="%s" type="text/css"></head><body><table border="1">'''% localsettings.stylesheet
    keys = notes_dict.keys()
    #keys.sort()

    for key in keys:
        date, op = key
        data = notes_dict[key]
        note = get_rec_summary(data)
        if note:
            retarg += '<tr><td>%s</td><td>%s</td></tr>'% (
                localsettings.formatDate(date), note)

    retarg += '</table></body></html>'

    return retarg


def notes(notes_dict):
    '''
    returns an html string of notes...
    '''

    retarg = '''<html><head><link rel="stylesheet"
    href="%s" type="text/css"></head><body>'''% localsettings.stylesheet
    keys = notes_dict.keys()
    #keys.sort()
    retarg += '''<table width = "100%">
        <tr>
            <th class = "date">Date</th>
            <th class = "ops">ops</th>
            <th class = "tx">Tx</th>
            <th class = "notes">Notes</th>
    '''

    if show_timestamps:
        retarg += '<th class="reception">metadata</th>'

    retarg += '</tr>'

    previousdate = "" #necessary to group notes on same day
    rowspan = 1
    newline = ""
    for key in keys:
        date, op = key
        data = notes_dict[key]
        tx, notes, metadata = get_notes_for_date(data)
        newline += "<tr>"
        if date != previousdate:
            previousdate = date
            rowspan = 1
            retarg += newline
            newline = '<td class="date">%s</td>'% (
                localsettings.readableDate(date))
        else:
            #alter the previous html, so that the rows are spanned
            rowspan += 1
            newline = re.sub(
            'class="date"( rowspan="\d")*',
            'class="date" rowspan="%d"'% rowspan, newline)

        newline += '''<td class="ops">%s</td>
        <td class="tx">%s</td>
        <td width="70%%" class="notes">%s</td>'''% (
        op, tx, notes)

        if show_timestamps:
            newline += '<td class="reception">%s</td></tr>'% metadata
        else:
            newline += '</tr>'
    retarg += newline
    retarg += '</table></div></body></html>'

    return retarg

if __name__ == "__main__":
    sys.path.insert(1, "/home/neil/openmolar/openmolar/src")
    from openmolar.dbtools import patient_class
    try:
        serialno=int(sys.argv[len(sys.argv)-1])
    except:
        serialno=1
    if "-v" in sys.argv:
        verbose=True
    else:
         verbose=False
    #print "getting notes"
    #print patient_class.patient(serialno).notes_dict

    #print rec_notes(patient_class.patient(serialno).notes_dict)
    print notes(patient_class.patient(serialno).notes_dict, verbose)

