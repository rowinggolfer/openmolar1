#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ############################################################################ #
# #                                                                          # #
# # Copyright (c) 2009-2014 Neil Wallace <neil@openmolar.com>                # #
# #                                                                          # #
# # This file is part of OpenMolar.                                          # #
# #                                                                          # #
# # OpenMolar is free software: you can redistribute it and/or modify        # #
# # it under the terms of the GNU General Public License as published by     # #
# # the Free Software Foundation, either version 3 of the License, or        # #
# # (at your option) any later version.                                      # #
# #                                                                          # #
# # OpenMolar is distributed in the hope that it will be useful,             # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of           # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # #
# # GNU General Public License for more details.                             # #
# #                                                                          # #
# # You should have received a copy of the GNU General Public License        # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.       # #
# #                                                                          # #
# ############################################################################ #

'''
This module replaces notes.py with schema version 1.9
'''

import logging
import re
import sys

from openmolar.settings import localsettings
from openmolar.dbtools import db_notes
from openmolar.dbtools import db_patients

LOGGER = logging.getLogger("openmolar")

try:
    from collections import OrderedDict
except ImportError:
    # OrderedDict only came in python 2.7
    LOGGER.warning("using openmolar.backports for OrderedDict")
    from openmolar.backports import OrderedDict

# some user variables which determine the verbosity of the notes

show_printed = False
show_payments = False
show_timestamps = False
show_metadata = False

# use these variables for the summary notes also?
same_for_clinical = False

HEADER = '''<html>
<head>
<link rel="stylesheet" href="%s" type="text/css">
</head>
<body>
<!HEADER>''' % localsettings.stylesheet


def get_notes_dict(serialno, today_only=False):
    '''
    '''
    results_tuple = db_notes.notes(serialno, today_only)

    notes_dict = OrderedDict()
    for ndate, op1, op2, ntype, note in results_tuple:

        ops = op1
        if op2:
            ops += "/%s" % op2

        key = (ndate, ops)
        if key in notes_dict:
            notes_dict[key].append((ntype, note))
        else:
            notes_dict[key] = [(ntype, note)]
    return notes_dict


def s_t_l(note):
    '''
    strip trailing linebreaks
    '''
    return re.sub("(<br /> *)*$", "", note)


def get_notes_for_date(lines, full_notes=False):
    '''
    this is the actual user clinically relevant stuff!
    '''
    txs = []
    rev_txs = []
    tx, note, metadata = "", "", ""
    for ntype, noteline in lines:
        if "NOTE" in ntype and noteline != "":
            note += "%s " % noteline.replace(
                "<", "&lt;").replace(">", "&gt;")
        else:
            if "TC" in ntype:
                txs.append((ntype, noteline))
            elif ntype == "UNCOMPLETED":
                rev_txs.append((ntype, noteline))
            elif full_notes:
                if "RECEIVED" in ntype:
                    receipt_text = noteline.replace("sundries 0.00", "")
                    receipt_text = receipt_text.replace("treatment 0.00", "")
                    if show_payments:
                        tx += "%s %s<br />" % (ntype, receipt_text)
                elif "PRINT" in ntype:
                    if show_printed:
                        tx += "%s %s<br />" % (ntype, noteline)
                elif ntype in ("opened", "closed"):
                    if show_timestamps:
                        note += "<i>%s %s</i><br />" % (ntype, noteline)
                elif show_metadata:
                    metadata += "<b>%s</b>%s<br />" % (ntype, noteline)

    note = note.replace("\n", "<br />")

    for tuple_ in set(txs):
        n = txs.count(tuple_)
        ntype, treatment = tuple_
        if n != 1:
            tx += "<b>%d%s</b><br />" % (n, treatment)
        else:
            tx += "<b>%s</b><br />" % treatment

    for tuple_ in rev_txs:
        ntype, treatment = tuple_
        tx += "<b>%s</b><br />" % treatment

    return s_t_l(tx), s_t_l(note), s_t_l(metadata)


def get_rec_summary(lines):
    '''
    this is the reception summary (what has been charged and/or printed)
    '''
    note = ""
    for ntype, noteline in lines:
        if "PRINTED" in ntype:
            note += '<img src=%s height="12" align="right"> %s<br />' % (
                localsettings.printer_png, noteline)
        elif "RECEIVED:" in ntype:
            noteline = noteline.replace("sundries 0.00", "")
            noteline = noteline.replace("treatment 0.00", "")
            note += '<img src=%s height="12" align="right"> %s<br />' % (
                localsettings.money_png, noteline)

    return s_t_l(note)


def rec_notes(notes_dict, startdate=None):
    '''
    returns an html string of notes, designed to fit into the
    reception notes panel (ie. vertical)
    '''

    retarg = HEADER + '<table border="1">'
    if startdate:
        retarg += "<h4>%s</h4>" % _("Course Activity")

    keys = notes_dict.keys()
    # keys.sort()

    for key in keys:
        date, op = key
        if startdate and date >= startdate:
            data = notes_dict[key]
            note = get_rec_summary(data)
            if note:
                retarg += '<tr><td>%s</td><td>%s</td></tr>' % (
                    localsettings.formatDate(date), note)

    retarg += '</table></body></html>'

    return retarg


def summary_notes(notes_dict):
    return notes(notes_dict, same_for_clinical)


def notes(notes_dict, full_notes=True):
    '''
    returns an html string of notes...
    '''

    retarg = HEADER + '''
        <table class="notes_table">
            <tr>
                <th class = "date">Date</th>
                <th class = "ops">ops</th>
                <th class = "tx">Tx</th>
                <th class = "notes">Notes</th>
        '''

    keys = notes_dict.keys()

    if full_notes and show_metadata:
        retarg += '<th class="reception">metadata</th>'

    retarg += '</tr>'

    previousdate = ""  # necessary to group notes on same day
    rowspan = 1
    newline = ""
    for key in keys:
        date, op = key
        data = notes_dict[key]
        tx, notes, metadata = get_notes_for_date(data, full_notes)
        newline += "<tr>"
        if date != previousdate:
            previousdate = date
            rowspan = 1
            retarg += newline
            link = ""

            newline = '<td class="date">%s %s</td>' % (
                localsettings.notesDate(date), link)
        else:
            # alter the previous html, so that the rows are spanned
            rowspan += 1
            newline = re.sub(
                'class="date"( rowspan="\d")*',
                'class="date" rowspan="%d"' % rowspan, newline)

        subline = '<td class="ops">%s' % op

        if (date == localsettings.currentDay() and
           op == localsettings.operator):
            subline += '<br /><a href="edit_notes?||SNO||">%s</a>' % _("Edit")

        newline += '''%s</td>
        <td class="tx">%s</td>
        <td width="70%%" class="notes">%s</td>''' % (subline, tx, notes)

        if show_metadata:
            newline += '<td class="reception">%s</td></tr>' % metadata
        else:
            newline += '</tr>'
    retarg += newline
    retarg += '</table></div></body></html>'

    return retarg


def todays_notes(serialno):
    html = notes(get_notes_dict(serialno, True))
    if not _("Today") in html:
        html = HEADER
        html += "%s <a href='edit_notes?%s'>%s</a></body></html>" % (
            _("No notes found"), serialno, _("Add a note"))

    name = db_patients.name(serialno)
    header = "<h3>%s %s</h3>" % (_("Todays notes for"), name)
    html = html.replace("<!HEADER>", header)
    html = html.replace("||SNO||", str(serialno))

    return html

if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    from openmolar.dbtools import patient_class
    try:
        serialno = int(sys.argv[len(sys.argv) - 1])
    except:
        serialno = 1

    notes_ = notes(patient_class.patient(serialno).notes_dict)
    print notes_.encode("ascii", "replace")
