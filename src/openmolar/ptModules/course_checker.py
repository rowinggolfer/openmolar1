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

import datetime
import logging
import re

from openmolar.dbtools.treatment_course import TreatmentCourse
from openmolar.dbtools import estimatesHistory
from openmolar.dbtools import daybook

LOGGER = logging.getLogger("openmolar")


class CourseChecker(object):
    '''
    look to see if there is consistency accross three tables
    currtrtmt2, daybook and newestimates
    '''
    def __init__(self, course, estimates, daybook_entries):
        self.course = course
        self.estimates = estimates
        self.daybook_entries = daybook_entries
        self._daybook_course = None
        self._courses_match = None

    @property
    def serialno(self):
        return self.course.serialno

    @property
    def courseno(self):
        return self.course.courseno

    @property
    def is_ongoing(self):
        return self.course.cmpd is None

    @property
    def days_at_course_end(self):
        if self.is_ongoing:
            return 0
        dead_space = 0
        for daybook_entry in self.daybook_entries:
            days = (self.course.cmpd - daybook_entry.date).days
            if dead_space > days:
                dead_space = days
        return dead_space

    @property
    def daybook_course(self):
        '''
        This is the daybook entries converted to a Treatment Course
        '''
        if self._daybook_course is None:
            self._daybook_course = TreatmentCourse(self.serialno, 0)
            self._daybook_course.courseno = self.courseno
            accd, cmpd = None, None
            for daybook_entry in self.daybook_entries:
                if not accd or daybook_entry.date < accd:
                    accd = daybook_entry.date
                if not cmpd or daybook_entry.date > cmpd:
                    cmpd = daybook_entry.date
                # diagn
                m = re.search("(E?CE) ", daybook_entry.diagn)
                if m:
                    self._daybook_course.examt += m.groups()[0]
                    self._daybook_course.examd = daybook_entry.date
                # xray
                for xray in re.findall(r"\d?[S|M|P] ", daybook_entry.diagn):
                    self._daybook_course.xraycmp += xray
                # perio
                if daybook_entry.perio.strip(" "):
                    self._daybook_course.periocmp += \
                        daybook_entry.perio.strip(" ") + " "
                # anaes
                if daybook_entry.anaes.strip(" "):
                    self._daybook_course.anaescmp += \
                        daybook_entry.anaes.strip(" ") + " "
                # misc
                if daybook_entry.misc.strip(" "):
                    self._daybook_course.customcmp += \
                        daybook_entry.misc.strip(" ") + " "
                # ndu
                if daybook_entry.ndu.strip(" "):
                    self._daybook_course.nducmp += \
                        daybook_entry.ndu.strip(" ") + " "
                # ndl
                if daybook_entry.ndl.strip(" "):
                    self._daybook_course.ndlcmp += \
                        daybook_entry.ndl.strip(" ") + " "
                # odu
                if daybook_entry.odu.strip(" "):
                    self._daybook_course.oducmp += \
                        daybook_entry.odu.strip(" ") + " "
                # odl
                if daybook_entry.odl.strip(" "):
                    self._daybook_course.odlcmp += \
                        daybook_entry.odl.strip(" ") + " "
                # other
                if daybook_entry.other.strip(" "):
                    self._daybook_course.othercmp += \
                        daybook_entry.other.strip(" ") + " "
                # chart
                chart_entries = daybook_entry.chart.decode("utf8").split("  ")
                for chart_entry in chart_entries:
                    m = re.match("([UL][LR][1-8]) (.*)", chart_entry)
                    if m:
                        att = "%scmp" % m.groups()[0].lower()
                        tx = m.groups()[1] + " "
                        self._daybook_course.__dict__[att] += tx

            if accd is None or (self.course.accd and self.course.accd < accd):
                self._daybook_course.accd = self.course.accd
            else:
                self._daybook_course.accd = accd
            self._daybook_course.cmpd = cmpd

        return self._daybook_course

    def completed_txs_match_daybook(self):
        for hash_, att, tx in self.course.completed_tx_hash_tups:
            print("checking '%s' '%s'" % (att, tx))

    @property
    def results(self):
        message = "<ul>"
        if self.is_ongoing:
            message += "<li>%s</li>" % _("Course is still active")
        dead_days = self.days_at_course_end
        if dead_days:
            message += "<li>%s %d %s.</li>" % (
                _("Course closed"),
                dead_days,
                _("days after last day treatment"))
        if not self.courses_match:
            message += "<li>%s</li>" % _(
                "Course doesn't tally with daybook entries")
        message += "</ul>"
        return message if message != "<ul></ul>" else _("No warnings")

    @property
    def courses_match(self):
        if self._courses_match is None:
            html = self.daybook_course.to_html()
            html1c = self.course.to_html(completed_only=True)
            self._courses_match = html == html1c
        return self._courses_match

    @property
    def has_errors(self):
        '''
        currently this looks for consistency betwwen the daybook
        and treatment plan only
        '''
        return (self.days_at_course_end > 0 or
                self.is_ongoing or
                not self.courses_match)


def get_course_checker(serialno, courseno):
    course = TreatmentCourse(serialno, courseno)
    ests = estimatesHistory.getEsts(serialno, courseno)
    daybook_list = []
    accd = datetime.date.today() if course.accd is None else course.accd
    cmpd = datetime.date.today() if course.cmpd is None else course.cmpd
    for daybook_entry in daybook.all_data(serialno):
        if accd <= daybook_entry.date <= cmpd:
            daybook_list.append(daybook_entry)

    return CourseChecker(course, ests, daybook_list)


if __name__ == "__main__":
    serialno = 11956
    courseno = 29749

    course_check = get_course_checker(serialno, courseno)
    print(course_check.results)

    course_check.completed_txs_match_daybook()

    print(course_check.daybook_course.to_html())
