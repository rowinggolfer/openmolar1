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

import copy
from gettext import gettext as _
import logging
import re
import sys

from openmolar.settings import localsettings

LOGGER = logging.getLogger("openmolar")


class TXHash(object):

    def __init__(self, hash_, completed=False):
        self.hash = hash_
        self.completed = completed

    def __hash__(self):
        '''
        new for python3 as the presence of the __eq__ method renders these
        instances unhashable.
        '''
        return object.__hash__(self)

    def __eq__(self, other):
        '''
        compare the object with another hash
        note - completion state is irrelevant
        '''
        if isinstance(other, TXHash):
            return self.hash == other.hash
        return self.hash == other

    def __repr__(self):
        return "TXHash %s completed=%s" % (self.hash, self.completed)


class Estimate(object):

    '''
    this class has attributes suitable for storing in the estimates table
    '''
    COMPLETED = 2
    PARTIALLY_COMPLETED = 1
    PLANNED = 0

    def __init__(self):
        self.ix = None
        self.serialno = None
        self.courseno = None
        self.number = 1
        self.itemcode = "-----"
        self.description = None
        self.fee = None
        self.ptfee = None
        self.feescale = None
        self.csetype = None
        self.dent = None

        self.tx_hashes = []

    @property
    def completed(self):
        '''
        returns a tri-state value.
        0 = nothing completed
        1 = some treatments completed
        2 = all related treatments completed
        '''
        if self.n_completed == len(self.tx_hashes):
            return 2
        if self.n_completed == 0:
            return 0
        return 1

    @property
    def n_completed(self):
        n_completed = 0
        for tx_hash in self.tx_hashes:
            if tx_hash.completed:
                n_completed += 1
        return n_completed

    @property
    def interim_fee(self):
        if self.tx_hashes == []:
            return 0
        return self.n_completed * self.fee // len(self.tx_hashes)

    @property
    def interim_pt_fee(self):
        if self.tx_hashes == []:
            return 0
        return self.n_completed * self.ptfee // len(self.tx_hashes)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "Estimate (%s %s %s %s %s %s %s %s %s %s %s %s)" % (
            self.ix,
            self.serialno,
            self.courseno,
            self.number,
            self.fee,
            self.ptfee,
            self.dent,
            self.itemcode,
            self.description,
            self.csetype,
            self.feescale,
            self.tx_hashes)

    @property
    def log_text(self):
        '''
        estimate data formatted so as to be useful in a log
        || can be used to separate values
        '''
        return "%s || %s || %s || %s || %s || %s || %s || %s||\n" % (
            self.number, self.itemcode, self.description, self.csetype,
            self.feescale, self.dent, self.fee, self.ptfee)

    def __hash__(self):
        '''
        new for python3 as the presence of the __eq__ method renders these
        instances unhashable.
        '''
        return object.__hash__(self)

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)

    def __lt__(self, other):
        try:
            return (self.itemcode.replace("-", "Z") <
                    other.itemcode.replace("-", "Z"))
        except AttributeError:
            return False

    def __gt__(self, other):
        try:
            return (self.itemcode.replace("-", "Z") >
                    other.itemcode.replace("-", "Z"))
        except AttributeError:
            return False

    def toHtmlRow(self):
        hash_string = ""
        for tx_hash in self.tx_hashes:
            hash_string += "<li>%s</li>" % tx_hash.hash
        if hash_string:
            hash_string = "<ul>%s</ul>" % hash_string
        else:
            hash_string = _("no treatments")

        if self.completed == 2:
            completed = _("Yes")
        elif self.completed == 1:
            completed = _("Partially")
        else:
            completed = _("No")
        return '''
            <tr>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
                <td>%s</td>
            </tr>
            ''' % (localsettings.ops.get(self.dent),
                   self.number,
                   self.itemcode,
                   self.description,
                   localsettings.formatMoney(self.fee),
                   localsettings.formatMoney(self.ptfee),
                   self.feescale,
                   self.csetype,
                   completed,
                   hash_string)

    def htmlHeader(self):
        color_string = ' bgcolor="#ffff99"'
        sub_values = (color_string, _("Estimates for Course Number"),
                      self.courseno) + (color_string,) * 10
        return '''
        <tr>
        <th%s colspan="10">%s %s <!--editlink--></th>
        </tr>
        <tr>
        <th%s>Dentist</th>
        <th%s>number</th>
        <th%s>code</th>
        <th%s>Description</th>
        <th%s>fee</th>
        <th%s>pt fee</th>
        <th%s>feescale</th>
        <th%s>cset</th>
        <th%s>completed</th>
        <th%s>Hashes</th>
        </tr>''' % sub_values

    def filteredDescription(self):
        '''
        removes {1 of 3} from the description
        '''
        retarg = copy.copy(self.description)
        gunks = re.findall(" {.*}", retarg)
        for gunk in gunks:
            retarg = retarg.replace(gunk, "")
        return retarg

    @property
    def is_exam(self):
        '''
        important that feescales use an itemcode that matches this!
        examples are 0101, 0111, 0121
        can also be prepended with a single character eg E0101
        '''
        try:
            return bool(re.match(".?01[012]1$", self.itemcode))
        except TypeError:
            return False

    @property
    def is_custom(self):
        return self.itemcode == "CUSTO"

    @property
    def has_one_tx(self):
        return len(self.tx_hashes) == 1

    @property
    def has_multi_txs(self):
        return len(self.tx_hashes) > 1


def strip_curlies(description):
    '''
    comments such as {2 of 2} are present in the estimates...
    this removes such stuff
    '''
    if re.search("{.*}", description):
        return description[:description.index("{")]
    else:
        return description


def sorted_estimates(ests):
    '''
    compresses a list of estimates down into number*itemcode
    '''
    def combineEsts(est):
        for se in combined_estimates:
            if se.itemcode == est.itemcode:
                if se.description == strip_curlies(est.description):
                    # don't combine items where description has changed
                    if est.number is not None and se.number is not None:
                        se.number += est.number
                    se.fee += est.fee
                    se.ptfee += est.ptfee
                    return True
    combined_estimates = []
    for est in ests:
        if not combineEsts(est):
            ce = copy.copy(est)
            ce.description = strip_curlies(ce.description)
            combined_estimates.append(ce)

    return sorted(combined_estimates)


def apply_exemption(pt, maxCharge=0):
    '''
    apply an exemption
    '''
    total = 0
    for est in pt.estimates:
        if "N" not in est.csetype:
            continue
        if maxCharge - total >= est.ptfee:
            pass
        else:
            if maxCharge - total > 0:
                est.ptfee = maxCharge - total
            else:
                est.ptfee = 0
        total += est.ptfee

    return True


if __name__ == "__main__":
    from openmolar.dbtools import patient_class
    localsettings.initiate()
    try:
        serialno = int(sys.argv[len(sys.argv) - 1])
    except:
        serialno = 23664

    pt = patient_class.patient(serialno)
    print("RAW")
    print(str(pt.estimates))
    print("HTML")
    for estimate in pt.estimates:
        print(estimate.toHtmlRow())
    print("SORTED")
    for estimate in sorted_estimates(pt.estimates):
        print(estimate.toHtmlRow())
