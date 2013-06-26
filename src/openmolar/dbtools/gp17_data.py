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

def convert_tooth(tooth):
    '''
    take something like "ul5" and return the iso code
    '''
    print "converting tooth '%s'"% tooth ,
    quadrant = tooth[:2].lower()
    iso_quadrant = ["ur", "ul", "ll", "lr"].index(quadrant)
    try:
        tooth_no = "abcde".index(tooth[2].lower()) + 1
        iso_quadrant += 4
    except ValueError:
        tooth_no = tooth[2]
    
    result = "%s%s"% (iso_quadrant+1, tooth_no)
    print result 
    return result

CAPITATION_SIMPLE = [ 
    "2771", #upper special tray 
  "2772"  #lower special tray
]

CONTINUING_CARE_SIMPLE = [ 
    "0101", # exam a 
    "0111", # exam b
    "0201", # exam c
    "1001", # perio a
    "1011", # perio b
    "2771", #upper special tray 
    "2772"  #lower special tray
]

TOOTH_SPECIFIC_CODES = [
    "0701", #Fissure sealant, unfilled third molars
    "1021", #non-surgical treatment of periodontal disease
    "1131", #crown lengthening
    "1401", #1 surface
    "1402", #2 surface
    "1403", #2 or more surface including MO or DO
    "1404", #3 or more surface including MOD
    "1411", #tunnel
    "1412", #tunnel, max per tooth
    "1421", #resin
    "1420", #2 or more (same tooth)
    "1422", #acid etch - 1 angle
    "1423", #incisal edge
    "1424", #2 agles - mesial and distal
    "1425", #cusp tip
    "1425", #glass ionomer - 1 filling
    "1426", #glass ionomer - 2 or more
]






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
    addr3 = ""
    town = "Inverness"
    county = ""
    pcde = "IV25XQ"
    accd = date(1969,12,9)
    cmpd = date(2015,12,9)
    dnt1 = 1
    dnt2 = None
    #dent0,dent1,dent2,dent3 = 0,0,0,0
    bpe = [""]
    under_capitation = False
    estimates = []
    nhs_claims = []
    
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
        for att in (self.pt.addr2, self.pt.addr3, self.pt.town, self.pt.county):
            att = att.strip(" ")
            if att != "":
                return att 
        
    @property
    def addr3(self):
        for att in (self.pt.addr3, self.pt.town, self.pt.county):
            att = att.strip(" ")
            if att != "" and att != self.addr2:
                return att 
        
        return ""
        
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
        if type(self.pt) == DuckPatient:
            return True
        
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
    def common_codes(self):
        '''
        looks for exams, perio, small xrays and special trays.
        counts these items.
        '''
        if "tx" in self.exclusions:
            return []        
        
        items = {}

        if self.pt.under_capitation:
            allowed_claim_codes = CAPITATION_SIMPLE
        else:
            allowed_claim_codes = CONTINUING_CARE_SIMPLE
                                
        for item in self.pt.nhs_claims:
            if item.itemcode in allowed_claim_codes:
                try:
                    items[item.itemcode] += item.number
                except KeyError:
                    items[item.itemcode] = item.number
        return items
        
    @property
    def simple_codes(self):
        if "tx" in self.exclusions:
            return []        
        
        return []
            
    @property
    def complex_codes(self):
        if "tx" in self.exclusions:
            return []        
        
        if self.testing_mode:
            return test_complex_codes
        else:
            return []
        
    @property
    def tooth_specific_codes(self):
        if "tx" in self.exclusions:
            return []    

        ts_items = {}

        allowed_claim_codes = TOOTH_SPECIFIC_CODES
        for item in self.pt.nhs_claims:
            if item.itemcode in allowed_claim_codes:
                iso_tooth = convert_tooth(item.category)
                try:
                    ts_items[item.itemcode].append(iso_tooth)
                except KeyError:
                    ts_items[item.itemcode] = [iso_tooth]
        return ts_items

        return []    
        
            
if __name__ == "__main__":
    data = Gp17Data(testing_mode=True)
    
