# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

import sys
from openmolar.connect import connect
from openmolar.settings import localsettings

private_only = False
nhs_only = False

newfeetable_Headers="section,code,oldcode,USERCODE,regulation,description,description1,NF08,NF08_pt,PFA"

def getFeeHeaders():
    return newfeetable_Headers.split(",")[1:]
def getFeeDict():
    '''returns a dictionary of dictionaries of the feestructure
    dict[section]=feedict
    feedict[code]=("item description",fees)
    '''
    global newtable_Headers
    option=""
    if private_only:
        option+="where PFA>0"
    elif nhs_only:
        option+="where NF08>0"

    db=connect()
    cursor=db.cursor()
    cursor.execute('select %s from newfeetable %s'%(newfeetable_Headers,option))
    feescales = cursor.fetchall()
    cursor.close()
    #db.close()

    sections={}

    for row in feescales:
        if not sections.has_key(row[0]):
            sections[row[0]]={}
        feecode=row[1]
        while sections[row[0]].has_key(feecode):
            feecode+="."
        sections[row[0]][feecode]=row[2:]
    return sections

def decode(blob):
    '''decode in blocks of 4 bytes - this is a relic from the old database
    '''
    i=0
    retlist=[]
    for i in range(0,len(blob),4):
        cost=struct.unpack_from('H',blob,i)[0]
        retlist.append(cost)
    return retlist


def feesHtml():
    return toHtml(getFees())

if __name__ == "__main__":
    #localsettings.initiate(False)
    #print localsettings.privateFees
    print getFeeDict()
