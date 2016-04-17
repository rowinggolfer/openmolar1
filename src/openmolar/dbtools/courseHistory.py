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

'''
a module to search for previous course items
'''

import datetime
import logging

from openmolar.settings import localsettings
from openmolar.connect import connect
from openmolar.dbtools.treatment_course import TreatmentCourse
from openmolar.dbtools import estimatesHistory
from openmolar.dbtools import daybook

from openmolar.ptModules.course_checker import CourseChecker

LOGGER = logging.getLogger("openmolar")

QUERY = '''SELECT courseno FROM currtrtmt2 WHERE serialno=%s
ORDER BY courseno desc, accd desc'''

ALLOW_EDIT = False


def _get_courses(sno, current_csno):
    # query allows exclusion of current course.
    if current_csno is None:
        query = QUERY
        values = (sno,)
    else:
        query = QUERY.replace("ORDER", " AND courseno!=%s ORDER")
        values = (sno, current_csno)
    db = connect()
    cursor = db.cursor()
    cursor.execute(query, values)
    rows = cursor.fetchall()
    cursor.close()

    for row in rows:
        yield TreatmentCourse(sno, row[0])


def details(sno, current_csno, include_estimates=False, include_daybook=False):
    '''
    returns an html page showing pt's Treatment History along with estimates
    '''
    courses = list(_get_courses(sno, current_csno))
    estimates_list = estimatesHistory.getEsts(sno) if include_estimates else []
    daybook_list = list(daybook.all_data(sno)) if include_daybook else []
    daybook_course_guesses = {}
    displayed_ests = []
    course_checker_errors = 0

    html = "<body><html><!-- ERRORS --><!-- ORPHANS --><h2>%s - %d %s</h2>" % (
        _("Past Courses of Treatment"),
        len(courses),
        _("found")
    )

    if current_csno is not None:
        html += "<strong>%s %s %s</strong><br />" % (
            _("Ignoring course number"),
            current_csno,
            _("as this is active")
        )

    days_elapsed = None

    for i, course in enumerate(courses):
        course_html = course.to_html(ALLOW_EDIT, days_elapsed)
        course_ests = []

        if include_estimates:
            est_table_init = False
            for est in estimates_list:
                if est.courseno == course.courseno:
                    course_ests.append(est)
                    if not est_table_init:
                        header = est.htmlHeader()
                        if estimatesHistory.ALLOW_EDIT:
                            header = header.replace(
                                "<!--editlink-->",
                                estimatesHistory.EDIT_STRING % est.courseno)
                        course_html += (
                            '<table width="100%%" border="1">%s ' % header)
                        est_table_init = True
                    course_html += est.toHtmlRow()

            if est_table_init:
                course_html += '</table>\n'
            else:
                course_html += "%s %d" % (_("no estimate found for courseno"),
                                          course.courseno)
        displayed_ests += course_ests

        if include_daybook:
            daybook_html = ""
            if course.accd is None:
                accd = datetime.date(1980, 1, 1)
                course_html += "<em>%s</em><br />" % _(
                    "Warning - No course acceptance date")
            else:
                accd = course.accd
            if course.cmpd is None:
                cmpd = datetime.date.today()
                course_html += "<em>%s</em><br />" % _(
                    "Warning - No course completion date, "
                    "using today to gather daybook items.")
            else:
                cmpd = course.cmpd
            for daybook_entry in daybook_list:
                if accd <= daybook_entry.date <= cmpd:
                    try:
                        daybook_course_guesses[course.courseno].append(
                            daybook_entry)
                    except KeyError:
                        daybook_course_guesses[
                            course.courseno] = [
                            daybook_entry]

                    gap = cmpd - daybook_entry.date
                    if daybook.ALLOW_TX_EDITS:
                        id_col = '<a href="daybook_id_edit?%s">%s</a>' % (
                            daybook_entry.id, _("Edit Tx"))
                    else:
                        id_col = str(daybook_entry.id)
                    daybook_html += "<tr><td>%s</td></tr>" % (
                        "</td><td> ".join(
                            (localsettings.formatDate(daybook_entry.date),
                             daybook_entry.coursetype,
                             localsettings.ops.get(daybook_entry.dntid),
                             localsettings.ops.get(daybook_entry.trtid, "-"),
                             daybook_entry.diagn, daybook_entry.perio,
                             daybook_entry.anaes, daybook_entry.misc,
                             daybook_entry.ndu, daybook_entry.ndl,
                             daybook_entry.odu, daybook_entry.odl,
                             daybook_entry.other,
                             daybook_entry.chart.decode(
                                 "utf8").strip(" %s" % chr(0)),
                             localsettings.formatMoney(daybook_entry.feesa),
                             localsettings.formatMoney(daybook_entry.feesb),
                             id_col))
                    )
            if daybook_html:
                header_rows = daybook.all_data_header()
                if course.cmpd is None:
                    header_rows = header_rows.replace(
                        "<!--gap-->", _("Course is Ongoing"))
                elif gap.days != 0:
                    header_rows = header_rows.replace(
                        "<!--gap-->",
                        "%s %s %s" % (_("Course closed"),
                                      gap.days,
                                      _("days after last treatment")))
                course_html += '<table width="100%%" border=1>%s%s</table>' % (
                    header_rows, daybook_html)
            else:
                course_html += "%s<br />" % _(
                    "Course dates not found in daybook")

            if include_estimates and include_daybook:
                course_check = CourseChecker(
                    course,
                    course_ests,
                    daybook_course_guesses.get(course.courseno, []))

                if course_check.has_errors:
                    course_checker_errors += 1
                    course_html += course_check.results
                    course_html += '''<br />
                        <a href="consistent_courseno?%s">%s</a>''' % (
                        course.courseno, _("Examine these Issues."))

        days_elapsed = ""
        try:
            prev_course = courses[i + 1]
            if ALLOW_EDIT:
                merge_link = '<br /><a href="merge_courses?%s+%s">%s?</a>' % (
                    course.courseno, prev_course.courseno,
                    _("Merge with previous course")
                )
                course_html = course_html.replace("<!--merge-->", merge_link)
            days_elapsed = (course.accd - prev_course.cmpd).days
        except IndexError:
            days_elapsed = None
        except TypeError:
            pass
        finally:
            course_html += '<br /><hr /><br />'

        html += course_html

    html += "</html></body>"

    orphaned_html = ""
    i = 0
    for est in estimates_list:
        if est not in displayed_ests and est.courseno != current_csno:
            if i == 0:
                orphaned_html += '''<h1>%s %s</h1>
                <table width="100%%" border="1">%s ''' % (
                    _("WARNING"),
                    _("ORPHANED ESTIMATE DATA"),
                    est.htmlHeader().replace("#ffff99", "red")
                )
            orphaned_html += est.toHtmlRow()
            i += 1

    if course_checker_errors:
        html = html.replace(
            "<!-- ERRORS -->",
            "<h3>%d %s</h3>" % (course_checker_errors, _("Errors Found"))
        )

    if i == 0:
        return html
    return html.replace("<!-- ORPHANS -->",
                        "%s</table><em>%s</em><br />" % (
                            orphaned_html,
                            _("This shouldn't happen!"))
                        )


if __name__ == "__main__":
    # ALLOW_EDIT = True
    localsettings.initiate()
    print(details(27107, 0, True, True))
