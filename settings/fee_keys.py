# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.


exam={
"CE":101,
"ECE":111,
"FCA":121
}

xray={
"S":201,
"M":202,
"P":204
}

perio={
"SP":1001,
"SP+":1011,
}

fill={
"am 1s":1401,
"am 2s":1402,
"am mo/do":1403,
"am mod":1404,
"tnl rest":1411,
"comp 1s":1415,
"comp 2s":1416,
"comp 3s":1417,
"comp >3s":1418,
"comp":1421,
"gl/sil":1426,
"fs":1441,
"fs comp":1442,
}

rct={
"root flg":1501,
"apic 1-3":1521,
"apic 4-5":1522,
"apic bucc":1523,
"apic 6-8":1531,
"apic/rr":1541,
}

veneer={
"pcln vnr":1601,
}

surgery={
"extr":2101,
}


def getExamCode(arg):
    if exam.has_key(arg):
        return exam[arg]
    
def getPerioCode(arg):
    if perio.has_key(arg):
        return perio[arg]
    else:
        if perio.has_key(arg[:3]):  #SP+
            return perio[arg[:3]]
        
def getCrownCode(arg):
    if arg=="PV":
        return veneer["pcln vnr"]
    
def getKey(arg):
    if arg[:2] in ("PV","CR","BR","PI"):
        return getCrownCode(arg)
    if len(arg)==1:
        return fill["am 1s"]
    elif arg[-3:]==",GL":
        return fill["gl/sil"] 
    elif arg=="MO" or arg=="DO":
        return fill["am 2s"]
    elif arg=="MOD":
        return fill["am mod"]    
    elif arg=="FS":
        return fill["fs"]
    elif arg=="FS,CO":
        return fill["fs comp"]
    elif arg=="RT":
        return rct["root flg"]
    elif arg=="EX":
        return surgery["extr"]








if __name__ == "__main__":
    for arg in ("EX","MOD","PV"):
        print getToothCode(arg)