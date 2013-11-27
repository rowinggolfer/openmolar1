# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

ESTS_QUERY = '''SELECT newestimates.ix, number, itemcode, description,
fee, ptfee, feescale, csetype, dent, est_link2.completed, tx_hash
from newestimates right join est_link2 on newestimates.ix = est_link2.est_id
where serialno=%s and courseno=%s order by itemcode, ix'''

PATIENT_QUERY = '''SELECT pf0, pf1, pf2, pf3, pf4, pf5, pf6, pf7, pf8, pf9,
pf10, pf11, pf12, pf14, pf15, pf16, pf17, pf18, pf19, money0, money1, money2,
money3, money4, money5, money6, money7, money8, money9, money10,
pd0, pd1, pd2, pd3, pd4, pd5, pd6, pd7, pd8, pd9, pd10, pd11, pd12, pd13,
pd14, sname, fname, title, sex, dob, addr1, addr2, addr3, pcde, tel1, tel2,
occup, nhsno, cnfd, psn, cset, dnt1, dnt2, courseno0, courseno1,
ur8st, ur7st, ur6st, ur5st, ur4st, ur3st, ur2st, ur1st, ul1st, ul2st, ul3st,
ul4st, ul5st, ul6st, ul7st, ul8st, ll8st, ll7st, ll6st, ll5st, ll4st, ll3st,
ll2st, ll1st, lr1st, lr2st, lr3st, lr4st, lr5st, lr6st, lr7st, lr8st, dent0,
dent1, dent2, dent3, dmask, minstart, maxend, billdate, billct, billtype,
pf20, money11, pf13, familyno, memo, town, county, mobile, fax, email1,
email2, status, source, enrolled, archived, initaccept, lastreaccept,
lastclaim, expiry, cstatus, transfer, pstatus, courseno2
from patients where serialno = %s'''
