# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

def toHtml(p1,p2):
    '''this sub puts all the attributes found for patient 1 and patient 2 (normally a shallow copy) into an html table (for comparison)'''
    retarg='<html><body><table width="100%" border="1">'
    retarg+='<tr><th>Attribute</th><th>orig</th><th>changed</th>'
    attribs=p1.__dict__.keys()
    attribs.sort()
    for att in attribs:
        if att[0:3] in ('ur8','ur7','ur6','ur5','ur4','ur3','ur2','ur1','ul1','ul2','ul3','ul4','ul5','ul6','ul7','ul8',
        'lr8','lr7','lr6','lr5','lr4','lr3','lr2','lr1','ll1','ll2','ll3','ll4','ll5','ll6','ll7','ll8'):
            retarg+= "<tr><td>%s</td><td>'%s'</td><td>'%s'</td></tr>"%(att,p1.__dict__[att],p2.__dict__[att])
        
        elif not att in ('addr1','addr2','addr3','chartgrid','county','cset','dob','occup'
        'email1','email2','familyno','fax','fname','memo','pcde','recd','serialno','sex','sname','tel1','tel2','title','town','notestuple'):
            retarg+= "<tr><td>%s</td><td>%s</td><td>%s</td></tr>"%(att,p1.__dict__[att],p2.__dict__[att])
    retarg +='</table></body></html>'
    return retarg
