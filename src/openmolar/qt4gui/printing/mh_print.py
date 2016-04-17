#! /usr/bin/python

# ########################################################################### #
# #                                                                         # #
# # Copyright (c) 2009-2016 Neil Wallace <neil@openmolar.com>               # #
# #                                                                         # #
# # This file is part of OpenMolar.                                         # #
# #                                                                         # #
# # OpenMolar is free software: you can redistribute it and/or modify       # #
# # it under the terms of the GNU General Public License as published by    # #
# # the Free Software Foundation, either version 3 of the License, or       # #
# # (at your option) any later version.                                     # #
# #                                                                         # #
# # OpenMolar is distributed in the hope that it will be useful,            # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of          # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           # #
# # GNU General Public License for more details.                            # #
# #                                                                         # #
# # You should have received a copy of the GNU General Public License       # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.      # #
# #                                                                         # #
# ########################################################################### #


from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtPrintSupport
from PyQt5 import QtWidgets

from openmolar.settings import localsettings
from openmolar.dbtools.medhist import get_mh

MARGIN_LEFT = 25
MARGIN_RIGHT = 25
MARGIN_TOP = 20
MARGIN_BOTTOM = 30

# alter this to print rectangles
DEBUG = False


class MHPrint(object):

    '''
    A class to print the MH form for a patient
    '''
    date_ = None
    mh = None

    def __init__(self, pt, parent):
        self.pt = pt
        self.parent = parent
        self.printer = QtPrintSupport.QPrinter()
        self.printer.setPageSize(QtPrintSupport.QPrinter.A4)

        if self.parent.include_mh:
            self.mh = get_mh(self.pt.serialno)

    @property
    def date_text(self):
        '''
        the date to be printed on the form.
        '''
        if not self.date_:
            return localsettings.formatDate(localsettings.currentDay())
        else:
            return localsettings.formatDate(self.date_)

    def print_(self):
        '''
        print the MH form
        '''
        def bold_on(bold=True):
            font = painter.font()
            font.setBold(bold)
            painter.setFont(font)

        def bold_off():
            bold_on(False)

        def italic_on(italic=True):
            font = painter.font()
            font.setItalic(italic)
            painter.setFont(font)

        def italic_off():
            italic_on(False)

        def print_line(y, left=0, colspan=12, dotted=True):
            '''
            print a line
            '''
            bottom_y = y + line_height
            left_point = QtCore.QPointF(
                MARGIN_LEFT +
                left *
                col_width,
                bottom_y)
            right_point = QtCore.QPointF(
                MARGIN_LEFT + (left + colspan) * col_width, bottom_y)
            painter.save()
            if dotted:
                pen = painter.pen()
                pen.setStyle(QtCore.Qt.DotLine)
                painter.setPen(pen)
            painter.drawLine(left_point, right_point)
            painter.restore()

        def print_text(text, y, left=0, colspan=12, rowspan=1,
                       option=QtCore.Qt.AlignLeft):
            '''
            print the text in a box
            '''
            rect = QtCore.QRectF(
                MARGIN_LEFT + left * col_width, y,
                colspan * col_width - 5, line_height * rowspan
            )
            if DEBUG:
                painter.drawRect(rect)
            text_option = QtGui.QTextOption(option | QtCore.Qt.AlignVCenter)
            # text_option.setWrapMode(text_option.NoWrap)
            painter.drawText(rect, text, text_option)
            return line_height * rowspan  # return so that y can be adjusted

        def circle_no(y):
            rect = QtCore.QRectF(
                MARGIN_LEFT + 6.5 * col_width - 3,
                y - 3,
                painter.fontMetrics().width(_("NO")) + 4,
                line_height + 5
            )
            painter.save()
            pen = painter.pen()
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawEllipse(rect)
            painter.restore()

        def circle_yes(y):
            rect = QtCore.QRectF(
                MARGIN_LEFT + 6.5 * col_width - 4 -
                painter.fontMetrics().width(_("YES")),
                y - 3,
                painter.fontMetrics().width(_("YES")) + 3,
                line_height + 5
            )
            painter.save()
            pen = painter.pen()
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawEllipse(rect)
            painter.restore()

        dialog = QtPrintSupport.QPrintDialog(self.printer, self.parent)

        if not dialog.exec_():
            return

        page_width = self.printer.pageRect().width() - (
            MARGIN_LEFT + MARGIN_RIGHT)

        # use a 12 column grid
        col_width = page_width / 12

        painter = QtGui.QPainter(self.printer)
        pen = QtGui.QPen(QtCore.Qt.black)
        pen.setWidth(1)
        painter.setPen(pen)

        font = QtGui.QFont("sans", 14)
        font.setBold(True)
        painter.setFont(font)

        line_height = QtGui.QFontMetrics(painter.font()).height() + 15
        padding = line_height / 6

        y = MARGIN_TOP

        for value in (localsettings.PRACTICE_NAME,
                      _("Confidential Medical History Questionaire")
                      ):
            if not value:
                continue
            y += print_text(value, y, option=QtCore.Qt.AlignCenter)

        print_line(y, dotted=False)

        y += line_height + padding

        painter.setFont(QtGui.QFont("sans", 9))
        line_height = QtGui.QFontMetrics(painter.font()).height()
        padding = line_height / 3

        if self.pt:
            print_text(str(self.pt.serialno), MARGIN_TOP, 11, 1)

        bold_on()

        y += print_text(_("PLEASE CHECK/COMPLETE THESE DETAILS"), y)
        y += padding
        section_bottom = y

        bold_off()

        FIELDS = (_("Date of Birth"), _("Home tel"), _("Work tel"),
                  _("Mobile"), _("Email"), _("Alternate Email"))

        if self.pt:
            VALUES = (localsettings.formatDate(self.pt.dob), self.pt.tel1,
                      self.pt.tel2, self.pt.mobile, self.pt.email1,
                      self.pt.email2)
            for value in (
                    self.pt.name,
                    self.pt.addr1,
                    self.pt.addr2,
                    self.pt.addr3,
                    self.pt.town,
                    self.pt.county,
                    self.pt.pcde):
                if value in (None, ""):
                    continue

                y += print_text(value, y, 0, colspan=5)
        else:
            bold_on()
            print_text(_("Name & Address"), y, 0, colspan=2,
                       option=QtCore.Qt.AlignRight)
            bold_off()
            VALUES = ("",) * len(FIELDS)
            y += 5 * line_height

        address_bottom = y
        y = section_bottom  # move back up to print next rows

        for i, value in enumerate(VALUES):
            field = FIELDS[i]
            if (value in (None, "") and
                    field in (_("Work tel"), _("Alternate Email"))):
                continue

            bold_on()
            print_text(field, y, 5, colspan=2, option=QtCore.Qt.AlignRight)
            bold_off()
            y += print_text(value, y, 7, colspan=5)

        if address_bottom > y:
            y = address_bottom

        y += line_height
        print_line(y, dotted=False)
        y += 2 * line_height

        bold_on()
        print_text(_("Please Circle"), y, 5.5, colspan=2,
                   option=QtCore.Qt.AlignCenter)
        y += print_text(_("If 'YES' - Give Details"), y, 8, colspan=4,
                        option=QtCore.Qt.AlignCenter)

        y += print_text(_("ARE YOU CURRENTLY?"), y, 0, colspan=6)
        y += padding
        bold_off()

        med_comments_y = y + 2 * \
            print_text(_("Taking any prescribed medicines?"), y, 0.5, 5.5)
        print_text(_("Yes"), y, 5.5, colspan=1, option=QtCore.Qt.AlignRight)
        print_text(_("No"), y, 6.5, colspan=1)
        i = 0
        if self.mh and self.mh.medications:
            circle_yes(y)
            italic_on()
            for med in list(self.mh.medications.keys()):
                print_text(med, y, 7, 5, option=QtCore.Qt.AlignCenter)
                print_line(y, 7, 5)
                y += line_height + padding
                i += 1
            italic_off()
        else:
            if self.mh:
                circle_no(y)

        for i in range(i, 5):
            print_line(y, 7, 5)
            y += line_height + padding
        if self.mh and self.mh.medication_comments:
            italic_on()
            print_text(self.mh.medication_comments, med_comments_y, 1, 6, 4)
            italic_off()

        y += line_height
        print_text(_("Carrying a Medical Warning Card?"), y, 0.5, 5.5)
        print_line(y, 7, 5)
        if self.mh and self.mh.warning_card:
            italic_on()
            print_text(self.mh.warning_card.lower(), y, 7, 5,
                       option=QtCore.Qt.AlignCenter)
            italic_off()
            circle_yes(y)
        else:
            if self.mh:
                circle_no(y)
        print_text(_("Yes"), y, 5.5, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 6.5, colspan=1)
        y += padding

        if self.pt is None or (self.pt.sex == "F" and
                               13 < self.pt.ageYears < 55):
            print_text(_("Pregnant or Breast Feeding?"), y, 0.5, 5.5)
            print_line(y, 7, 5)
            print_text(_("Yes"), y, 5.5, colspan=1,
                       option=QtCore.Qt.AlignRight)
            y += print_text(_("No"), y, 6.5, colspan=1)

        y += line_height
        bold_on()
        y += print_text(_("DO YOU SUFFER FROM?"), y, 0, colspan=6)
        y += padding
        bold_off()

        y += print_text(
            _("Allergies to Any Medicines or Substances?"),
            y, 0.5, 5.5)
        print_text(_("eg. Penicillin, aspirin or latex."), y, 2, 4)
        print_line(y, 7, 5)
        if self.mh and self.mh.allergies:
            italic_on()
            print_text(self.mh.allergies.lower(), y, 7, 5,
                       option=QtCore.Qt.AlignCenter)
            italic_off()
            circle_yes(y)
        else:
            if self.mh:
                circle_no(y)
        print_text(_("Yes"), y, 5.5, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 6.5, colspan=1)
        y += padding

        print_text(
            _("Bronchitis, Asthma, other Chest Conditions?"),
            y, 0.5, 5.5)
        print_line(y, 7, 5)
        if self.mh and self.mh.respiratory:
            italic_on()
            print_text(self.mh.respiratory.lower(), y, 7, 5,
                       option=QtCore.Qt.AlignCenter)
            italic_off()
            circle_yes(y)
        else:
            if self.mh:
                circle_no(y)
        print_text(_("Yes"), y, 5.5, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 6.5, colspan=1)
        y += padding

        y += print_text(
            _("Heart Problems, Angina, Blood pressure"),
            y, 0.5, 5.5)
        print_text(_("problems, or a stroke?"), y, 2, 4)
        print_line(y, 7, 5)
        if self.mh and self.mh.heart:
            italic_on()
            print_text(self.mh.heart.lower(), y, 7, 5,
                       option=QtCore.Qt.AlignCenter)
            italic_off()
            circle_yes(y)
        else:
            if self.mh:
                circle_no(y)
        print_text(_("Yes"), y, 5.5, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 6.5, colspan=1)
        y += padding

        print_text(_("Diabetes?"), y, 0.5, 5.5)
        print_line(y, 7, 5)
        if self.mh and self.mh.diabetes:
            italic_on()
            print_text(self.mh.diabetes.lower(), y, 7, 5,
                       option=QtCore.Qt.AlignCenter)
            italic_off()
            circle_yes(y)
        else:
            if self.mh:
                circle_no(y)
        print_text(_("Yes"), y, 5.5, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 6.5, colspan=1)
        y += padding

        print_text(_("Arthritis?"), y, 0.5, 5.5)
        print_line(y, 7, 5)
        if self.mh and self.mh.arthritis:
            italic_on()
            print_text(self.mh.arthritis.lower(), y, 7, 5,
                       option=QtCore.Qt.AlignCenter)
            italic_off()
            circle_yes(y)
        else:
            if self.mh:
                circle_no(y)
        print_text(_("Yes"), y, 5.5, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 6.5, colspan=1)
        y += padding

        y += print_text(
            _("Bruising or persistant bleeding after"),
            y, 0.5, 5.5)
        print_text(_("surgery or tooth extraction?"), y, 2, 4)
        print_line(y, 7, 5)
        if self.mh and self.mh.bleeding:
            italic_on()
            print_text(self.mh.bleeding.lower(), y, 7, 5,
                       option=QtCore.Qt.AlignCenter)
            italic_off()
            circle_yes(y)
        else:
            if self.mh:
                circle_no(y)
        print_text(_("Yes"), y, 5.5, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 6.5, colspan=1)
        y += padding

        y += print_text(_("Any Infectious Diseases"), y, 0.5, 5.5)
        print_text(_("(including HIV and Hepatitis)?"), y, 2, 4)
        print_line(y, 7, 5)
        if self.mh and self.mh.infectious_disease:
            italic_on()
            print_text(self.mh.infectious_disease.lower(), y, 7, 5,
                       option=QtCore.Qt.AlignCenter)
            italic_off()
            circle_yes(y)
        else:
            if self.mh:
                circle_no(y)
        print_text(_("Yes"), y, 5.5, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 6.5, colspan=1)
        y += padding

        y += line_height
        bold_on()
        y += print_text(_("DID YOU, AS A CHILD OR SINCE HAVE"), y, 0,
                        colspan=6)
        y += padding
        bold_off()

        print_text(_("Bacterial Endocarditis?"), y, 0.5, 5.5)
        print_line(y, 7, 5)
        if self.mh and self.mh.endocarditis:
            italic_on()
            print_text(self.mh.endocarditis.lower(), y, 7, 5,
                       option=QtCore.Qt.AlignCenter)
            italic_off()
            circle_yes(y)
        else:
            if self.mh:
                circle_no(y)
        print_text(_("Yes"), y, 5.5, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 6.5, colspan=1)
        y += padding

        print_text(_("Liver Disease (eg. Jaundice or Hepatitis)?"),
                   y, 0.5, 5.5)
        print_line(y, 7, 5)
        if self.mh and self.mh.liver:
            italic_on()
            print_text(self.mh.liver.lower(), y, 7, 5,
                       option=QtCore.Qt.AlignCenter)
            italic_off()
            circle_yes(y)
        else:
            if self.mh:
                circle_no(y)
        print_text(_("Yes"), y, 5.5, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 6.5, colspan=1)
        y += padding

        print_text(_("A bad reaction to a Local or General Anaesthetic?"),
                   y, 0.5, 5.5)
        print_line(y, 7, 5)
        if self.mh and self.mh.anaesthetic:
            italic_on()
            print_text(self.mh.anaesthetic.lower(), y, 7, 5,
                       option=QtCore.Qt.AlignCenter)
            italic_off()
            circle_yes(y)
        else:
            if self.mh:
                circle_no(y)
        print_text(_("Yes"), y, 5.5, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 6.5, colspan=1)
        y += padding

        print_text(_("A joint replacement or other implant?"), y, 0.5, 5.5)
        print_line(y, 7, 5)
        if self.mh and self.mh.joint_replacement:
            italic_on()
            print_text(self.mh.joint_replacement.lower(), y, 7, 5,
                       option=QtCore.Qt.AlignCenter)
            italic_off()
            circle_yes(y)
        else:
            if self.mh:
                circle_no(y)
        print_text(_("Yes"), y, 5.5, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 6.5, colspan=1)
        y += padding

        print_text(_("Heart Surgery?"), y, 0.5, 5.5)
        print_line(y, 7, 5)
        if self.mh and self.mh.heart_surgery:
            italic_on()
            print_text(self.mh.heart_surgery.lower(), y, 7, 5,
                       option=QtCore.Qt.AlignCenter)
            italic_off()
            circle_yes(y)
        else:
            if self.mh:
                circle_no(y)
        print_text(_("Yes"), y, 5.5, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 6.5, colspan=1)
        y += padding

        print_text(_("Brain Surgery?"), y, 0.5, 5.5)
        print_line(y, 7, 5)
        if self.mh and self.mh.brain_surgery:
            italic_on()
            print_text(self.mh.brain_surgery.lower(), y, 7, 5,
                       option=QtCore.Qt.AlignCenter)
            italic_off()
            circle_yes(y)
        else:
            if self.mh:
                circle_no(y)
        print_text(_("Yes"), y, 5.5, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 6.5, colspan=1)
        y += padding

        y += print_text(_("Treatment that required you to be"), y, 0.5, 5.5)
        print_line(y, 7, 5)
        print_text(_("in Hospital?"), y, 2, 4)
        if self.mh and self.mh.hospital:
            italic_on()
            print_text(self.mh.hospital.lower(), y, 7, 5,
                       option=QtCore.Qt.AlignCenter)
            italic_off()
            circle_yes(y)
        else:
            if self.mh:
                circle_no(y)
        print_text(_("Yes"), y, 5.5, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 6.5, colspan=1)
        y += padding

        print_text(
            _("A close relative with Creutzfeldt Jacob Disease?"),
            y, 0.5, 5.5)
        print_line(y, 7, 5)
        if self.mh and self.mh.cjd:
            italic_on()
            print_text(self.mh.cjd.lower(), y, 7, 5,
                       option=QtCore.Qt.AlignCenter)
            italic_off()
            circle_yes(y)
        else:
            if self.mh:
                circle_no(y)
        print_text(_("Yes"), y, 5.5, colspan=1, option=QtCore.Qt.AlignRight)
        y += print_text(_("No"), y, 6.5, colspan=1)
        y += padding

        y += line_height
        print_line(y, dotted=False)

        y += line_height * 2
        bold_on()
        y += print_text(
            _("PLEASE GIVE ANY OTHER DETAILS WHICH YOU THINK "
              "MAY BE RELEVANT TO YOUR DENTIST"), y)
        if self.mh and self.mh.other:
            y += line_height
            bold_off()
            italic_on()
            print_text(self.mh.other.lower(), y, rowspan=4)
            italic_off()
            bold_on()

        y = self.printer.pageRect().height() - MARGIN_BOTTOM

        print_text(_("Patient's Signature"), y, 0, 3)
        print_line(y, 3, 6)

        print_text(self.date_text, y, 10, 2)


if __name__ == "__main__":
    import os
    os.chdir(os.path.expanduser("~"))

    localsettings.initiate()
    app = QtWidgets.QApplication([])
    from openmolar.dbtools.patient_class import patient

    mw = QtWidgets.QWidget()
    mw.include_mh = True
    pt = patient(29833)

    mh_print = MHPrint(pt, mw)
    mh_print.print_()
