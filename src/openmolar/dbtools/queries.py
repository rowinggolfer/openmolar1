#! /usr/bin/env python
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

PATIENT_QUERY_FIELDS = (
    "money0", "money1", "money2", "money3", "money4", "money5", "money6",
    "money7", "money8", "money9", "money10",
    "pd0", "pd1", "pd2", "pd3", "pd4", "pd5", "pd6", "pd7",
    "pd8", "pd9", "pd10", "pd11", "pd12", "pd13", "pd14",
    "sname", "fname", "title", "sex", "dob",
    "addr1", "addr2", "addr3", "pcde", "tel1", "tel2",
    "occup", "nhsno", "cnfd", "cset", "dnt1", "dnt2", "courseno0",
    "ur8", "ur7", "ur6", "ur5", "ur4", "ur3", "ur2", "ur1", "ul1", "ul2", "ul3",
    "ul4", "ul5", "ul6", "ul7", "ul8", "ll8", "ll7", "ll6", "ll5", "ll4", "ll3",
    "ll2", "ll1", "lr1", "lr2", "lr3", "lr4", "lr5", "lr6", "lr7", "lr8",
    "dent0", "dent1", "dent2", "dent3", "billdate", "billct", "billtype",
    "money11", "familyno", "memo", "town", "county", "mobile", "fax", "email1",
    "email2", "status", "initaccept", "lastreaccept",
    "lastclaim", "expiry", "cstatus", "transfer", "pstatus"
)

PATIENT_QUERY = '''SELECT %s
from new_patients
left join patient_money on serialno = patient_money.pt_sno
left join static_chart on serialno = static_chart.pt_sno
left join patient_dates on serialno = patient_dates.pt_sno
left join patient_nhs on serialno = patient_nhs.pt_sno
where serialno = %%s''' % ", ".join(PATIENT_QUERY_FIELDS)

FUTURE_EXAM_QUERY = '''select count(*) from aslot
where serialno=%s
and (code0="EXAM" or code1="EXAM" or code2="EXAM") and adate >= CURDATE()'''

PSN_QUERY = "select psn from previous_snames where serialno=%s order by ix desc"

FAMILY_COUNT_QUERY = "select count(*) from new_patients where familyno=%s"

QUICK_MED_QUERY = 'select alert, chkdate from medhist where pt_sno=%s order by ix desc limit 1'

MED_FORM_QUERY = '''select chk_date from medforms where pt_sno=%s
order by chk_date desc'''

SYNOPSIS_QUERY = 'SELECT synopsis from clinical_memos where serialno=%s'
