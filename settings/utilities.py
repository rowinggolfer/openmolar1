# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License
# for more details.

import os

def getPDF():
    '''
    get's the pdf which has been created to local file during some print proc
    '''
    try:
        f=open("temp.pdf","rb")
        data=f.read()
        f.close()
        return data
    except Exception,e:
        print "error in utilities.getPdf"
        print Exception,e
        
def deletePDF():
    '''
    delete's any temprorary pdf file
    '''
    if os.exists("temp.pdf"):
        os.remove("temp.pdf")
    
if __name__ == "__main__":
    '''testing only'''
    