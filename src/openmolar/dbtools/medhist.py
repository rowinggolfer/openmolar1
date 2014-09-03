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
this module provides read/write tools for medical history
'''
from collections import namedtuple
import logging

from openmolar.connect import connect
from openmolar.settings import localsettings

LOGGER = logging.getLogger("openmolar")

ALL_MEDS_QUERY = 'select medication from medications'

NEW_MED_QUERY = '''insert into medications (medication, warning) values (%s, %s)
on duplicate key update medication=medication'''

MH_QUERY = '''
select ix, warning_card, medication_comments, allergies,
respiratory,heart, diabetes, arthritis, bleeding, infectious_disease,
endocarditis, liver, anaesthetic, joint_replacement, heart_surgery,
brain_surgery, hospital, cjd, other, alert, chkdate, time_stamp
from medhist where pt_sno = %s order by ix desc limit 1
'''

MEDS_QUERY = 'select med, details from medication_link where med_ix=%s'

DELETE_MEDS_QUERY = 'delete from medication_link where med_ix=%s'

INSERT_MEDS_QUERY = \
    'insert into medication_link (med_ix, med, details) values (%s, %s, %s)'

UPDATE_CHKDATE_QUERY = "update medhist set chkdate=%s, modified_by=%s where ix=%s"

PROPERTIES = ('ix', 'warning_card', 'medications',
              'medication_comments', 'allergies',
              'respiratory', 'heart', 'diabetes', 'arthritis', 'bleeding',
              'infectious_disease', 'endocarditis', 'liver', 'anaesthetic',
              'joint_replacement', 'heart_surgery', 'brain_surgery', 'hospital', 'cjd',
              'other', 'alert', 'chkdate', 'time_stamp')

MedHist = namedtuple('MedHist', PROPERTIES)

INSERT_QUERY = '''
insert into medhist (pt_sno, warning_card,
medication_comments, allergies, respiratory, heart, diabetes, arthritis,
bleeding, infectious_disease, endocarditis, liver, anaesthetic,
joint_replacement, heart_surgery, brain_surgery, hospital, cjd, other, alert,
chkdate, modified_by)
values (%s)''' % ", ".join(["%s" for val in PROPERTIES[:-1]])

UPDATE_QUERY = '''
update medhist set warning_card=%s,
medication_comments=%s, allergies=%s, respiratory=%s, heart=%s, diabetes=%s,
arthritis=%s, bleeding=%s, infectious_disease=%s, endocarditis=%s, liver=%s,
anaesthetic=%s, joint_replacement=%s, heart_surgery=%s, brain_surgery=%s,
hospital=%s, cjd=%s, other=%s, alert=%s, chkdate = %s, modified_by=%s
where ix=%s'''


NULLS = (None, "", {}) + \
    ("", ) * (len(PROPERTIES) - 6) + (False, localsettings.currentDay(), None)


def get_medications():
    '''
    get all medications currently stored in the database
    (used for autocomplete function)
    '''
    db = connect()
    cursor = db.cursor()
    cursor.execute(ALL_MEDS_QUERY)
    for row in cursor.fetchall():
        yield row[0]
    cursor.close()


def get_mh(sno):
    db = connect()
    cursor = db.cursor()
    cursor.execute(MH_QUERY, (sno,))
    row = cursor.fetchone()
    if row:
        values = row[:2] + ({},) + row[2:]
        med_hist = MedHist(*values)
        cursor.execute(MEDS_QUERY, (med_hist.ix,))
        for med, details in cursor.fetchall():
            med_hist.medications[med] = "" if details is None else details
    else:
        med_hist = MedHist(*NULLS)
    cursor.close()
    return med_hist


def update_chkdate(ix):
    LOGGER.debug("marking mh %s as checked today", ix)
    db = connect()
    cursor = db.cursor()
    result = cursor.execute(
        UPDATE_CHKDATE_QUERY, (localsettings.currentDay(), localsettings.operator, ix))
    cursor.close()
    return result


def insert_medication(medication, warning=False):
    LOGGER.warning(
        "inserting new medication '%s' into approved list", medication)
    db = connect()
    cursor = db.cursor()
    result = cursor.execute(NEW_MED_QUERY, (medication, warning))
    cursor.close()
    return result


def insert_mh(sno, mh):
    assert isinstance(mh, MedHist), "bad object passed to insert mh"
    db = connect()
    cursor = db.cursor()
    values = (sno,
              mh.warning_card,
              mh.medication_comments,
              mh.allergies,
              mh.respiratory,
              mh.heart,
              mh.diabetes,
              mh.arthritis,
              mh.bleeding,
              mh.infectious_disease,
              mh.endocarditis,
              mh.liver,
              mh.anaesthetic,
              mh.joint_replacement,
              mh.heart_surgery,
              mh.brain_surgery,
              mh.hospital,
              mh.cjd,
              mh.other,
              mh.alert,
              mh.chkdate,
              localsettings.operator,
              )
    cursor.execute(INSERT_QUERY, values)
    ix = db.insert_id()
    cursor.executemany(INSERT_MEDS_QUERY,
                       [(ix, key, mh.medications[key]) for key in mh.medications])
    cursor.close()


def update_mh(ix, mh):
    assert isinstance(mh, MedHist), "bad object passed to insert mh"
    db = connect()
    cursor = db.cursor()
    values = (mh.warning_card,
              mh.medication_comments,
              mh.allergies,
              mh.respiratory,
              mh.heart,
              mh.diabetes,
              mh.arthritis,
              mh.bleeding,
              mh.infectious_disease,
              mh.endocarditis,
              mh.liver,
              mh.anaesthetic,
              mh.joint_replacement,
              mh.heart_surgery,
              mh.brain_surgery,
              mh.hospital,
              mh.cjd,
              mh.other,
              mh.alert,
              mh.chkdate,
              localsettings.operator,
              ix
              )
    result = cursor.execute(UPDATE_QUERY, values)
    cursor.execute(DELETE_MEDS_QUERY, (ix,))
    cursor.executemany(INSERT_MEDS_QUERY,
                       [(ix, key, mh.medications[key]) for key in mh.medications])
    cursor.close()
    return result


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    get_medications()
    mh_null = get_mh(0)
    mh_valid = get_mh(1)

    print mh_null
    assert mh_null == MedHist(*NULLS), "null medical history shouldn't happen"
    print mh_valid

    insert_mh(1, mh_valid)
