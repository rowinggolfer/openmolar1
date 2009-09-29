# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.

from openmolar import connect
from openmolar.settings import localsettings

class task():
    '''
    a custom data type to hold a row from the task table
    '''
    def __init__(self):
        self.ix = None
        self.op = ""
        self.author = ""
        self.type = ""
        self.mdate = None
        self.due = None
        self.message = ""
        self.completed = False
        self.visible = False

def getTasks():
    '''
    poll the database for tasks
    '''
    retarg = []
    db = connect.connect()
    query = '''select ix, op, author, type, mdate, due, message,
    completed, visible from tasks'''
    
    if localsettings.logqueries:
        print query
    cursor = db.cursor()
    try:
        cursor.execute(query)
        rows=cursor.fetchall()
    except connect.ProgrammingError, ex:
        print "tasks table not found?", ex
        #- test row
        rows = (
        (1,"NW","NW","","","","X-ray Door",False,True),
        (1,"NW","NW","","","","Referal to Buchanan",False,True),
        (1,"NW","NW","","","","Surgery Door",False,True),)
    cursor.close()
    for row in rows:
        newtask=task()
        newtask.ix = row[0]
        newtask.op = row[1]
        newtask.author = row[2]
        newtask.type = row[3]
        newtask.mdate = row[4]
        newtask.due = row[5]
        newtask.message = row[6]
        newtask.completed = row[7]
        newtask.visible = row[8]
        retarg.append(newtask)
    return retarg

def updateTask(task):
    '''
    update a task which is already in the database
    '''
    db = connect.connect()
    
    values = (task.op, task.author, task.type, task.mdate, task.due, 
    task.message, task.completed, task.visible)
    
    query = '''update tasks set op=%s, author=%s, type=%s, mdate=%s, due=%s,
    message=%s, completed=%s, visible=%s ''' 
    query += "where ix = %d"% task.ix
    if localsettings.logqueries:
        print query, values
    cursor = db.cursor()
    result=cursor.execute(query, values)
    db.commit()
    cursor.close()
    #db.close()
    return result

def savetask(task):
    '''
    put a task into the database
    '''
    db = connect.connect()
    
    values = (task.op, task.author, task.type, task.mdate, task.due, 
    task.message, task.completed, task.visible)
    
    query = '''insert into tasks 
    (op, author, type, mdate, due, message,completed, visible) 
    VALUES (%s ,%s ,%s ,%s ,%s ,%s ,%s , %s)'''
    if localsettings.logqueries:
        print query, values
    cursor = db.cursor()
    result=cursor.execute(query, values)
    db.commit()
    cursor.close()
    #db.close()
    return result

if __name__ == "__main__":
    test_task = task()
    print saveTask(test_task)
