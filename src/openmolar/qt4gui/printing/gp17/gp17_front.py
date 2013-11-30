#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011, Neil Wallace <rowinggolfer@googlemail.com>               ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your OPTION) any later version.                                      ##
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
Provides a Class for printing the GP17(Scotland) NHS form
'''
import os

from PyQt4 import QtCore, QtGui

from openmolar.backports.printed_form import PrintedForm
from openmolar.qt4gui.printing.gp17.gp17_config import gp17config

TEXTBOX_WIDTH = 16
TEXTBOX_HEIGHT = 21

CB_WIDTH = 16
CB_HEIGHT = 16


teeth_x = [ 50,92,133,173,216,256,300,342, 394,434,474,516,560,599,640,681]

RECTS = {}

#upper teeth
for i,x in enumerate(teeth_x):
    RECTS["upper%da"% (i+1)] = QtCore.QRectF(x, 355, 32, CB_HEIGHT)
    RECTS["upper%db"% (i+1)] = QtCore.QRectF(x, 382, 32, CB_HEIGHT)
    RECTS["upper%dc"% (i+1)] = QtCore.QRectF(x, 409, 32, CB_HEIGHT)
    RECTS["lower%da"% (i+1)] = QtCore.QRectF(x, 485, 32, CB_HEIGHT)
    RECTS["lower%db"% (i+1)] = QtCore.QRectF(x, 511, 32, CB_HEIGHT)
    RECTS["lower%dc"% (i+1)] = QtCore.QRectF(x, 538, 32, CB_HEIGHT)


#row1
xs = [80, 100, 175, 195, 292, 312, 383, 403, 439, 460, 481, 501, 532, 552, 578, 596]
ys= [594, 627, 661, 694, 727, 760, 794, 828, 860, 894, 927, 961, 994, 1028]

#column 1
RECTS["0101"] = QtCore.QRectF(xs[0], ys[0], CB_WIDTH, CB_HEIGHT)
RECTS["0111"] = QtCore.QRectF(xs[0], ys[1], CB_WIDTH, CB_HEIGHT)
RECTS["0121"] = QtCore.QRectF(xs[0], ys[2], CB_WIDTH, CB_HEIGHT)
#skips a row
RECTS["2730"] = QtCore.QRectF(xs[0], ys[4], CB_WIDTH, CB_HEIGHT)
RECTS["2731"] = QtCore.QRectF(xs[0], ys[5], CB_WIDTH, CB_HEIGHT)
RECTS["2732"] = QtCore.QRectF(xs[0], ys[6], CB_WIDTH, CB_HEIGHT)

RECTS["2733a"] = QtCore.QRectF(xs[0], ys[7], CB_WIDTH, CB_HEIGHT)
RECTS["2733b"] = QtCore.QRectF(xs[1], ys[7], CB_WIDTH, CB_HEIGHT)

RECTS["2735a"] = QtCore.QRectF(xs[0], ys[8], CB_WIDTH, CB_HEIGHT)
RECTS["2735b"] = QtCore.QRectF(xs[1], ys[8], CB_WIDTH, CB_HEIGHT)

RECTS["2801"] = QtCore.QRectF(xs[0], ys[9], CB_WIDTH, CB_HEIGHT)
RECTS["2802"] = QtCore.QRectF(xs[0], ys[10], CB_WIDTH, CB_HEIGHT)
RECTS["2771"] = QtCore.QRectF(xs[0], ys[11], CB_WIDTH, CB_HEIGHT)
RECTS["2772"] = QtCore.QRectF(xs[0], ys[12], CB_WIDTH, CB_HEIGHT)
RECTS["2738"] = QtCore.QRectF(xs[0], ys[13], CB_WIDTH, CB_HEIGHT)


RECTS["0201a"] = QtCore.QRectF(xs[2], ys[0], CB_WIDTH, CB_HEIGHT)
RECTS["0201b"] = QtCore.QRectF(xs[3], ys[0], CB_WIDTH, CB_HEIGHT)

RECTS["0204a"] = QtCore.QRectF(xs[2], ys[1], CB_WIDTH, CB_HEIGHT)
RECTS["0204b"] = QtCore.QRectF(xs[3], ys[1], CB_WIDTH, CB_HEIGHT)

RECTS["0211"] = QtCore.QRectF(xs[2], ys[2], CB_WIDTH, CB_HEIGHT)
RECTS["1700"] = QtCore.QRectF(xs[2], ys[4], CB_WIDTH, CB_HEIGHT)
RECTS["1716a"] = QtCore.QRectF(xs[2], ys[5], CB_WIDTH, CB_HEIGHT)
RECTS["1716b"] = QtCore.QRectF(xs[3], ys[5], CB_WIDTH, CB_HEIGHT)
RECTS["1721a"] = QtCore.QRectF(xs[2], ys[6], CB_WIDTH, CB_HEIGHT)
RECTS["1721b"] = QtCore.QRectF(xs[3], ys[6], CB_WIDTH, CB_HEIGHT)
RECTS["1732a"] = QtCore.QRectF(xs[2], ys[7], CB_WIDTH, CB_HEIGHT)
RECTS["1732b"] = QtCore.QRectF(xs[3], ys[7], CB_WIDTH, CB_HEIGHT)
RECTS["1734a"] = QtCore.QRectF(xs[2], ys[8], CB_WIDTH, CB_HEIGHT)
RECTS["1734b"] = QtCore.QRectF(xs[3], ys[8], CB_WIDTH, CB_HEIGHT)
RECTS["1782a"] = QtCore.QRectF(xs[2], ys[9], CB_WIDTH, CB_HEIGHT)
RECTS["1782b"] = QtCore.QRectF(xs[3], ys[9], CB_WIDTH, CB_HEIGHT)
RECTS["1600"] = QtCore.QRectF(xs[2], ys[11], CB_WIDTH, CB_HEIGHT)
RECTS["1601"] = QtCore.QRectF(xs[2], ys[12], CB_WIDTH, CB_HEIGHT)


RECTS["1001"] = QtCore.QRectF(xs[4], ys[0], CB_WIDTH, CB_HEIGHT)

RECTS["1011"] = QtCore.QRectF(xs[4], ys[1], CB_WIDTH, CB_HEIGHT)

RECTS["1021a"] = QtCore.QRectF(xs[4], ys[2], CB_WIDTH, CB_HEIGHT)
RECTS["1021b"] = QtCore.QRectF(xs[5], ys[2], CB_WIDTH, CB_HEIGHT)

RECTS["1022"] = QtCore.QRectF(xs[4], ys[3], CB_WIDTH, CB_HEIGHT)

RECTS["1501a"] = QtCore.QRectF(xs[4], ys[5], CB_WIDTH, CB_HEIGHT)
RECTS["1501b"] = QtCore.QRectF(xs[5], ys[5], CB_WIDTH, CB_HEIGHT)

RECTS["1502a"] = QtCore.QRectF(xs[4], ys[6], CB_WIDTH, CB_HEIGHT)

RECTS["1503a"] = QtCore.QRectF(xs[4], ys[7], CB_WIDTH, CB_HEIGHT)

RECTS["1504a"] = QtCore.QRectF(xs[4], ys[8], CB_WIDTH, CB_HEIGHT)
RECTS["1504b"] = QtCore.QRectF(xs[5], ys[8], CB_WIDTH, CB_HEIGHT)

RECTS["3611a"] = QtCore.QRectF(xs[4], ys[10], CB_WIDTH, CB_HEIGHT)
RECTS["3611b"] = QtCore.QRectF(xs[5], ys[10], CB_WIDTH, CB_HEIGHT)

RECTS["3631"] = QtCore.QRectF(xs[4], ys[11], CB_WIDTH, CB_HEIGHT)

RECTS["3701"] = QtCore.QRectF(xs[4], ys[12], CB_WIDTH, CB_HEIGHT)

RECTS["1401a"] = QtCore.QRectF(xs[6], ys[0], CB_WIDTH, CB_HEIGHT)
RECTS["1401b"] = QtCore.QRectF(xs[7], ys[0], CB_WIDTH, CB_HEIGHT)

RECTS["1402a"] = QtCore.QRectF(xs[6], ys[1], CB_WIDTH, CB_HEIGHT)
RECTS["1402b"] = QtCore.QRectF(xs[7], ys[1], CB_WIDTH, CB_HEIGHT)

RECTS["1403a"] = QtCore.QRectF(xs[6], ys[2], CB_WIDTH, CB_HEIGHT)
RECTS["1403b"] = QtCore.QRectF(xs[7], ys[2], CB_WIDTH, CB_HEIGHT)

RECTS["1404a"] = QtCore.QRectF(xs[6], ys[3], CB_WIDTH, CB_HEIGHT)
RECTS["1404b"] = QtCore.QRectF(xs[7], ys[3], CB_WIDTH, CB_HEIGHT)

RECTS["1421a"] = QtCore.QRectF(xs[6], ys[4], CB_WIDTH, CB_HEIGHT)
RECTS["1421b"] = QtCore.QRectF(xs[7], ys[4], CB_WIDTH, CB_HEIGHT)

RECTS["1420a"] = QtCore.QRectF(xs[6], ys[5], CB_WIDTH, CB_HEIGHT)
RECTS["1420b"] = QtCore.QRectF(xs[7], ys[5], CB_WIDTH, CB_HEIGHT)

RECTS["1422a"] = QtCore.QRectF(xs[6], ys[6], CB_WIDTH, CB_HEIGHT)
RECTS["1422b"] = QtCore.QRectF(xs[7], ys[6], CB_WIDTH, CB_HEIGHT)

RECTS["1423a"] = QtCore.QRectF(xs[6], ys[7], CB_WIDTH, CB_HEIGHT)
RECTS["1423b"] = QtCore.QRectF(xs[7], ys[7], CB_WIDTH, CB_HEIGHT)

RECTS["1426a"] = QtCore.QRectF(xs[6], ys[8], CB_WIDTH, CB_HEIGHT)
RECTS["1426b"] = QtCore.QRectF(xs[7], ys[8], CB_WIDTH, CB_HEIGHT)

RECTS["1431a"] = QtCore.QRectF(xs[6], ys[9], CB_WIDTH, CB_HEIGHT)
RECTS["1431b"] = QtCore.QRectF(xs[7], ys[9], CB_WIDTH, CB_HEIGHT)

RECTS["2101a"] = QtCore.QRectF(xs[6], ys[11], CB_WIDTH, CB_HEIGHT)
RECTS["2101b"] = QtCore.QRectF(xs[7], ys[11], CB_WIDTH, CB_HEIGHT)

RECTS["2121a"] = QtCore.QRectF(xs[6], ys[12], CB_WIDTH, CB_HEIGHT)
RECTS["2121b"] = QtCore.QRectF(xs[7], ys[12], CB_WIDTH, CB_HEIGHT)



RECTS["4401a"] = QtCore.QRectF(xs[10], ys[0], CB_WIDTH, CB_HEIGHT)
RECTS["4401b"] = QtCore.QRectF(xs[11], ys[0], CB_WIDTH, CB_HEIGHT)

RECTS["4402a"] = QtCore.QRectF(xs[10], ys[1], CB_WIDTH, CB_HEIGHT)
RECTS["4402b"] = QtCore.QRectF(xs[11], ys[1], CB_WIDTH, CB_HEIGHT)

RECTS["4403a"] = QtCore.QRectF(xs[14], ys[0], CB_WIDTH, CB_HEIGHT)
RECTS["4403b"] = QtCore.QRectF(xs[15], ys[0], CB_WIDTH, CB_HEIGHT)

RECTS["4404a"] = QtCore.QRectF(xs[14], ys[1], CB_WIDTH, CB_HEIGHT)
RECTS["4404b"] = QtCore.QRectF(xs[15], ys[1], CB_WIDTH, CB_HEIGHT)


#dentists use only
RECTS["DENTIST_USE_pound"] = QtCore.QRectF(634, ys[0], 48, 410)
RECTS["DENTIST_USE_pence"] = QtCore.QRectF(688, ys[0], 30, 410)

for i in range(1,10):
    RECTS["other%dA"% i] = QtCore.QRectF(
        xs[8], ys[2+i], CB_WIDTH, CB_HEIGHT)
    RECTS["other%dB"% i] = QtCore.QRectF(
        xs[9], ys[2+i], CB_WIDTH, CB_HEIGHT)
    RECTS["other%dC"% i] = QtCore.QRectF(
        xs[10], ys[2+i], CB_WIDTH, CB_HEIGHT)
    RECTS["other%dD"% i] = QtCore.QRectF(
        xs[11], ys[2+i], CB_WIDTH, CB_HEIGHT)
    RECTS["other%da"% i] = QtCore.QRectF(
        xs[12], ys[2+i], CB_WIDTH, CB_HEIGHT)
    RECTS["other%db"% i] = QtCore.QRectF(
        xs[13], ys[2+i], CB_WIDTH, CB_HEIGHT)
    RECTS["free_replace%d"% i] = QtCore.QRectF(
        xs[15], ys[2+i], CB_WIDTH, CB_HEIGHT)


RECTS["4600a"] = QtCore.QRectF(xs[14], ys[12], CB_WIDTH, CB_HEIGHT)
RECTS["4600b"] = QtCore.QRectF(xs[15], ys[12], CB_WIDTH, CB_HEIGHT)

RECTS["radiographs"] = QtCore.QRectF(229, ys[13], CB_WIDTH, CB_HEIGHT)
RECTS["models"] = QtCore.QRectF(359, ys[13], CB_WIDTH, CB_HEIGHT)
RECTS["trauma"] = QtCore.QRectF(460, ys[13], CB_WIDTH, CB_HEIGHT)

RECTS["TOTAL1"] = QtCore.QRectF(602, ys[13], CB_WIDTH, CB_HEIGHT)
RECTS["TOTAL2"] = QtCore.QRectF(622, ys[13], CB_WIDTH, CB_HEIGHT)
RECTS["TOTAL3"] = QtCore.QRectF(642, ys[13], CB_WIDTH, CB_HEIGHT)
RECTS["TOTAL4"] = QtCore.QRectF(662, ys[13], CB_WIDTH, CB_HEIGHT)
RECTS["TOTAL5"] = QtCore.QRectF(684, ys[13], CB_WIDTH, CB_HEIGHT)
RECTS["TOTAL6"] = QtCore.QRectF(702, ys[13], CB_WIDTH, CB_HEIGHT)

##sname boxes
PADDING = 3.1
for i in range(14):
    x = 94 + i * (TEXTBOX_WIDTH + PADDING)
    y = 28
    RECTS["surname_%02d"% i] = QtCore.QRectF(x,y,TEXTBOX_WIDTH,TEXTBOX_HEIGHT)

##fname boxes
for i in range(14):
    x = 94 + i * (TEXTBOX_WIDTH + PADDING)
    y = 60
    RECTS["forename_%02d"% i] = QtCore.QRectF(x,y,TEXTBOX_WIDTH,TEXTBOX_HEIGHT)

##dob
for i, x in enumerate([66,85,123,142,180,199,217,236]):
    RECTS["dob_%d"% i] = QtCore.QRectF(x, 93 ,TEXTBOX_WIDTH,TEXTBOX_HEIGHT)

##sex
RECTS["male"] = QtCore.QRectF(304, 93, TEXTBOX_WIDTH, TEXTBOX_HEIGHT)
RECTS["female"] = QtCore.QRectF(341, 93, TEXTBOX_WIDTH, TEXTBOX_HEIGHT)

## patient identifier
for i, x in enumerate([133,152,171,198,217,236,255,274,293,312]):
    RECTS["pid_%d"% i] = QtCore.QRectF(x, 124 ,TEXTBOX_WIDTH,TEXTBOX_HEIGHT)

## previous sname
for i, x in enumerate([133,152,171,190,209,228,247,266,286,305,324,343]):
    RECTS["psn_%d"% i] = QtCore.QRectF(x, 157 ,TEXTBOX_WIDTH,TEXTBOX_HEIGHT)

##dentists stamp box
RECTS["stampbox"] = QtCore.QRectF(426, 42, 292, 132)

##address
for i, x in enumerate(range(16, 340, 19)):
    RECTS["addr1_%02d"% i] = QtCore.QRectF(x, 216, TEXTBOX_WIDTH, TEXTBOX_HEIGHT)
    RECTS["addr2_%02d"% i] = QtCore.QRectF(x, 244, TEXTBOX_WIDTH, TEXTBOX_HEIGHT)
    RECTS["addr3_%02d"% i] = QtCore.QRectF(x, 272, TEXTBOX_WIDTH, TEXTBOX_HEIGHT)

##postcode
for i, x in enumerate((92,111,130,149,187,206,225)):
    RECTS["pcde_%d"% i] = QtCore.QRectF(x, 304, TEXTBOX_WIDTH, TEXTBOX_HEIGHT)

##accept date and completiondate
for i, x in enumerate((540,560,591,609,640,659,678,697)):
    RECTS["accd_%d"% i] = QtCore.QRectF(x, 185, TEXTBOX_WIDTH, TEXTBOX_HEIGHT)
    RECTS["cmpd_%d"% i] = QtCore.QRectF(x, 219, TEXTBOX_WIDTH, TEXTBOX_HEIGHT)

##treatmentonReferral/specialNeeds/registration
RECTS["on_referral"] = QtCore.QRectF(697, 260, CB_WIDTH, CB_HEIGHT)
RECTS["special_needs"] = QtCore.QRectF(697, 290, CB_WIDTH, CB_HEIGHT)
RECTS["not_extending"] = QtCore.QRectF(697, 316, CB_WIDTH, CB_HEIGHT)

OPTION = QtGui.QTextOption(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)

class GP17Front(PrintedForm):
    '''
    a class to set up and print a GP17
    '''
    NAME = "OLD GP17 Front"
    data = None

    def __init__(self):
        PrintedForm.__init__(self)
        self.row = 1
        self.rects = RECTS

    @classmethod
    def is_active(self):
        if "neil" in os.path.expanduser("~"):
            return False
        return QtCore.QDate.currentDate() < QtCore.QDate(2013,7,1)

    def set_data(self, data):
        self.data = data

    def print_(self):
        self.set_offset(gp17config.OFFSET_LEFT, gp17config.OFFSET_TOP)
        self.set_scaling(gp17config.SCALE_X, gp17config.SCALE_Y)

        painter = PrintedForm.print_(self)
        self._fill(painter)

    def _fill(self, painter):
        if self.data is None:
            return

        serifFont = QtGui.QFont("Courier", 12)
        serifFont.setBold(True)
        fm=QtGui.QFontMetrics(serifFont)
        serifLineHeight = fm.height()

        painter.setPen(QtGui.QPen(QtCore.Qt.black,1))
        painter.setFont(serifFont)

        for func_ in (
            self._fill_surname,
            self._fill_forename,
            self._fill_dob,
            self._fill_sex,
            self._fill_pid,
            self._fill_accd,
            self._fill_cmpd,
            self._fill_misc_cbs,
            self._fill_stampbox,
            self._fill_previous_surname,
            self._fill_address,
            self._fill_simple_codes,
            self._fill_complex_codes
            ):

            painter.save()
            #painter.translate(self.off_set)
            func_(painter)
            painter.restore()

    def _fill_surname(self, painter):
        for i in range(14):
            rect = self.rects["surname_%02d"% i]
            try:
                painter.drawText(rect, self.data.pt.sname[i], OPTION)
            except IndexError:
                break

    def _fill_forename(self, painter):
        for i in range(14):
            rect = self.rects["forename_%02d"% i]
            try:
                painter.drawText(rect, self.data.pt.fname[i], OPTION)
            except IndexError:
                break

    def _fill_dob(self, painter):
        for i in range(8):
            rect = self.rects["dob_%d"% i]
            try:
                painter.drawText(rect, self.data.dob[i], OPTION)
            except IndexError:
                break

    def _fill_sex(self, painter):
        sex = self.data.pt.sex
        if sex=="M":
            painter.drawText(self.rects["male"], "M", OPTION)
        elif sex=="F":
            painter.drawText(self.rects["female"],"F", OPTION)
        else:
            print "UNKNOWN SEX for GP17!"

    def _fill_pid(self, painter):
        for i in range(10):
            rect = self.rects["pid_%d"% i]
            try:
                painter.drawText(rect, self.data.identifier[i], OPTION)
            except IndexError:
                break

    def _fill_previous_surname(self, painter):
        for i in range(10):
            rect = self.rects["psn_%d"% i]
            try:
                painter.drawText(rect, self.data.previous_sname[i], OPTION)
            except IndexError:
                break

    def _fill_stampbox(self, painter):
        painter.drawText(self.rects["stampbox"], self.data.stamp_text)

    def _fill_address(self, painter):
        for i in range(18):
            rect = self.rects["addr1_%02d"% i]
            try:
                painter.drawText(rect, self.data.addr1[i], OPTION)
            except IndexError:
                break

        for i in range(18):
            rect = self.rects["addr2_%02d"% i]
            try:
                painter.drawText(rect, self.data.addr2[i], OPTION)
            except IndexError:
                break

        for i in range(18):
            rect = self.rects["addr3_%02d"% i]
            try:
                painter.drawText(rect, self.data.addr3[i], OPTION)
            except IndexError:
                break

        for i in range(7):
            rect = self.rects["pcde_%d"% i]
            try:
                painter.drawText(rect, self.data.pcde[i], OPTION)
            except IndexError:
                break

    def _fill_accd(self, painter):
        for i in range(8):
            rect = self.rects["accd_%d"% i]
            try:
                painter.drawText(rect, self.data.accd[i], OPTION)
            except IndexError:
                break

    def _fill_cmpd(self, painter):
        for i in range(8):
            rect = self.rects["cmpd_%d"% i]
            try:
                painter.drawText(rect, self.data.cmpd[i], OPTION)
            except IndexError:
                break

    def _fill_misc_cbs(self, painter):
        for key in ["on_referral", "not_extending", "special_needs","on_referral",
                    "radiographs","models","trauma"]:
            if self.data.misc_dict.get(key, False):
                rect = self.rects[key]
                painter.drawText(rect, "X", OPTION)

    def _fill_simple_codes(self, painter):
        self.row = 1
        def other_treatment():

            painter.drawText(self.rects["other%dA"% self.row], code[0], OPTION)
            painter.drawText(self.rects["other%dB"% self.row], code[1], OPTION)
            painter.drawText(self.rects["other%dC"% self.row], code[2], OPTION)
            painter.drawText(self.rects["other%dD"% self.row], code[3], OPTION)
            painter.drawText(self.rects["other%da"% self.row], "0", OPTION)
            painter.drawText(self.rects["other%db"% self.row], "1", OPTION)
            self.row += 1

        for code in self.data.simple_codes:
            try:
                painter.drawText(self.rects[code], "X", OPTION)
            except KeyError:
                other_treatment()

    def _fill_complex_codes(self, painter):
        def other_treatment():

            painter.drawText(self.rects["other%dA"% self.row], code.code[0], OPTION)
            painter.drawText(self.rects["other%dB"% self.row], code.code[1], OPTION)
            painter.drawText(self.rects["other%dC"% self.row], code.code[2], OPTION)
            painter.drawText(self.rects["other%dD"% self.row], code.code[3], OPTION)
            n = "%02d"% code.number
            painter.drawText(self.rects["other%da"% self.row], n[0], OPTION)
            painter.drawText(self.rects["other%db"% self.row], n[1], OPTION)

            if code.free_replace:
                painter.drawText(self.rects["free_replace%d"% self.row], "X", OPTION)
            self.row += 1

        for code in self.data.complex_codes:
            if code.free_replace:
                other_treatment()
                continue
            try:
                n = "%02d"% code.number
                painter.drawText(self.rects["%sa"% code.code], n[0], OPTION)
                painter.drawText(self.rects["%sb"% code.code], n[1], OPTION)
            except KeyError:
                other_treatment()


if __name__ == "__main__":
    os.chdir(os.path.expanduser("~")) # for print to file
    from openmolar.settings import localsettings
    from openmolar.qt4gui.printing.gp17.gp17_data import Gp17Data

    data = Gp17Data(testing_mode=True)
    TEST_IMAGE = os.path.join(localsettings.resources_location, "gp17",
        "front.jpg")

    data = Gp17Data(testing_mode=True)

    app = QtGui.QApplication([])
    form = GP17Front()

    form.set_data(data)

    form.testing_mode = True

    form.print_background = True
    form.BACKGROUND_IMAGE = TEST_IMAGE

    form.controlled_print()

    #for key in sorted(form.rects.keys()):
    #    print key,

