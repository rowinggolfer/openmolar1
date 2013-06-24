#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011, Neil Wallace <rowinggolfer@googlemail.com>               ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

'''
Provides Gp17Data class for the data required by a GP17(Scotland) NHS form
'''

from datetime import date
from openmolar.settings import localsettings
from openmolar.ptModules import dec_perm


test_misc_dict = {
    "on_referral":True,
    "special_needs":True,
    "not_extending":True,
    "radiographs":True,
    "models":True,
    "trauma":True
    }

class DuckCode(object):
    def __init__(self, code, number=1, free_replace= False):
        self.code = code
        self.number = number
        self.free_replace = free_replace
    
test_complex_codes = [
    DuckCode("4401",2),
    DuckCode("3803",1,True)
    ]


class DuckPatient(object):
    sname = "Wallace"
    fname = "Bea"
    dob = date(1969,12,9)
    sex = "F"
    nhsno = "1231234567"
    psn = "Davis"  #previous surname
    addr1 = "The Gables"
    addr2 = "Daviot"
    addr3 = "Inverness"
    pcde = "IV25XQ"
    accd = date(1969,12,9)
    cmpd = date(2015,12,9)
    dnt1 = 1
    dnt2 = None
    dent0,dent1,dent2,dent3 = 0,0,0,0
    bpe = [""]

    
class Gp17Data(object):
    '''
    a class to hold data required by the form
    '''
    
    misc_dict = {}
    
    def __init__(self, pt=None, testing_mode=False):
        
        self.pt = DuckPatient() if pt is None else pt
        self.dentist = self.pt.dnt2 if self.pt.dnt2 != 0 else self.pt.dnt1
        
        self.testing_mode = testing_mode
        if testing_mode:
            self.misc_dict = test_misc_dict

        self.exclusions = []
    
    def format_date(self, date):
        '''
        format's a date of birth to MMDDYYYY
        '''
        try:
            return "%02d%02d%04d"% (
                date.day, 
                date.month, 
                date.year)
        except AttributeError:
            return "        "
        
    @property
    def dob(self):
        '''
        format the patients date of birth to MMDDYYYY
        '''
        return self.format_date(self.pt.dob)
            
    @property
    def stamp_text(self):
        '''
        The Dentist's Information
        '''
        try:
            text = localsettings.dentDict[self.dentist][2]+"\n"
        except KeyError:
            print "Key Error getting dentist",self.dentist
            text = "\n"
        for line in localsettings.practiceAddress:
            text += line+"\n"
        try:
            text += localsettings.dentDict[self.dentist][3]
        except KeyError:
            text += ""
    
        return text
    
    @property
    def addr1(self):
        return self.pt.addr1
    
    @property
    def addr2(self):
        return self.pt.addr2
    
    @property
    def addr3(self):
        return self.pt.addr3
        
    @property
    def pcde(self):
        pcde = self.pt.pcde
        if len(pcde) == 6:
            return "%s %s"% (pcde[:3], pcde[3:])
        return pcde
    
    @property
    def identifier(self):
        '''
        CHI number
        '''
        return str(self.pt.nhsno)
    
    @property
    def previous_sname(self):
        return self.pt.psn
    
    @property
    def accd(self):
        '''
        date of registration/acceptance
        '''
        if "accd" in self.exclusions:
            return ""
        return self.format_date(self.pt.accd)
    
    @property
    def cmpd(self):
        '''
        date of completion
        '''
        if "cmpd" in self.exclusions:
            return ""        
        return self.format_date(self.pt.cmpd)

    @property
    def show_chart(self):
        if "chart" in self.exclusions:
            return False                
        return True
    
    def tooth_present(self, quadrant, tooth):
        '''
        chart - returns True if the tooth is present.
        '''
        
        old_quadrant = ["ur","ul","ll","lr"][(quadrant %4)-1]
        old_notation = "%s%dst"%(old_quadrant, tooth)
        static_string = self.pt.__dict__[old_notation].split(" ")
        
        #print "checking for tooth %s%s (%s), '%s'"% (
        #    quadrant, tooth, old_notation, static_string)
        
        if "TM" in static_string:
            return False
        
        if quadrant > 4:
            if self._is_deciduous(quadrant-4, tooth):
                result = True
            else:
                result = False
        else:
            if self._is_deciduous(quadrant, tooth):
                result = "+P" in static_string
            else:
                result = not "AT" in static_string
                
        return result
        
    def _is_deciduous(self, quadrant, tooth):
        '''
        chart - returns True if the tooth is present.
        '''
        if quadrant == 1:
            att = self.pt.dent0
        elif quadrant == 2:
            att = self.pt.dent1
        elif quadrant == 3:
            att = self.pt.dent2
        elif quadrant == 4:
            att = self.pt.dent3
        else:
            return False    

        array = dec_perm.fromSignedByte(att)
        if quadrant in (2,4):
            array = list(reversed(array))
        return array[tooth-1] == "1"

    @property
    def bpe(self):
        '''
        bpe
        '''
        if "bpe" in self.exclusions:
            return "" 
        try:       
            return self.pt.bpe[-1][1]
        except IndexError:
            return ""
        
    @property
    def simple_codes(self):
        if "tx" in self.exclusions:
            return []        

        if self.testing_mode:
            return ["0101", "0111", "3502"]
        else:
            return []
    
    @property
    def complex_codes(self):
        if "tx" in self.exclusions:
            return []        
        
        if self.testing_mode:
            return test_complex_codes
        else:
            return []
            
if __name__ == "__main__":
    data = Gp17Data(testing_mode=True)
    
