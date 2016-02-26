#! /usr/bin/python
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


import logging
import textwrap

from openmolar.connect import connect
from openmolar.settings import localsettings
from openmolar.dbtools import patient_class
from openmolar.dbtools import estimates
from openmolar.dbtools.treatment_course import CURRTRT_ATTS
from openmolar.dbtools.treatment_course import UPDATE_CURRTTMT2_QUERY

LOGGER = logging.getLogger("openmolar")

BPE_INS_QUERY = '''insert into bpe (serialno, bpedate, bpe)
values (%s, %s, %s) on duplicate key update bpe=%s'''

EXMPT_INS_QUERY = ('insert into exemptions '
                   '(serialno, exemption, exempttext, datestamp) '
                   'values (%s,%s,%s, NOW())')


SYNOPSIS_INS_QUERY = '''
insert into clinical_memos (serialno, synopsis, author, datestamp)
values (%s, %s, %s, NOW())'''

RESET_MONEY_QUERY = '''
insert into patient_money (pt_sno, money0, money1) values (%s, %s, %s)
on duplicate key update money0=%s, money1=%s'''

INSERT_NOTE_QUERY = '''insert into formatted_notes
(serialno, ndate, op1, op2, ntype, note)
VALUES (%s, DATE(NOW()), %s, %s, %s, %s)'''


def note_splitter(notes, line_end=""):
    '''
    takes a list of lines, and further splits any lines which exceed 79 chars
    in length.
    '''
    lines = notes.split("\n")
    for line in lines:
        if line == "":
            yield line_end
        else:
            for short_line in textwrap.wrap(line, 78):
                yield short_line + line_end


def all_changes(pt, changes):
    LOGGER.debug("writing_changes to patient - %s" % str(changes))
    if changes == []:
        LOGGER.warning(
            "write changes called, but no changes for patient %d!" % (
                pt.serialno)
        )
        return True
    success = True
    # set up some booleans to prevent multiple updates of the same data
    # example exemption AND exemption text have changed..
    exemptionsHandled = False

    if pt.HIDDENNOTES != []:
        #  hidden notes is
        #  treatment codes... money, printing etc..
        LOGGER.debug("saving hiddennotes")
        toNotes(pt.serialno, pt.HIDDENNOTES)
        pt.clearHiddenNotes()

    sqlcommands = {}
    patchanges, patvalues = [], []
    static_changes, static_values = [], []
    date_changes, date_values = [], []
    nhs_changes, nhs_values = [], []
    trtchanges, trtvalues = "", []

    # money handled slightly differently. more complex query.
    money_changes, money_values = [], []

    for change in changes:
        if change == "courseno":
            pass  # these values should never get munged.

        elif change in patient_class.money_table_atts:
            money_changes.append(change)
            money_values.append(pt.__dict__[change])

        elif change in patient_class.patientTableAtts:
            # patchanges += '%s = %%s,' % change
            patchanges.append(change)
            patvalues.append(pt.__dict__[change])

        elif change in patient_class.date_table_atts:
            date_changes.append(change)
            date_values.append(pt.__dict__[change])

        elif change in patient_class.static_table_atts:
            static_changes.append(change.rstrip("st"))
            static_values.append(pt.__dict__[change])

        elif change in patient_class.nhs_table_atts:
            nhs_changes.append(change)
            nhs_values.append(pt.__dict__[change])

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

        elif change == "treatment_course":  # patient.CURRTRT_ATTS:
            for trt_att in CURRTRT_ATTS:
                value = pt.treatment_course.__dict__[trt_att]
                existing = pt.dbstate.treatment_course.__dict__[trt_att]
                if pt.has_new_course or value != existing:
                    trtchanges += '%s = %%s ,' % trt_att
                    trtvalues.append(value)

        elif change == "appt_prefs":
            pt.appt_prefs.commit_changes()

        elif change == "estimates":
            pass  # dealt with below

    if patchanges:
        query = "update new_patients SET %s where serialno=%%s" % \
            ", ".join(["%s = %%s" % change for change in patchanges])
        patvalues.append(pt.serialno)
        sqlcommands['patients'] = ((query, patvalues),)

    if static_changes:
        LOGGER.warning(
            "applying static_changes %s values %s",
            static_changes,
            static_values)
        query = '''insert into static_chart (pt_sno, %s) values (%%s, %s)
        on duplicate key update %s''' % (
            ", ".join(static_changes),
            ", ".join(("%s",) * len(static_changes)),
            ", ".join(["%s = %%s" % change for change in static_changes])
        )
        values = [pt.serialno] + static_values * 2
        sqlcommands['static'] = ((query, values),)

    if nhs_changes:
        LOGGER.warning(
            "applying nhs_changes %s values %s",
            nhs_changes,
            nhs_values)
        query = '''insert into patient_nhs (pt_sno, %s) values (%%s, %s)
        on duplicate key update %s''' % (
            ", ".join(nhs_changes),
            ", ".join(("%s",) * len(nhs_changes)),
            ", ".join(["%s = %%s" % change for change in nhs_changes])
        )
        values = [pt.serialno] + nhs_values * 2
        sqlcommands['nhs'] = ((query, values),)

    if date_changes:
        LOGGER.warning(
            "applying date_changes %s values %s",
            date_changes,
            date_values)
        query = '''insert into patient_dates (pt_sno, %s) values (%%s, %s)
        on duplicate key update %s''' % (
            ", ".join(date_changes),
            ", ".join(("%s",) * len(date_changes)),
            ", ".join(["%s = %%s" % change for change in date_changes])
        )
        values = [pt.serialno] + date_values * 2
        sqlcommands['patient_dates'] = ((query, values),)

    if money_changes:
        update_money_values = []
        update_query = "update "
        for i, change in enumerate(money_changes):
            if change in ("money0", "money1"):
                diff = pt.__dict__[change] - pt.dbstate.__dict__[change]
                update_money_values.append(diff)
                update_query += "%s=%s +%%s, " % (change, change)
            else:
                update_money_values.append(money_values[i])
                update_query += "%s=%%s, " % change

        LOGGER.warning(
            "applying money_changes %s values %s addition_values %s",
            money_changes,
            money_values,
            update_money_values)
        query = '''insert into patient_money (pt_sno, %s) values (%%s, %s)
        on duplicate key %s''' % (
            ", ".join(money_changes),
            ", ".join(("%s",) * len(money_changes)),
            update_query.rstrip(", ")
        )
        values = [pt.serialno] + money_values + update_money_values
        LOGGER.debug(query.replace("\n", " "))
        LOGGER.debug(values)
        sqlcommands['patient_money'] = ((query, values),)

    if trtchanges != "":
        trtvalues.append(pt.serialno)
        trtvalues.append(pt.treatment_course.courseno)

        query = UPDATE_CURRTTMT2_QUERY % (trtchanges.strip(","))
        sqlcommands['currtrtmt'] = ((query, trtvalues),)

    try:
        db = connect()
        db.autocommit = False

        if sqlcommands != {}:
            LOGGER.debug(sqlcommands)
            cursor = db.cursor()
            tables = sqlcommands.keys()
            for table in tables:
                for query, values in sqlcommands[table]:
                    try:
                        cursor.execute(query, values)
                    except Exception as exc:
                        LOGGER.error("error executing query %s" % query)
                        raise exc

            cursor.close()

        if "estimates" in changes:
            estimates.apply_changes(pt, pt.dbstate.estimates, pt.estimates)
        db.commit()

    except Exception as exc:
        LOGGER.exception("rolling back database")
        db.rollback()
        success = False
        raise exc
    finally:
        db.autocommit = True

    return success


def toNotes(serialno, newnotes):
    '''
    new code with schema 1.9
    '''
    LOGGER.debug("write changes - toNotes for patient %d" % serialno)

    tstamp = localsettings.currentTime().strftime("%d/%m/%Y %H:%M:%S")

    notetuplets = []
    notetuplets.append(("opened", "System date - %s" % tstamp))

    # database version stores max line length of 80chars
    for ntype, notes in newnotes:
        line_end = "\n" if ntype == "newNOTE" else ""
        for line in note_splitter(notes, line_end):
            notetuplets.append((ntype, line))
    notetuplets.append(("closed", "%s %s" % (localsettings.operator, tstamp)))

    try:
        op1, op2 = localsettings.operator.split("/")
    except ValueError:
        op1 = localsettings.operator
        op2 = None

    values = []
    for ntype, noteline in notetuplets:
        values.append((serialno, op1, op2, ntype, noteline))

    rows = 0
    if values:
        db = connect()
        cursor = db.cursor()
        # this (superior code?) didn't work on older MySQLdb versions.
        # rows = cursor.executemany(query, tuple(values))
        for value in values:
            rows += cursor.execute(INSERT_NOTE_QUERY, value)
        cursor.close()
        db.commit()

    return rows > 0


def discreet_changes(pt, changes):
    '''
    this is actually a duplication of the all-changes function, and writes only
    the changes passed.
    the only reason to keep it is for the extra message posted to the log.
    '''
    LOGGER.warning("discreet changes sno=%s %s", pt.serialno, changes)
    if not changes:
        LOGGER.error("no changes passed")
    return all_changes(pt, changes)


def reset_money(pt):
    if pt.monies_reset:
        values = (pt.serialno,) + (pt.dbstate.money0, pt.dbstate.money1) * 2
        db = connect()
        cursor = db.cursor()
        cursor.execute(RESET_MONEY_QUERY, values)
        cursor.close()
    return False