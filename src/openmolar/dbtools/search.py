# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

'''this script connects to the database and performs searches'''

import sys
from openmolar.connect import connect
from openmolar.settings import localsettings

def getcandidates(dob,addr,tel,sname,similar_sname,fname,similar_fname,pcde):
    '''this searches the database for patients matching the given fields'''
    query=''
    if addr!='':
        query+='(ADDR1 like %s or '%(r'"%'+addr+r'%"')
        query+='ADDR2 like %s) and '%(r'"%'+addr+r'%"')
    if tel!='':
        query+='tel1 like %s and '%(r'"%'+tel+r'%"')
    if str(dob)!='00000000' and str(dob)!="no date":
        query+='dob="%s" and '%dob
    if pcde!='':
        query+='pcde like %s and '%(r'"%'+pcde+r'%"')
    if sname!='':
        if similar_sname:
            query+='sname sounds like "%s" and '%sname
        else:
            query+='sname like %s and '%('"'+sname+r'%"')
    if fname!='':
        if similar_fname:
            query+='fname sounds like "%s" and '%fname
        else:
            query+='fname like %s and '%('"'+fname+r'%"')

    if query!='':
        fields='serialno,sname,fname,DATE_FORMAT(dob,"%s"),addr1,addr2,pcde,tel1,tel2,mobile'%localsettings.sqlDateFormat #this needs to be the headers in qt4gui/main select_patient()
        query="select %s from patients where %s order by sname,fname"%(fields,query[0:query.rindex("and")])
        if "demo" in localsettings.DBNAME:
            #demo db uses the same name and address for everyone!
            query += " limit 10"

        if localsettings.logqueries:
            print query
        db=connect()
        cursor = db.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        #db.close()
        return results
    else:
        return ()

def getsimilar(serialno,addr,sname,family):
    '''this searches the database for patients matching the given fields'''
    db=connect()
    cursor = db.cursor()
    fields='serialno,sname,fname,DATE_FORMAT(dob,"%s"),addr1,addr2,pcde'%localsettings.sqlDateFormat #this needs to be the headers in qt4gui/main select_patient()
    if family>0:
        query="select %s from patients where serialno != %d and familyno=%d order by dob"%(fields,serialno,family)

        if localsettings.logqueries:
            print query

        cursor.execute(query)
        families = cursor.fetchall()
    else:
        families=()

    if addr!='':
        query='(ADDR1 like "%%%s%%" or ADDR2 like "%%%s%%")'% (addr,addr)
        query='''select %s from patients where serialno != %d
        and %s order by fname,sname'''% (fields,serialno,query)
        if "demo" in localsettings.DBNAME:
            #demo db uses the same name and address for everyone!
            query += " limit 10"

        if localsettings.logqueries:
            print query

        cursor.execute(query)
        addresses = cursor.fetchall()
    else:
        addresses=()
    query='select %s from patients where serialno != %d and sname sounds like "%s" order by fname,sname'%(fields,serialno,sname)
    if "demo" in localsettings.DBNAME:
            #demo db uses the same name and address for everyone!
            query += " limit 10"

    if localsettings.logqueries:
            print query

    cursor.execute(query)
    snames = cursor.fetchall()

    cursor.close()
    #db.close()
    return (families,addresses,snames)

def getcandidates_from_serialnos(list_of_snos):
    query=""
    for sno in list_of_snos:
        query+="serialno=%d or "%sno
    if query!='':
        fields='serialno,sname,fname,DATE_FORMAT(dob,"%s"),addr1,addr2,pcde,tel1,tel2,mobile'%localsettings.sqlDateFormat #this needs to be the headers in qt4gui/main select_patient()
        query="select %s from patients where %s order by sname,fname"%(fields,query[:query.rindex("or")])
        if localsettings.logqueries:
            print query

        db=connect()
        cursor = db.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        #db.close()
        return results
    else:
        return()
if __name__=='__main__':
    print getcandidates("0000-00-00","","","wallace","","","","")
    print getcandidates_from_serialnos((1,2,3,4))