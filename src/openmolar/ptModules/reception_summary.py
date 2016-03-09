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
this module provides an html summary of the patient's reception activity
'''

from gettext import gettext as _

from openmolar.settings import localsettings
from openmolar.dbtools import paymentHistory
from openmolar.dbtools import estimate_synopsis

HTML_TEMPLATE = '''
<html>
<head><link rel="stylesheet" href="%s" type="text/css">
</head>
<body>
<!-- HEADER -->
{{CONTENT}}
</body>
</html>
''' % localsettings.stylesheet


ACTIVE_HTML_TEMPLATE = HTML_TEMPLATE.replace("{{CONTENT}}", '''
{{HEADER}}
<hr />
{{TREATMENTS}}
<hr />
{{PAYMENTS}}
''')

UNKNOWN_DENT = ("??", _("Unknown"), _("Unknown"), "", "")


def header_html(pt):

    if pt.underTreatment:
        html_ = "<h3>Patient is under Treatment</h3>course started %s" % (
            localsettings.readableDate(pt.treatment_course.accd))
    else:
        html_ = "<h3>Last course of treatment</h3>completed %s" % (
            localsettings.readableDate(pt.treatment_course.cmpd))

    return html_


def treatment_html(pt):
    return "<h4>Treatments (courseno %s)</h4>%s" % (
        pt.courseno0, estimate_synopsis.html(pt.serialno, pt.courseno0))


def payments_html(pt):
    return '''<h4>Payments Since this course began (excluding Sundries)</h4>
        %s ''' % paymentHistory.summary_details(
        pt.serialno, pt.treatment_course.accd)


def active_course_html(pt):
    html_ = ACTIVE_HTML_TEMPLATE.replace("{{TREATMENTS}}", treatment_html(pt))
    html_ = html_.replace("{{PAYMENTS}}", payments_html(pt))
    html_ = html_.replace("{{HEADER}}", header_html(pt))

    return html_


def summary_html(pt):
    key_values = []
    key_values.append((
        _("Contract Dentist"),
        localsettings.dentDict.get(pt.dnt1, UNKNOWN_DENT)[1]
        ))

    days = (localsettings.currentDay() - pt.first_note_date).days
    if days < 7:
        duration = _("this week")
    elif days < 365:
        duration = _("recently")
    elif days < 730:
        duration = _("last year")
    else:
        duration = "%s %s" % (days//365, _("years ago."))

    key_values.append((
        _("Joined the practice"),
        duration
        ))

    key_values.append((
        _("Last Treatment"),
        localsettings.formatDate(pt.last_treatment_date)
        ))

    key_values.append((
        _("Exam Due"),
        _("YES!") if pt.exam_due else _("No")
        ))

    key_values.append((
        _("Has seen hygienist on"),
        "%s %s" % (pt.n_hyg_visits, _("Occasions"))
        ))

    phone = False
    for i, val in enumerate((pt.tel1, pt.tel2, pt.mobile)):
        if val:
            key = (_("Telephone (Home)"),
                   _("Telephone (Work)"),
                   _("Mobile"))[i]
            key_values.append((key, val))
            phone = True
    if not phone:
        key_values.append((_("Telephone"), _("Please get a phone number")))

    content = "<ul>"
    for key, value in key_values:
        content += "<li><b>%s</b> - %s</li>" % (key, value)
    content += "</ul>"
    html_ = HTML_TEMPLATE.replace("{{CONTENT}}", content)

    return html_


def finished_today_html(pt):
    return active_course_html(pt).replace(
        "<!-- HEADER -->",
        _("COMPLETED COURSE TODAY")
        )


def html(pt, summary=True):
    if summary:
        return summary_html(pt)

    if pt.last_treatment_date == localsettings.currentDay():
        return finished_today_html(pt)
    return active_course_html(pt)


if __name__ == '__main__':
    from openmolar.dbtools.patient_class import patient
    localsettings.initiate()

    pt = patient(26041)
    html = html(pt)
    print(html)
