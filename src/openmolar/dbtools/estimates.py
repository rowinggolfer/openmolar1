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

from openmolar import connect
from openmolar.settings import localsettings
from openmolar.ptModules.estimates import TXHash, Estimate


LOGGER = logging.getLogger("openmolar")


ESTS_QUERY = '''SELECT newestimates.ix, number, itemcode, description,
fee, ptfee, feescale, csetype, dent, est_link2.completed, tx_hash, courseno
from newestimates right join est_link2 on newestimates.ix = est_link2.est_id
where serialno=%s and courseno=%s order by itemcode, ix'''

ESTS_INS_QUERY = ('insert into newestimates (serialno, '
                  'courseno, number, itemcode, description, fee, ptfee, feescale, '
                  'csetype, dent, modified_by, time_stamp) values '
                  '(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())')

EST_LINK_INS_QUERY = (
    'insert into est_link2 (est_id, tx_hash, completed) values (%s, %s, %s)')

EST_DEL_QUERY = "delete from newestimates where ix=%s"
EST_LINK_DEL_QUERY = "delete from est_link2 where est_id=%s"

ESTS_UPDATE_QUERY = '''UPDATE newestimates SET
number=%s, itemcode=%s, description=%s, fee=%s, ptfee=%s, feescale=%s,
csetype=%s, dent=%s, modified_by=%s, time_stamp=NOW() WHERE ix=%s
'''.replace("\n", " ")


# too risky not to check these are unique before updating.
EST_DAYBOOK_ALTERATION_QUERIES = [
    'select daybook_id from daybook_link where tx_hash = %s',

    '''select sum(fee), sum(ptfee) from newestimates join est_link2
on newestimates.ix = est_link2.est_id where tx_hash in
(select tx_hash from daybook join daybook_link
on daybook.id = daybook_link.daybook_id where id=%s)''',

    'update daybook set feesa = %s, feesb = %s where serialno=%s and id=%s'
]


def get_ests(serialno, courseno):
    '''
    get estimate data
    '''
    db = connect.connect()
    cursor = db.cursor()

    cursor.execute(ESTS_QUERY, (serialno, courseno))

    rows = cursor.fetchall()
    ests = []

    for row in rows:
        hash_ = row[10]
        completed = bool(row[9])

        tx_hash = TXHash(hash_, completed)

        ix = row[0]

        found = False
        # use existing est if one relates to multiple treatments
        for existing_est in ests:
            if existing_est.ix == ix:
                existing_est.tx_hashes.append(tx_hash)
                found = True
                break
        if found:
            continue

        # initiate a custom data class
        est = Estimate()

        est.ix = ix
        est.courseno = row[11]
        est.number = row[1]
        est.itemcode = row[2]
        est.description = row[3]
        est.fee = row[4]
        est.ptfee = row[5]
        est.feescale = row[6]
        est.csetype = row[7]
        est.dent = row[8]

        est.tx_hashes = [tx_hash]
        ests.append(est)

    cursor.close()
    return ests


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
    db = connect.connect()
    cursor = db.cursor()
    query = EST_DAYBOOK_ALTERATION_QUERIES[0]
    cursor.execute(query, (tx_hash.hash,))
    rows = cursor.fetchall()
    if len(rows) != 1:
        LOGGER.warning(
            "unable to update daybook after estimate change - abandoning")
        return
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


def apply_changes(pt, old_ests, new_ests):

    LOGGER.info("APPLY ESTIMATE CHANGES")
    estimate_insertions = []
    estimate_updates = []
    estimate_deletions = []
    post_cleanup_commands = []

    result = True

    old_ests_dict = {}

    for est in old_ests:
        if est.ix is not None:
            old_ests_dict[est.ix] = est

    for est in new_ests:
        if est.ix is None:  # --new item
            values = (pt.serialno, est.courseno, est.number,
                      est.itemcode, est.description,
                      est.fee, est.ptfee, est.feescale, est.csetype,
                      est.dent, localsettings.operator)

            estimate_insertions.append((ESTS_INS_QUERY, values, est.tx_hashes))

        elif est.ix in old_ests_dict.keys():
            oldEst = old_ests_dict[est.ix]
            if oldEst != est:
                values = (est.number,
                          est.itemcode, est.description,
                          est.fee, est.ptfee, est.feescale, est.csetype,
                          est.dent, localsettings.operator, est.ix)

                estimate_updates.append((ESTS_UPDATE_QUERY, values, est))
                for tx_hash in est.tx_hashes:
                    values = (pt.serialno, tx_hash)
                    post_cleanup_commands.append(
                        (update_daybook_after_estimate_change, values))

            old_ests_dict.pop(est.ix)

    #-- all that is left in old_ests_dict now are items which
    #-- have been removed.
    #-- so remove from database if they are current course!
    for ix, old_est in old_ests_dict.iteritems():
        #--removed
        if old_est.courseno == pt.courseno0:
            values = (ix,)
            estimate_deletions.append((EST_DEL_QUERY, values))
            estimate_deletions.append((EST_LINK_DEL_QUERY, values))
            for tx_hash in old_est.tx_hashes:
                values = (pt.serialno, tx_hash)
                post_cleanup_commands.append(
                    (update_daybook_after_estimate_change, values))

    db = connect.connect()
    cursor = db.cursor()

    for query, values, tx_hashes in estimate_insertions:
        LOGGER.debug(query)
        LOGGER.debug(values)
        cursor.execute(query, values)
        ix = cursor.lastrowid
        for tx_hash in tx_hashes:
            vals = (ix, tx_hash.hash, tx_hash.completed)
            cursor.execute(EST_LINK_INS_QUERY, vals)

    for query, values, estimate in estimate_updates:
        LOGGER.debug(query)
        LOGGER.debug(values)
        cursor.execute(query, values)
        cursor.execute(EST_LINK_DEL_QUERY, (estimate.ix,))
        for tx_hash in estimate.tx_hashes:
            cursor.execute(EST_LINK_INS_QUERY,
                          (estimate.ix, tx_hash.hash,
                           tx_hash.completed)
                           )

    for query, values in estimate_deletions:
        LOGGER.debug(query)
        LOGGER.debug(values)
        cursor.execute(query, values)

    cursor.close()

    for func, values in post_cleanup_commands:
        func.__call__(values)

    return result


if __name__ == "__main__":
    ests = get_ests(11956, 29749)
    print ests
    print "equality test   (should be True)     ", ests[0] == ests[0]
    print "inequality test (should also be True)", ests[0] != ests[1]
