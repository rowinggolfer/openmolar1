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

import logging
import sys
import types

import MySQLdb

from openmolar.connect import connect
from openmolar.settings import localsettings
from openmolar.dbtools import patient_class
from openmolar.dbtools.treatment_course import CURRTRT_ATTS
from openmolar.dbtools.treatment_course import UPDATE_CURRTTMT2_QUERY

LOGGER = logging.getLogger("openmolar")

BPE_INS_QUERY = '''insert into bpe (serialno, bpedate, bpe)
values (%s, %s, %s) on duplicate key update bpe=%s'''

EXMPT_INS_QUERY = ('insert into exemptions '
                   '(serialno, exemption, exempttext, datestamp) '
                   'values (%s,%s,%s, NOW())')

ESTS_INS_QUERY = ('insert into newestimates (serialno, '
                  'courseno, number, itemcode, description, fee, ptfee, feescale, '
                  'csetype, dent, modified_by, time_stamp) values '
                  '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())')

EST_LINK_INS_QUERY = (
    'insert into est_link2 (est_id, tx_hash, completed) values (%s, %s, %s)')

EST_DEL_QUERY = "delete from newestimates where ix=%s"
EST_LINK_DEL_QUERY = "delete from est_link2 where est_id=%s"


# too risky not to check these are unique before updating.
EST_DAYBOOK_ALTERATION_QUERIES = [
    'select daybook_id from daybook_link where tx_hash = %s',

    '''select sum(fee), sum(ptfee) from newestimates join est_link2
on newestimates.ix = est_link2.est_id where tx_hash in
(select tx_hash from daybook join daybook_link
on daybook.id = daybook_link.daybook_id where id=%s)''',

    'update daybook set feesa = %s, feesb = %s where serialno=%s and id=%s'
]


SYNOPSIS_INS_QUERY = '''
insert into clinical_memos (serialno, synopsis, author, datestamp)
values (%s, %s, %s, NOW())'''


def update_daybook_after_estimate_change(values):
    '''
    if the value of a treatment item has been changed after completion,
    update the daybook.
    most common example of this is when an exemption is applied to a course of
    treatment at reception (altering the charges put into the system in the
    surgery)
    note - use of serialno here is purely for precautionary reasons.
    Hash collisions shouldn't occur... but easy to be cautious here.
    '''
    serialno, tx_hash = values
    result = True
    db = connect()
    cursor = db.cursor()
    try:
        query = EST_DAYBOOK_ALTERATION_QUERIES[0]
        cursor.execute(query, (tx_hash.hash,))
        rows = cursor.fetchall()
        if len(rows) != 1:
            LOGGER.warning(
                "unable to update daybook after estimate change - abandoning")
            return True
        daybook_id = rows[0][0]
        LOGGER.debug("updating daybook row %s" % daybook_id)

        query = EST_DAYBOOK_ALTERATION_QUERIES[1]
        cursor.execute(query, (daybook_id,))
        feesa, feesb = cursor.fetchone()

        LOGGER.debug(
            "updating row with feesa, feesb = %s and %s" %
            (feesa, feesb))
        query = EST_DAYBOOK_ALTERATION_QUERIES[2]
        rows_changed = cursor.execute(
            query, (feesa, feesb, serialno, daybook_id))
        LOGGER.info("changes applied = %s" % bool(rows_changed))

    except Exception as exc:
        LOGGER.exception("error executing query %s" % query)
        result = False

    return result


def all_changes(pt, changes):
    LOGGER.debug("writing_changes to patient - %s" % str(changes))
    if changes == []:
        LOGGER.warning(
            "write changes called, but no changes for patient %d!" % (
                pt.serialno)
        )
        return True
    else:
        # set up some booleans to prevent multiple updates of the same data
        # example exemption AND exemption text have changed..
        exemptionsHandled = False

        if pt.HIDDENNOTES != []:
            #-- hidden notes is
            #-- treatment codes... money, printing etc..
            LOGGER.debug("saving hiddennotes")
            toNotes(pt.serialno, pt.HIDDENNOTES)
            pt.clearHiddenNotes()

        sqlcommands = {}
        estimate_commands = {}
        patchanges, patvalues = "", []
        trtchanges, trtvalues = "", []
        post_cleanup_commands = []

        for change in changes:
            if change == "courseno":
                pass  # these values should never get munged.

            elif change in ("money0, money1"):
                diff = pt.__dict__[change] - pt.dbstate.__dict__[change]
                patvalues.append(diff)
                patchanges += '%s = %s + %%s,' % (change, change)

            elif change in patient_class.patientTableAtts:
                patvalues.append(pt.__dict__[change])
                patchanges += '%s = %%s,' % change

            elif (change in patient_class.exemptionTableAtts and
                  not exemptionsHandled):
                values = (pt.serialno, pt.exemption, pt.exempttext)
                sqlcommands['exemptions'] = ((EXMPT_INS_QUERY, values),)
                exemptionsHandled = True

            elif change == "bpe":
                values = (pt.serialno,
                          pt.bpe[-1][0],
                          pt.bpe[-1][1],
                          pt.bpe[-1][1]
                          )
                sqlcommands['bpe'] = ((BPE_INS_QUERY, values),)

            elif change == "synopsis":
                values = (pt.serialno, pt.synopsis,
                          localsettings.operator)

                sqlcommands['clinical_memos'] = ((SYNOPSIS_INS_QUERY, values),)

            elif change == "estimates":
                estimate_commands["insertions"] = []
                estimate_commands["updates"] = []
                sqlcommands["estimate_deletions"] = []
                sqlcommands["estimate_daybook_alterations"] = []

                oldEstDict = {}

                for est in pt.dbstate.estimates:
                    #-- generate a dictionary with the
                    #-- autogenerated db indexas key
                    if est.ix is not None:
                        oldEstDict[est.ix] = est

                for est in pt.estimates:
                    if est.ix is None:  # --new item
                        values = (pt.serialno, est.courseno, est.number,
                                  est.itemcode, est.description,
                                  est.fee, est.ptfee, est.feescale, est.csetype,
                                  est.dent, localsettings.operator)

                        estimate_commands["insertions"].append(
                            (ESTS_INS_QUERY, values, est.tx_hashes)
                        )

                    elif est.ix in oldEstDict.keys():
                        oldEst = oldEstDict[est.ix]

                        if str(oldEst) != str(est):
                            #-- have to use the str because est class does not
                            #-- have a _eq_ property ??
                            query = 'update newestimates set '
                            values = []
                            if oldEst.number != est.number:
                                query += "number=%s,"
                                values.append(est.number)
                            if oldEst.itemcode != est.itemcode:
                                query += 'itemcode=%s,'
                                values.append(est.itemcode)
                            if oldEst.description != est.description:
                                query += 'description=%s,'
                                values.append(est.description)
                            if oldEst.fee != est.fee:
                                query += 'fee=%s,'
                                values.append(est.fee)
                            if oldEst.ptfee != est.ptfee:
                                query += "ptfee=%s,"
                                values.append(est.ptfee)
                            if oldEst.feescale != est.feescale:
                                query += 'feescale=%s,'
                                values.append(pt.feescale)
                            if oldEst.csetype != est.csetype:
                                query += 'csetype=%s,'
                                values.append(est.csetype)
                            if oldEst.dent != est.dent:
                                query += 'dent=%d,'
                                values.append(est.dent)

                            query += ('modified_by = %s, '
                                      'time_stamp = NOW() where ix = %s')

                            values.append(localsettings.operator)
                            values.append(est.ix)

                            estimate_commands["updates"].append(
                                (query, tuple(values), est))
                            for tx_hash in est.tx_hashes:
                                values = (pt.serialno, tx_hash)
                                post_cleanup_commands.append(
                                    (update_daybook_after_estimate_change, values))

                        oldEstDict.pop(est.ix)

                #-- all that is left in oldEstDict now are items which
                #-- have been removed.
                #-- so remove from database if they are current course!
                for ix, old_est in oldEstDict.iteritems():
                    #--removed
                    if old_est.courseno == pt.courseno0:
                        values = (ix,)
                        deletions = sqlcommands["estimate_deletions"]
                        deletions.append((EST_DEL_QUERY, values))
                        deletions.append((EST_LINK_DEL_QUERY, values))
                        for tx_hash in old_est.tx_hashes:
                            values = (pt.serialno, tx_hash)
                            post_cleanup_commands.append(
                                (update_daybook_after_estimate_change, values))

            elif change == "treatment_course":  # patient.CURRTRT_ATTS:
                for trt_att in CURRTRT_ATTS:
                    value = pt.treatment_course.__dict__[trt_att]
                    existing = pt.dbstate.treatment_course.__dict__[trt_att]
                    if pt.has_new_course or value != existing:
                        trtchanges += '%s = %%s ,' % trt_att
                        trtvalues.append(value)

            elif change == "appt_prefs":
                pt.appt_prefs.commit_changes()

    result = True
    if patchanges != "":
        patvalues.append(pt.serialno)
        values = tuple(patvalues)

        query = "update patients SET %s where serialno=%%s" % patchanges.strip(
            ",")

        sqlcommands['patients'] = ((query, values),)

    if trtchanges != "":
        trtvalues.append(pt.serialno)
        trtvalues.append(pt.treatment_course.courseno)
        values = tuple(trtvalues)

        query = UPDATE_CURRTTMT2_QUERY % (trtchanges.strip(","))
        sqlcommands['currtrtmt'] = ((query, values),)

    if sqlcommands != {} or estimate_commands != {}:
        LOGGER.debug(sqlcommands)
        LOGGER.debug(estimate_commands)
        db = connect()
        cursor = db.cursor()
        tables = sqlcommands.keys()
        for table in tables:
            for query, values in sqlcommands[table]:
                try:
                    cursor.execute(query, values)
                except Exception as exc:
                    LOGGER.exception("error executing query %s" % query)
                    result = False

        insert_commands = estimate_commands.get("insertions", [])
        for query, values, tx_hashes in insert_commands:
            try:
                cursor.execute(query, values)
                ix = cursor.lastrowid
                try:
                    for tx_hash in tx_hashes:
                        vals = (ix, tx_hash.hash, tx_hash.completed)
                        cursor.execute(EST_LINK_INS_QUERY, vals)
                except Exception as exc:
                    LOGGER.exception("error executing query\n %s\n %s" % (
                        EST_LINK_INS_QUERY, vals))
                    result = False
            except Exception as exc:
                LOGGER.exception("error executing query\n %s\n %s" % (
                    query, str(values)))
                result = False

        update_commands = estimate_commands.get("updates", [])
        for query, values, estimate in update_commands:
            try:
                cursor.execute(query, values)
                cursor.execute(EST_LINK_DEL_QUERY, (estimate.ix,))
                for tx_hash in estimate.tx_hashes:
                    cursor.execute(EST_LINK_INS_QUERY,
                                  (estimate.ix, tx_hash.hash,
                                   tx_hash.completed)
                                   )
            except Exception as exc:
                LOGGER.exception("error updating estimate %s" % estimate)
                result = False

        cursor.close()

        for func, values in post_cleanup_commands:
            func.__call__(values)

        db.commit()

    return result


def toNotes(serialno, newnotes):
    '''
    new code with schema 1.9
    '''
    LOGGER.debug("write changes - toNotes for patient %d" % serialno)

    # database version stores max line length of 80chars

    query = '''insert into formatted_notes
    (serialno, ndate, op1, op2, ntype, note)
    VALUES (%s, DATE(NOW()), %s, %s, %s, %s)
    '''
    notetuplets = []

    tstamp = localsettings.currentTime().strftime("%d/%m/%Y %T")
    notetuplets.append(
        ("opened", "System date - %s" % tstamp))
    for ntype, note in newnotes:
        while len(note) > 79:
            if " " in note[:79]:
                pos = note[:79].rindex(" ")
                #--try to split nicely
            elif "," in note[:79]:
                pos = note[:79].rindex(",")
                #--try to split nicely
            else:
                pos = 79
                #--ok, no option (unlikely to happen though)
            notetuplets.append((ntype, note[:pos]))
            note = note[pos + 1:]

        notetuplets.append((ntype, note + "\n"))
    notetuplets.append(
        ("closed", "%s %s" % (localsettings.operator, tstamp)))

    values = []
    ops = localsettings.operator.split("/")
    op1 = ops[0]
    try:
        op2 = ops[1]
    except IndexError:
        op2 = None
    for ntype, noteline in notetuplets:
        values.append((serialno, op1, op2, ntype, noteline))

    rows = 0
    if values:
        db = connect()
        cursor = db.cursor()

        # this (superior code?) didn't work on older MySQLdb versions.
        # rows = cursor.executemany(query, tuple(values))
        for value in values:
            rows += cursor.execute(query, value)

        cursor.close()
        db.commit()

    return rows > 0


def discreet_changes(pt_changed, changes):
    '''
    this updates only the selected atts
    (usually called by automated proc such as recalls...
    and accounts) only updates the patients table
    '''
    LOGGER.debug("write changes - discreet changes")

    sqlcond = ""
    for change in changes:
        value = pt_changed.__dict__[change]
        LOGGER.debug("discreet change %s %s" % (change, type(value)))
        if change in patient_class.dateFields:
            if value != "" and value is not None:
                sqlcond += '%s="%s" ,' % (change, value)
        elif value is None:
            sqlcond += '%s=NULL ,' % change
        elif type(value) in (int, int):
            sqlcond += '%s=%s ,' % (change, value)
        else:
            sqlcond += '%s="%s" ,' % (change, value)

    sqlcommand = "update patients SET %s where serialno=%%s" % (
        sqlcond.strip(","))

    LOGGER.debug("%s (%s,)" % (sqlcommand, pt_changed.serialno))

    result = True
    if sqlcond != "":
        db = connect()
        cursor = db.cursor()
        try:
            cursor.execute(sqlcommand, (pt_changed.serialno,))
            db.commit()
        except Exception as e:
            LOGGER.exception("unable to write discreet changes")
            result = False
        cursor.close()
    return result
