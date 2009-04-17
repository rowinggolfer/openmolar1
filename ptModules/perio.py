# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

'''gets and decodes the perio charts'''

import sys
from openmolar.settings import localsettings
from openmolar.connect import connect

import struct

def get_perioData(data):
    perioData={}

    i=0
    for tooth in ('ur8','ur7','ur6','ur5','ur4','ur3','ur2','ur1','ul1','ul2','ul3','ul4','ul5','ul6','ul7','ul8',
        'lr8','lr7','lr6','lr5','lr4','lr3','lr2','lr1','ll1','ll2','ll3','ll4','ll5','ll6','ll7','ll8'):
        d=struct.unpack_from('b'*45,data,i)
        recession=(d[0],d[1],d[2],d[3],d[4],d[5])
        pocketing=(d[6],d[7],d[8],d[9],d[10],d[11])
        plaque=(d[12],d[13],d[14],d[15],d[16],d[17])
        bleeding=(d[18],d[19],d[20],d[21],d[22],d[23])
        other=(d[24],d[25],d[26],d[27],d[28],d[29])
        mobility=d[34]
        furcation=(d[30],d[31],d[32],d[33])
        suppuration=(d[35],d[36],d[37],d[38],d[39],d[40])
        perioData[tooth]=(recession,pocketing,plaque,bleeding,other,suppuration,furcation,mobility)
        i+=45

    return perioData

if __name__ == "__main__":
    try:
        serialno=int(sys.argv[len(sys.argv)-1])
    except:
        serialno=707 #29833
    db=connect()
    cursor=db.cursor()
    cursor.execute('select chartdata from perio where serialno=%d'%serialno)
    chartdata=cursor.fetchall()
    cursor.close()
    #db.close()
    perioData=get_perioData(chartdata[0][0])
    newdict={}
    for key in perioData.keys():
    #    print key,perioData[key]
        newdict[key]=perioData[key][1]
    print newdict