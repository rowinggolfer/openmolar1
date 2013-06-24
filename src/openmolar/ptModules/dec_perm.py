# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.


def toSignedByte(val):
    lav=list(val)
    if lav[0]=="1":
        retarg=-128
        i=6
        for c in lav[1:8]:
            if c =="1":
                retarg+=2**i
            i-=1
    else:
        retarg=0
        i=7
        for c in lav:
            if c =="1":
                retarg+=2**i
            i-=1
    return retarg

def fromSignedByte(val):
    '''this returns a bit by bit representation of a signed byte - used for deciduous tooth'''
    if val>=0:
        base=(128,64,32,16,8,4,2,1)
        bstring=""
        for b in base:
            if val>=b:
                bstring+="1"
                val-=b
            else:
                bstring+="0"
    else:
        base=(-64,-32,-16,-8,-4,-2,-1)
        bstring="1" #set the negative bit
        for b in base:
            if val<b:
                bstring+="0"
                val-=b
            else:
                bstring+="1"
    return bstring

if __name__=="__main__":
        for byte in(-127,-126,-125,-8,120,32):
            print byte,
            result = fromSignedByte(int(byte))
            print "chart =",result,
            print "and back =",toSignedByte(result)
