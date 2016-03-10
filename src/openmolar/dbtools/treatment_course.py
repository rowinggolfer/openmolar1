#! /usr/bin/python

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2016 Neil Wallace <neil@openmolar.com>               # #
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

from gettext import gettext as _
import logging

from openmolar import connect
from openmolar.settings import localsettings

LOGGER = logging.getLogger("openmolar")

CURRTRT_NON_TOOTH_ATTS = (
    'xray', 'perio', 'anaes', 'other', 'ndu', 'ndl', 'odu', 'odl', 'custom')

UPPERS = ('ur8', 'ur7', 'ur6', 'ur5', 'ur4', 'ur3', 'ur2', 'ur1',
          'ul1', 'ul2', 'ul3', 'ul4', 'ul5', 'ul6', 'ul7', 'ul8')

LOWERS = ('lr8', 'lr7', 'lr6', 'lr5', 'lr4', 'lr3', 'lr2', 'lr1',
          'll1', 'll2', 'll3', 'll4', 'll5', 'll6', 'll7', 'll8')

CURRTRT_ROOT_ATTS = CURRTRT_NON_TOOTH_ATTS + UPPERS + LOWERS

CURRTRT_ATTS = (
    'courseno', 'xraypl', 'periopl', 'anaespl', 'otherpl',
    'ndupl', 'ndlpl', 'odupl', 'odlpl', "custompl", 'xraycmp',
    'periocmp', 'anaescmp', 'othercmp', 'nducmp', 'ndlcmp',
    'oducmp', 'odlcmp', "customcmp",
    'ur8pl', 'ur7pl', 'ur6pl', 'ur5pl', 'ur4pl', 'ur3pl', 'ur2pl', 'ur1pl',
    'ul1pl', 'ul2pl', 'ul3pl', 'ul4pl', 'ul5pl', 'ul6pl', 'ul7pl', 'ul8pl',
    'll8pl', 'll7pl', 'll6pl', 'll5pl', 'll4pl', 'll3pl', 'll2pl', 'll1pl',
    'lr1pl', 'lr2pl', 'lr3pl', 'lr4pl', 'lr5pl', 'lr6pl', 'lr7pl', 'lr8pl',
    'ur8cmp', 'ur7cmp', 'ur6cmp', 'ur5cmp',
    'ur4cmp', 'ur3cmp', 'ur2cmp', 'ur1cmp',
    'ul1cmp', 'ul2cmp', 'ul3cmp', 'ul4cmp',
    'ul5cmp', 'ul6cmp', 'ul7cmp', 'ul8cmp',
    'll8cmp', 'll7cmp', 'll6cmp', 'll5cmp',
    'll4cmp', 'll3cmp', 'll2cmp', 'll1cmp',
    'lr1cmp', 'lr2cmp', 'lr3cmp', 'lr4cmp',
    'lr5cmp', 'lr6cmp', 'lr7cmp', 'lr8cmp',
    'examt', 'examd', 'accd', 'cmpd', 'ftr')

QUERY = "SELECT "
for field in CURRTRT_ATTS:
    QUERY += "%s, " % field
QUERY = QUERY.rstrip(", ")
QUERY += " from currtrtmt2 where serialno=%s and courseno=%s"

MAX_COURSE_QUERY = "select max(courseno) from currtrtmt2 where serialno=%s"
DATE_QUERY = "select accd, cmpd, examd from currtrtmt2 where courseno=%s"
UPDATE_DATES_QUERY = "update currtrtmt2 set accd=%s, cmpd=%s where courseno=%s"

UPDATE_CURRTTMT2_QUERY = (
    'UPDATE currtrtmt2 SET %s WHERE serialno=%%s and courseno=%%s')

DELETE_CURRTTMT2_QUERY = (
    'DELETE from currtrtmt2 WHERE serialno=%s and courseno=%s')

UPDATE_ESTS_COURSENO_QUERY = (
    'UPDATE newestimates SET courseno=%s WHERE courseno=%s')


def get_course_dates(courseno):
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(DATE_QUERY, (courseno, ))
    row = cursor.fetchone()
    cursor.close()
    return row


def update_course_dates(accd, cmpd, courseno):
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(UPDATE_DATES_QUERY, (accd, cmpd, courseno, ))
    cursor.close()


def update_estimate_courseno(courseno_orig, courseno_new):
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(UPDATE_ESTS_COURSENO_QUERY, (courseno_new, courseno_orig))
    cursor.close()


def update_course(query_insert, values, serialno, courseno):
    assert len(values) == query_insert.count("=")
    query = UPDATE_CURRTTMT2_QUERY % query_insert
    values.append(serialno)
    values.append(courseno)
    db = connect.connect()
    cursor = db.cursor()
    result = cursor.execute(query, values)
    cursor.close()
    return result


def delete_course(serialno, courseno):
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(DELETE_CURRTTMT2_QUERY % (serialno, courseno))
    cursor.close()


class TreatmentCourse(object):

    def __init__(self, sno, courseno):
        '''
        initiate the class with default variables, then load from database
        '''
        self.dbstate = None
        self.serialno = sno
        self.courseno = courseno
        self.xraypl = ''
        self.periopl = ''
        self.anaespl = ''
        self.otherpl = ''
        self.ndupl = ''
        self.ndlpl = ''
        self.odupl = ''
        self.odlpl = ''
        self.custompl = ''
        self.xraycmp = ''
        self.periocmp = ''
        self.anaescmp = ''
        self.othercmp = ''
        self.nducmp = ''
        self.ndlcmp = ''
        self.oducmp = ''
        self.odlcmp = ''
        self.customcmp = ''
        self.ur8pl = ''
        self.ur7pl = ''
        self.ur6pl = ''
        self.ur5pl = ''
        self.ur4pl = ''
        self.ur3pl = ''
        self.ur2pl = ''
        self.ur1pl = ''
        self.ul1pl = ''
        self.ul2pl = ''
        self.ul3pl = ''
        self.ul4pl = ''
        self.ul5pl = ''
        self.ul6pl = ''
        self.ul7pl = ''
        self.ul8pl = ''
        self.ll8pl = ''
        self.ll7pl = ''
        self.ll6pl = ''
        self.ll5pl = ''
        self.ll4pl = ''
        self.ll3pl = ''
        self.ll2pl = ''
        self.ll1pl = ''
        self.lr1pl = ''
        self.lr2pl = ''
        self.lr3pl = ''
        self.lr4pl = ''
        self.lr5pl = ''
        self.lr6pl = ''
        self.lr7pl = ''
        self.lr8pl = ''
        self.ur8cmp = ''
        self.ur7cmp = ''
        self.ur6cmp = ''
        self.ur5cmp = ''
        self.ur4cmp = ''
        self.ur3cmp = ''
        self.ur2cmp = ''
        self.ur1cmp = ''
        self.ul1cmp = ''
        self.ul2cmp = ''
        self.ul3cmp = ''
        self.ul4cmp = ''
        self.ul5cmp = ''
        self.ul6cmp = ''
        self.ul7cmp = ''
        self.ul8cmp = ''
        self.ll8cmp = ''
        self.ll7cmp = ''
        self.ll6cmp = ''
        self.ll5cmp = ''
        self.ll4cmp = ''
        self.ll3cmp = ''
        self.ll2cmp = ''
        self.ll1cmp = ''
        self.lr1cmp = ''
        self.lr2cmp = ''
        self.lr3cmp = ''
        self.lr4cmp = ''
        self.lr5cmp = ''
        self.lr6cmp = ''
        self.lr7cmp = ''
        self.lr8cmp = ''
        self.examt = ''
        self.examd = ''
        self.accd = None
        self.cmpd = None
        self.ftr = None

        # this next line gives me a way to create a Mock Instance of the class
        if self.courseno == 0:
            return

        self.getCurrtrt()

    def __repr__(self):
        message = "TreatmentCourse for patient %s courseno %s\n" % (
            self.serialno, self.courseno)

        for att in CURRTRT_ATTS:
            value = self.__dict__.get(att, "")
            if value != "":
                message += "   %s,%s\n" % (att, value)
        return message

    def __eq__(self, other):
        return str(self) == str(other)

    def _non_tooth_items(self, suffix="pl"):
        for att in CURRTRT_NON_TOOTH_ATTS:
            value = self.__dict__.get(att + suffix, "")
            if value != "":
                txs = value.split(" ")
                for tx in set(txs):
                    if tx != "":
                        n = txs.count(tx)
                        if n != 1:
                            tx = "%d%s" % (n, tx)
                        yield att, tx

    @property
    def non_tooth_plan_items(self):
        return list(self._non_tooth_items("pl"))

    @property
    def non_tooth_cmp_items(self):
        items = []
        if self.examt != "" and self.examd:
            items.append(("exam", self.examt))
        return items + list(self._non_tooth_items("cmp"))

    def getCurrtrt(self):
        db = connect.connect()
        cursor = db.cursor()
        cursor.execute(QUERY, (self.serialno, self.courseno))
        for value in cursor.fetchall():
            for i, field in enumerate(CURRTRT_ATTS):
                self.__dict__[field] = value[i]
        cursor.close()

    @property
    def underTreatment(self):
        return self.accd not in ("", None) and self.cmpd in ("", None)

    @property
    def max_tx_courseno(self):
        db = connect.connect()
        cursor = db.cursor()
        if cursor.execute(MAX_COURSE_QUERY, (self.serialno,)):
            cno = cursor.fetchone()[0]
        else:
            cno = 0
        cursor.close()
        return cno

    @property
    def newer_course_found(self):
        try:
            return self.max_tx_courseno > self.courseno
        except TypeError:  # one or both of these values are NoneType
            if self.max_tx_courseno:
                return True
            return False

    @property
    def has_exam(self):
        return self.examt != "" and self.examd

    def setAccd(self, accd):
        '''
        set the acceptance date (with a pydate)
        '''
        if accd is None:
            accd = localsettings.currentDay()
        self.accd = accd

    def setCmpd(self, cmpd):
        '''
        set the completion date (with a pydate)
        '''
        self.cmpd = cmpd

    def set_ftr(self, ftr):
        '''
        ftr = "Failed to Return"
        '''
        self.ftr = ftr

    @property
    def has_treatment_outstanding(self):
        for att in CURRTRT_ATTS:
            if att[-2:] == "pl":
                if self.__dict__[att].strip(" ") != "":
                    return True
        return False

    @property
    def tx_hashes(self):
        return self._get_tx_hashes()

    @property
    def completed_tx_hash_tups(self):
        return self._get_tx_hashes(True)

    @property
    def completed_tx_hashes(self):
        for hash_, att, tx in self._get_tx_hashes(True):
            yield hash_

    @property
    def planned_tx_hash_tups(self):
        for tup in self._get_tx_hashes():
            if tup not in self.completed_tx_hash_tups:
                yield tup

    def _get_tx_hashes(self, completed_only=False):
        '''
        returns a tuple (unique hash, attribute, treatment)
        hashes will be unique as multiple identical items are indexed
        eg. eg "perio SP AC SP " is hashed as follows
        "%sperio1SP"% courseno
        "%sperio2SP"% courseno
        "%sperio1AC"% courseno
        '''
        if self.examt != "":
            hash_ = localsettings.hash_func(
                "%sexam1%s" % (self.courseno, self.examt))
            yield (hash_, "exam", self.examt + " ")

        for att in CURRTRT_ROOT_ATTS:
            treats = self.__dict__[att + "cmp"]
            if not completed_only:
                treats += " " + self.__dict__[att + "pl"]
            treat_list = sorted(treats.split(" "))
            prev_tx, count = None, 1

            for tx in treat_list:
                if tx == "":
                    continue
                if tx != prev_tx:
                    count = 1
                    prev_tx = tx
                else:
                    count += 1
                hash_ = localsettings.hash_func(
                    "%s%s%s%s" % (self.courseno, att, count, tx))
                yield (hash_, att, tx + " ")

    def get_tx_from_hash(self, hash_):
        '''
        example
        imput a hash 039480284098
        get back ("ur1", "M")
        '''
        for tx_hash in self.tx_hashes:
            if tx_hash[0] == hash_:
                return tx_hash[1], tx_hash[2]
        LOGGER.warning("couldn't find treatment %s" % hash_)
        LOGGER.debug("listing existing hashes")
        for tx_hash in self.tx_hashes:
            LOGGER.debug(tx_hash)
        return None, None

    def pl_txs(self, att):
        '''
        returns the list of treatments currently planned for this attribute.
        eg pl_txs("ul8") may return ["O", "B,CO"]
        '''
        txs = self.__dict__["%spl" % att].split(" ")
        while "" in txs:
            txs.remove("")
        return txs

    def cmp_txs(self, att):
        '''
        returns the list of treatments currently planned for this attribute.
        eg cmp_txs("ul8") may return ["O", "B,CO"]
        '''
        txs = self.__dict__["%scmp" % att].split(" ")
        while "" in txs:
            txs.remove("")
        return txs

    def all_txs(self, att):
        '''
        returns the list of treatments currently associated with an attribute.
        eg all_txs("ul8") may return ["O", "B,CO"]
        '''
        return self.cmp_txs(att) + self.pl_txs(att)

    @property
    def course_duration(self):
        if not self.cmpd:
            return (_("still ongoing"))
        else:
            days = (self.cmpd - self.accd).days + 1
            if days == 1:
                return "1 %s" % _("day")
            return "%s %s" % (days, _("days"))

    def to_html(self, allow_edit=False, days_elapsed=None,
                completed_only=False):
        def sorted_work(work):
            items = work.split(" ")
            return " ".join(sorted([item for item in items if item != ""]))

        if allow_edit:
            edit_str = '''<a href="edit_courseno?%s">%s</a><br />
            <a href="edit_tx_courseno?%s">%s</a>
            <!--merge-->''' % (
                self.courseno, _("Edit Course Dates"),
                self.courseno, _("Edit Treatments"))
        else:
            edit_str = ""

        if days_elapsed is None:
            days_str = ""
        else:
            days_str = " (%s %s)" % (days_elapsed, _("days earlier"))

        html = '''
        <h4>%s %s %s</h4>
        <font color="red">%s</font>
        <table width = "100%%" border = "1">
        <tr>
            <th width="20%%" colspan="1" bgcolor="#ffff99">%s</th>
            <th width="20%%" colspan="1" bgcolor="#ffff99">
                %s %s<br />%s %s
            </th>
            <th width="60%%" bgcolor="#ffff99">%s %s</th>
        </tr>
        ''' % (
            _("Course Number"), self.courseno, days_str,
            _("PATIENT FAILED TO RETURN") if self.ftr else "",
            edit_str,
            _("Opened"), localsettings.formatDate(self.accd),
            _("Closed"), localsettings.formatDate(self.cmpd),
            _("Duration"), self.course_duration,
        )

        attributes = ("cmp",) if completed_only else ("pl", "cmp")

        # plan row.
        for planned in attributes:
            rows = []

            if planned == "pl":
                bgcolor = ' bgcolor = "#eeeeee"'
                header = "%s<br />%s" % (_("Planned"), _("or incomplete"))
            else:
                bgcolor = ' bgcolor = "#ddeeee"'
                header = _("Completed")
                if self.examt != "":
                    exam_details = self.examt
                    if self.examd:
                        exam_details += " %s - %s" % (
                            _("dated"),
                            localsettings.formatDate(self.examd))
                    cells = "<th%s>%s</th>\n<td>%s</td>\n" % (
                        bgcolor, _("Exam"), exam_details)
                    rows.append(cells)

            for att, con_att in (
                ("perio", _("perio")),
                ("xray", _('xray')),
                ("anaes", _('anaes')),
                ("other", _('other')),
                ("custom", _("custom")),
                ('ndu', _("New Denture (upper)")),
                ('ndl', _("New Denture (lower)")),
                ('odu', _("Other Denture (upper)")),
                ('odl', _("Other Denture (lower)")),
            ):
                work = self.__dict__[att + planned]
                if work.strip(" ") != "":
                    cells = "<th%s>%s</th>\n<td>%s</td>\n" % (
                        bgcolor, con_att, sorted_work(work))
                    rows.append(cells)

            show_chart = False
            row1, row2, row3, row4 = "<tr>", "<tr>", "<tr>", "<tr>"

            for att in UPPERS:
                work = self.__dict__[att + planned]
                row1 += '<td>%s</td>\n' % sorted_work(work)
                row2 += '<td align="center"%s>%s</td>\n' % (
                    bgcolor, att.upper())
                show_chart = show_chart or work.strip(" ") != ""

            for att in LOWERS:
                work = self.__dict__[att + planned]
                row3 += '<td align="center"%s>%s</td>\n' % (
                    bgcolor, att.upper())
                row4 += '<td>%s</td>\n' % sorted_work(work)
                show_chart = show_chart or work.strip(" ") != ""

            if show_chart:
                chart_cells = '''<td colspan="2">
                    <table width = "100%%" border = "1">
                    %s</tr>\n%s</tr>\n%s</tr>\n%s</tr>\n</table></td>
                    ''' % (row1, row2, row3, row4)
                rows.append(chart_cells)

            row_span = len(rows)

            if rows != []:
                html += '<tr>\n<th rowspan = "%s"%s>%s</th>\n' % (
                    row_span, bgcolor, header)
            for row in rows:
                if row == rows[0]:
                    html += "%s</tr>\n" % row
                else:
                    html += "<tr>%s</tr>\n" % row

        html += '</table>\n'
        return html


if __name__ == "__main__":
    '''
    testing stuff
    '''
    tc = TreatmentCourse(14469, 45869)
    print(tc)

    print(tc.non_tooth_plan_items)
    print(tc.non_tooth_cmp_items)
    print(tc.all_txs("ur5"))

    f = open("/home/neil/out.html", "w")
    f.write(tc.to_html())
    f.close()
