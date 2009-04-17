# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.


import sys,datetime,time,pickle
from openmolar.connect import connect
from openmolar.ptModules import perio,dec_perm,estimates
from openmolar.settings import localsettings


dateFields=("dob","pd0","pd1","pd2","pd3","pd4","pd5","pd6","pd7","pd8","pd9","pd10",
"pd11","pd12","pd13","pd14","cnfd","recd","billdate","enrolled","initaccept","lastreaccept",
"lastclaim","expiry","transfer","chartdate","accd","cmpd","examd","bpedate")

nullDate=""
#nullDate=datetime.date(1900, 1, 1)

patientTableAtts=(
'pf0','pf1','pf2','pf3','pf4','pf5','pf6','pf7','pf8','pf9','pf10','pf11','pf12','pf14','pf15','pf16','pf17','pf18','pf19',
'money0','money1','money2','money3','money4','money5','money6','money7','money8','money9','money10',
'pd0','pd1','pd2','pd3','pd4','pd5','pd6','pd7','pd8','pd9','pd10','pd11','pd12','pd13','pd14',
'sname','fname','title','sex','dob', 'addr1','addr2','addr3','pcde','tel1','tel2','occup',
'nhsno','cnfd','psn','cset','dnt1','dnt2','courseno0','courseno1','exempttext',
'ur8st','ur7st','ur6st','ur5st','ur4st','ur3st','ur2st','ur1st',
'ul1st','ul2st','ul3st','ul4st','ul5st','ul6st','ul7st','ul8st',
'll8st','ll7st','ll6st','ll5st','ll4st','ll3st','ll2st','ll1st',
'lr1st','lr2st','lr3st','lr4st','lr5st','lr6st','lr7st','lr8st',
'dent0','dent1','dent2','dent3','exmpt','recd',
'dmask','minstart','maxend','billdate','billct',
'billtype','pf20','money11','pf13','familyno','memo',
'town','county','mobile','fax','email1','email2','status','source','enrolled','archived',
'initaccept','lastreaccept','lastclaim','expiry','cstatus','transfer','pstatus','courseno2')
patientTableVals=(
0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,0,0,0,
nullDate, nullDate, nullDate, nullDate, nullDate, nullDate, nullDate, nullDate, nullDate, nullDate, nullDate, nullDate, nullDate, nullDate,nullDate,
'','','','',nullDate,'','', '','', '','', '',
'',nullDate, '','',0,0,0,0,'',
'','', '','', '','', '','',
'','', '','', '','', '','',
'','', '','', '','', '','',
'','', '','', '','', '','',
0,0,0,0,'',nullDate,
'',0,0,nullDate,0,
'',0,0,0,0,'',
'','','','','','','','',nullDate,0,
nullDate,nullDate,nullDate,nullDate,0,nullDate,0,0)

bpeTableAtts=('bpedate','bpe')
bpeTableVals=(nullDate,'',())

currtrtmtTableAtts=('courseno','xraypl','periopl','anaespl','otherpl','ndupl','ndlpl','odupl',
'odlpl','xraycmp','periocmp','anaescmp','othercmp','nducmp','ndlcmp','oducmp','odlcmp','ur8pl','ur7pl',
'ur6pl','ur5pl','ur4pl','ur3pl','ur2pl','ur1pl','ul1pl','ul2pl','ul3pl','ul4pl','ul5pl','ul6pl','ul7pl',
'ul8pl','ll8pl','ll7pl','ll6pl','ll5pl','ll4pl','ll3pl','ll2pl','ll1pl','lr1pl','lr2pl','lr3pl','lr4pl',
'lr5pl','lr6pl','lr7pl','lr8pl','ur8cmp','ur7cmp','ur6cmp','ur5cmp','ur4cmp','ur3cmp','ur2cmp','ur1cmp',
'ul1cmp','ul2cmp','ul3cmp','ul4cmp','ul5cmp','ul6cmp','ul7cmp','ul8cmp','ll8cmp','ll7cmp','ll6cmp','ll5cmp',
'll4cmp','ll3cmp','ll2cmp','ll1cmp','lr1cmp','lr2cmp','lr3cmp','lr4cmp','lr5cmp','lr6cmp','lr7cmp','lr8cmp',
'examt','examd','accd','cmpd')

perioTableAtts=('chartdate','bpe','chartdata','flag')

mnhistTableAtts=('chgdate','ix','note')

prvfeesTableAtts=('courseno','dent','esta','acta','estb','actb','data')

notesTableAtts=('lineno','line')

mouth= ['ul8','ul7','ul6','ul5','ul4','ul3','ul2','ul1','ur1','ur2','ur3','ur4','ur5','ur6','ur7','ur8',
'lr8','lr7','lr6','lr5','lr4','lr3','lr2','lr1','ll1','ll2','ll3','ll4','ll5','ll6','ll7','ll8']
decidmouth= ['***','***','***','ulE','ulD','ulC','ulB','ulA','urA','urB','urC','urD','urE','***','***','***',
'***','***','***','lrE','lrD','lrC','lrB','lrA','llA','llB','llC','llD','llE','***','***','***']


class patient():
    def __init__(self,sno):
        '''initiate the class with default variables, then load from database'''
        self.serialno=sno
        i=0
        for att in patientTableAtts:
            self.__dict__[att]=patientTableVals[i]
            i+=1
        ######TABLE 'mnhist'#######
        self.chgdate =nullDate # date 	YES 	 	None
        self.ix = 0 #tinyint(3) unsigned 	YES 	 	None
        self.note='' #varchar(60) 	YES 	 	None

        ######data from the completed table#########
        for att in currtrtmtTableAtts:
            if att =='courseno':
                self.__dict__[att]=0
            elif att in ('examd','accd','cmpd'):
                self.__dict__[att]=nullDate
            else:
                self.__dict__[att]=""

        #from prvfees
        self.estimates=()
        self.tsfees=()

        ####NEIL'S STUFF####
        self.perioData={}
        self.bpe=[]
        self.fees=0
        self.notestuple=()
        self.estimates=()
        self.currEstimate=((),0)
        self.MH=()
        self.MEDALERT=False
        self.HIDDENNOTES=[]
        self.chartgrid={}
        self.dayBookHistory=()
        self.underTreatment=False

        if self.serialno!=0:
            #load stuff from the database
            db=connect()
            cursor = db.cursor()
            ############################experiment
            cursor.execute('select DATE_FORMAT(bpedate,"%s"),bpe from bpe where serialno=%d'%(localsettings.sqlDateFormat,self.serialno))
            values = cursor.fetchall()
            for value in values:
                self.bpe.append(value)

            #table - patients

            fields=patientTableAtts
            query=""
            for field in fields:
                if field in dateFields:
                    query+='DATE_FORMAT(%s,"%s"),'%(field,localsettings.sqlDateFormat)
                else:
                    query+=field+","
            query=query.strip(",")
            cursor.execute('select %s from patients where serialno=%d'%(query,self.serialno))
            values= cursor.fetchall()
            i=0
            for field in fields:
                if values[0][i] !=None:
                    self.__dict__[field]=values[0][i]
                i+=1
            
            self.getCurrtrt(cursor)
            self.getEsts(cursor)
            self.getNotesTuple(cursor)

            cursor.execute('select chartdate,chartdata from perio where serialno=%d'%self.serialno)
            perioData=cursor.fetchall()
            for data in perioData:
                self.perioData[formatDate(data[0])]=perio.get_perioData(data[1])             #a dictionary (keys=dates) of dictionaries with keys like "ur8" and containing 7 tuples of data

            try:
                cursor.execute('select drnm,adrtel,curmed,oldmed,allerg,heart,lungs,liver,kidney,bleed,anaes,other from mednotes where serialno=%d'%self.serialno)
                self.MH=cursor.fetchall()
                if self.MH!=():
                    allerg=self.MH[0][4]
                    if len(allerg)>0 and not "med ok" in allerg.lower():
                        self.MEDALERT=True
            except:
                print "patient class - error getting mednotes"


            cursor.execute('select DATE_FORMAT(date,"%s"), trtid, chart from daybook where serialno = %d'%(localsettings.sqlDateFormat,self.serialno))
            self.dayBookHistory=cursor.fetchall()

            cursor.close()
            db.close()

            self.updateChartgrid()
            self.updateFees()
            self.setCurrentEstimate()

    def getEsts(self,cursor=None):
        disconnectNeeded=False
        
        if cursor==None:
            disconnectNeeded=True
            db=connect()
            cursor=db.cursor()
      
        cursor.execute('select  serialno,courseno,dent,esta,acta, estb,actb ,data from prvfees where serialno=%d and courseno=%d'%(self.serialno,self.courseno0))
        self.estimates = cursor.fetchall()
        cursor.execute('select serialno,courseno, dent, ct,data from tsfees where serialno=%d and courseno=%d'%(self.serialno,self.courseno0))
        if disconnectNeeded:
            cursor.close()
            db.close()
        self.tsfees = cursor.fetchall()


    def getCurrtrt(self,cursor=None):
        disconnectNeeded=False
        if cursor==None:
            disconnectNeeded=True
            db=connect()
            cursor=db.cursor()
        fields=currtrtmtTableAtts
        query=""
        for field in fields:
            if field in dateFields:
                query+='DATE_FORMAT(%s,"%s"),'%(field,localsettings.sqlDateFormat)
            else:
                query+=field+","
        query=query.strip(",")
        cursor.execute('select %s from currtrtmt where serialno=%d and courseno=%d'%(query,self.serialno,self.courseno0))               ##todo - I should lever these multiple tx plans!!!!
        values= cursor.fetchall()
        for value in values:
            i=0
            for field in fields:
                self.__dict__[field]=value[i]
                i+=1
        if self.accd!="" and self.accd!=None:
            self.underTreatment=True
        if disconnectNeeded:
            cursor.close()
            db.close()
    def getNotesTuple(self,cursor=None):
        '''this is either called when the class is initiated (when cursor will be an active db cursor) or to refresh the notes.
        in the latter case, a new cursor needs to be initiated here.
        '''
        if cursor==None:
            db=connect()
            cursor=db.cursor()
            cursor.execute("select lineno,line from notes where serialno=%d"%self.serialno)
            self.notestuple = cursor.fetchall()                                                     # so "notes" is a tuple like this ((0,'notes'),(1,"morenotes"),...etc...)
            cursor.close()
            db.close()
        else:
            cursor.execute("select lineno,line from notes where serialno=%d"%self.serialno)
            self.notestuple = cursor.fetchall()                                                     # so "notes" is a tuple like this ((0,'notes'),(1,"morenotes"),...etc...)

    def flipDec_Perm(self,tooth):
        '''switches a deciduous tooth to a permanent one, and viceVersa pass a variable like "ur5" '''
        quadrant=tooth[:2]
        pos=int(tooth[2])-1                 # will be 0-7
        if quadrant=="ul":
            var=self.dent1
            pos=7-pos
        elif quadrant=="ur":
            var=self.dent0
        elif quadrant=="ll":
            var=self.dent2
        else: #lr
            var=self.dent3
            pos=7-pos
        existing=dec_perm.fromSignedByte(var)
        print "original",existing,
        if existing[pos]=="1":
            existing=existing[:pos]+"0"+existing[pos+1:]
        else:
            existing=existing[:pos]+"1"+existing[pos+1:]
        print "new",existing
        if quadrant=="ul":
            self.dent1=dec_perm.toSignedByte(existing)
        elif quadrant=="ur":
            self.dent0=dec_perm.toSignedByte(existing)
        elif quadrant=="ll":
            self.dent2=dec_perm.toSignedByte(existing)
        else: #lr
            self.dent3=dec_perm.toSignedByte(existing)
        self.updateChartgrid()
    def updateChartgrid(self):
        grid=""
        for quad in (self.dent1,self.dent0,self.dent3,self.dent2):
            grid+=dec_perm.fromSignedByte(quad)
        print grid
        for pos in mouth:
            if grid[mouth.index(pos)]=="0":
                self.chartgrid[pos]=pos
            else:
                self.chartgrid[pos]=decidmouth[mouth.index(pos)]

    def updateFees(self):
        self.fees=(self.money0 + self.money1 + self.money9 + self.money10 + self.money11 - self.money2 - self.money3 - self.money8)

    def setCurrentEstimate(self):
        self.currEstimate=estimates.getCurrentEstimate(self.estimates,self.tsfees)


    def addHiddenNote(self,notetype,note=""):
        if notetype=="payment":
            note=chr(3)+chr(119)+note
            self.HIDDENNOTES.append(note)
        if notetype=="printed":
            note=chr(3)+"v"+note
            self.HIDDENNOTES.append(note)
        if notetype=="exam":               #other treatment
            note=chr(3)+chr(112)+note
            self.HIDDENNOTES.append(note)
        if notetype=="treatment":               #other treatment
            note=chr(3)+chr(107)+note
            self.HIDDENNOTES.append(note)

    def clearHiddenNotes(self):
        self.HIDDENNOTES=[]
    def updateBilling(self,tone):
        self.billdate=localsettings.ukToday()
        self.billct+=1
        self.billtype=tone

def formatDate(d):
    ''' takes a date, returns a string'''
    try:
        retarg= "%02d/%02d/%d"%(d.day,d.month,d.year)
    except:
        retarg="no date"
    return retarg


if __name__ =="__main__":
    '''testing stuff'''
    try:
        serialno=int(sys.argv[len(sys.argv)-1])
    except:
        serialno=106
    if "-v" in sys.argv:
        verbose=True
    else:
         verbose=False
    #pt=patient(serialno)
    #print pt.title,pt.fname,pt.sname,pt.dob
    #for line in pt.notestuple:
    #    print str(line)
    #print load_debug(pt,pt)
    #print pt.save()
    #print pt.notestuple

    pt=patient(serialno)
    if False:
      for att in pt.__dict__.keys():
        if pt.__dict__[att]=="":
            print att, "e"
        else:
            print att,pt.__dict__[att]
    #print pt.dent1,pt.dent0,pt.dent3,pt.dent2
    #pt.flipDec_Perm("ur8")
    #print pt.dent1,pt.dent0,pt.dent3,pt.dent2
    print pt.dayBookHistory