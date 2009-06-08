# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for
# more details.

import sys
from openmolar.connect import connect
from openmolar.settings import localsettings

headers=["topic","submitted","initials","Comment"]

def getPosts(table="forum"):
    '''
    gets all active rows from a forum table
    '''

    db=connect()
    cursor=db.cursor()
    query='''select
    ix, parent_ix,topic,fdate,inits,comment from %s where open'''%table

    if localsettings.logqueries:
        print query
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    #db.close()

    return rows

if __name__ == "__main__":
    posts = getPosts()
    for post in posts:
        print post
