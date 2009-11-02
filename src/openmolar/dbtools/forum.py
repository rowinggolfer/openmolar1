# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for
# more details.

import sys,datetime
from openmolar.connect import forumConnect,connect
from openmolar.settings import localsettings

headers=["db_index",_("topic"),_("author"), _("recipient"),
_("submitted"),_("comment")]

class post():
    def __init__(self):
        self.ix=None
        self.parent_ix=None
        self.inits=""
        self.recipient=None
        self.date=None
        self.topic=""
        self.comment=""
        self.briefcomment=""
        self.open=True

def commitPost(post):
    #use a different connection for forum, as it runs in a separate thread

    db=connect() 
    cursor=db.cursor()
    columns="parent_ix,inits,recipient,fdate,topic,comment"
    
    values=(post.parent_ix,post.inits,post.recipient,
    datetime.datetime.now(),post.topic,post.comment)

    query="insert into forum (%s) "% columns
    query+="VALUES (%s,%s,%s,%s,%s,%s)"
    if localsettings.logqueries:
        print query,values
    cursor.execute(query,values)
    db.commit()
    cursor.close()
    #db.close()
    
def deletePost(ix,table="forum"):
    db=connect()
    cursor=db.cursor()
    query="select parent_ix from %s where ix=%d"%(table,ix)
    if localsettings.logqueries:
        print query
    parent=None
    if cursor.execute(query):
        parent=cursor.fetchone()[0]
    print parent
    if parent==None:parent='Null'
    
    query="update %s set open=False where ix=%d"%(table,ix)
    query2='update %s set parent_ix=%s where parent_ix=%d'%(table,parent,ix)
    if True or localsettings.logqueries:
        print query
        print query2
    print cursor.execute(query2)
    print cursor.execute(query)    
    db.commit()
    cursor.close()
    #db.close()
    
def newPosts():
    #--use a different connection because this is called in a thread
    users = localsettings.operator.split("/")
    print "checking for new posts for ", users
    if users == []:
        return
    db=forumConnect()
    cursor=db.cursor()
    query='''select max(ix) from forum'''
    cursor.execute(query)
    row = cursor.fetchone()
    query="select max(id) from forumread where recipient=NULL"
    for user in users:
        query += " or recipient='%s'"% user
    cursor.execute(query)
    row2 = cursor.fetchone()
    
    cursor.close()
    db.close()
    
    return row[0] > row2[0]
        
    
def getPosts(table="forum"):
    '''
    gets all active rows from a forum table
    '''

    db=connect()
    cursor=db.cursor()
    query='''select ix, parent_ix,topic,inits,fdate, recipient, comment 
    from %s where open order by parent_ix,ix'''%table

    if localsettings.logqueries:
        print query
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    #db.close()
    retarg=[]
    for row in rows:
        newpost=post()
        newpost.ix=row[0]
        newpost.parent_ix=row[1]
        newpost.topic=row[2]
        newpost.inits=row[3]
        newpost.date=row[4]
        newpost.recipient = row[5]
        newpost.comment=row[6]
        newpost.briefcomment=row[6][:40]
        if newpost.comment!=newpost.briefcomment:
            newpost.briefcomment+="...."
        retarg.append(newpost)
    return retarg

if __name__ == "__main__":
    posts = getPosts()
    for post in posts:
        print post.topic
    #deletePost(20,"omforum")
    print lastPost()
    