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

from collections import namedtuple
from collections import OrderedDict
from gettext import gettext as _
import datetime
import logging
import re
from xml.dom import minidom

from openmolar.settings import localsettings
from openmolar.dbtools.feescales import feescale_handler

LOGGER = logging.getLogger("openmolar")


def isParseable(data):
    '''
    takes a string, tries to parse it.
    '''
    try:
        d = minidom.parseString(data)
        d.toxml()
        d.unlink
    except Exception as exc:
        return (False, str(exc))
    return (True, "")


def getListFromNode(node, id):
    '''
    get the text data from the first child of any such nodes
    '''
    nlist = node.getElementsByTagName(id)
    values = []
    for n in nlist:
        children = n.childNodes
        for child in children:
            values.append(child.data.strip())
    return values


def getTextFromNode(node, id):
    '''
    get the text data from the first child of any such nodes
    '''
    nlist = node.getElementsByTagName(id)
    text = ""
    for n in nlist:
        children = n.childNodes
        for child in children:
            text += child.data.strip()
    return text


def getBoolFromNode(node, id, default=False):
    '''
    get the text data from the first child of any such nodes
    '''
    if default:
        return not getTextFromNode(node, id) in ("False", "0")
    else:
        return getTextFromNode(node, id) in ("True", "1")


def _stripped(xml_string):
        return xml_string.replace("&gt;", ">").replace("&lt;", "<")


class FeeTables(object):

    '''
    a wrapper class to contain as many fee tables as the user has outlined.
    '''

    def __init__(self):
        self.tables = OrderedDict()
        self.warnings = []
        self._ui_crown_chart_buttons = None
        self._ui_post_chart_buttons = None
        self._ui_implant_chart_buttons = None
        self._ui_fs_chart_buttons = None
        self._ui_endo_chart_buttons = None
        self._ui_surgical_chart_buttons = None

        self.getTables()
        self.loadTables()
        if not self.default_table:
            self.warnings.append("No Feetables Found")
        else:
            LOGGER.info("Default FeeTable = %s" % self.default_table)

    @property
    def default_csetype(self):
        try:
            return self.default_table.categories[0]
        except AttributeError:
            return ""

    @property
    def csetypes(self):
        csetypes = []
        for table in list(self.tables.values()):
            for cset in table.categories:
                if cset not in csetypes:
                    csetypes.append(cset)
        return csetypes

    @property
    def default_table(self):
        try:
            return list(self.tables.values())[0]
        except IndexError:
            return None

    def get_all_buts(self, att):
        unique_shortcuts = set([])
        types_ = []
        for table in list(self.tables.values()):
            for button in table.ui_lists.get(att, []):
                if button.shortcut not in unique_shortcuts:
                    types_.append(button)
                unique_shortcuts.add(button.shortcut)
        return sorted(types_, key=lambda x: x.ix)

    @property
    def ui_fs_chart_buttons(self):
        if self._ui_fs_chart_buttons is None:
            self._ui_fs_chart_buttons = self.get_all_buts("fs_buttons")
        return self._ui_fs_chart_buttons

    @property
    def ui_crown_chart_buttons(self):
        '''
        A list of unique crown types from all tables.
        '''
        if self._ui_crown_chart_buttons is None:
            self._ui_crown_chart_buttons = self.get_all_buts("crown_buttons")
        return self._ui_crown_chart_buttons

    @property
    def ui_post_chart_buttons(self):
        '''
        A list of unique post types from all tables.
        '''
        if self._ui_post_chart_buttons is None:
            self._ui_post_chart_buttons = self.get_all_buts("post_buttons")
        return self._ui_post_chart_buttons

    @property
    def ui_implant_chart_buttons(self):
        '''
        A list of unique implant types from all tables.
        '''
        if self._ui_implant_chart_buttons is None:
            self._ui_implant_chart_buttons = \
                self.get_all_buts("implant_buttons")
        return self._ui_implant_chart_buttons

    @property
    def ui_endo_chart_buttons(self):
        '''
        A list of unique implant types from all tables.
        '''
        if self._ui_endo_chart_buttons is None:
            self._ui_endo_chart_buttons = \
                self.get_all_buts("endo_buttons")
        return self._ui_endo_chart_buttons

    @property
    def ui_surgical_chart_buttons(self):
        '''
        A list of unique implant types from all tables.
        '''
        if self._ui_surgical_chart_buttons is None:
            self._ui_surgical_chart_buttons = \
                self.get_all_buts("surgical_buttons")
        return self._ui_surgical_chart_buttons

    def __repr__(self):
        '''
        a readable description of the object
        '''
        retarg = "%d Tables \n" % len(self.tables)
        for key in self.tables:
            table = self.tables[key]
            retarg += "===" * 12 + "\n"
            retarg += "   table %s - %s\n" % (key, table.briefName)
            retarg += "%s \n" % table.description
            retarg += "valid %s - %s\n" % (
                localsettings.formatDate(table.startDate),
                localsettings.formatDate(table.endDate))

            retarg += "       categories %s\n" % table.categories
            retarg += "       fee cols %s\n" % str(table.feeColNames)
            retarg += "    pt_fee cols %s\n" % str(table.pt_feeColNames)
            retarg += "       query %s\n" % table.columnQuery
            retarg += "===" * 12 + "\n"
        return retarg

    def getTables(self):
        '''
        get the key to our tables
        '''
        rows = feescale_handler.get_feescales_from_database()
        for i, (ix, xml_data) in enumerate(rows):
            ft = FeeTable(ix, xml_data)
            ft.index = i
            self.tables[i] = ft

    def loadTables(self):
        '''
        iterate through the child tables, and get them loaded
        '''
        for table in list(self.tables.values()):
            try:
                table.load_from_xml()
            except Exception as exc:
                message = "%s %s %s" % (
                    _("feesscale"),
                    table.database_ix,
                    _("Failed to Load")
                )

                LOGGER.exception(message)
                self.warnings.append(message + "<hr /><pre>%s</pre>" % exc)

    @property
    def all_other_shortcuts(self):
        for table in list(self.tables.values()):
            if table.is_current:
                for shortcut in table.other_shortcuts:
                    yield table, shortcut


class FeeTable(object):

    '''
    a class to contain and allow quick access to data stored in a fee table
    '''

    def __init__(self, ix, xml_data):
        LOGGER.info("initiating Feetable %s" % ix)
        self.database_ix = ix
        self.dom = minidom.parseString(xml_data)

        self.setCategories()
        self.setTableDescription()
        self.setStartDate()
        self.setEndDate()
        self.setSectionHeaders()

        self.feesDict = {}

        self.complex_shortcuts = []
        self.treatmentCodes = OrderedDict()
        self.chartPlainCodes = OrderedDict()
        self.chartRegexCodes = OrderedDict()
        self.otherRegexCodes = OrderedDict()
        self.item_modifiers = []

        self.ui_lists = {
            "crown_buttons": [],
            "implant_buttons": [],
            "fs_buttons": [],
            "endo_buttons": [],
            "surgical_buttons": [],
            "post_buttons": [],
        }

    def __repr__(self):
        '''
        a readable description of the object
        '''
        return "FeeTable %s database index %s - has %s feeItems" % (
            self.briefName, self.database_ix, len(self.feesDict))

    def __hash__(self):
        '''
        new for python3 as the presence of the __eq__ method renders these
        instances unhashable.
        '''
        return object.__hash__(self)

    def __eq__(self, other):
        return self.database_ix == other.database_ix

    @property
    def briefName(self):
        return self.description

    @property
    def hasPtCols(self):
        for fee_item in list(self.feesDict.values()):
            if fee_item.has_pt_fees:
                return True
        return False

    @property
    def feeColCount(self):
        if self.hasPtCols:
            return 2
        return 1

    def setCategories(self):
        '''
        the categories will be a list like "P", "PB" etc...
        '''
        LOGGER.debug("loading categories")
        self.categories = []
        for node in self.dom.getElementsByTagName("category"):
            try:
                text = node.firstChild.data.strip(" \n")
                self.categories.append(text)
            except AttributeError:  # no categories
                pass
        LOGGER.debug("categories = %s" % str(self.categories))

    def setSectionHeaders(self):
        '''
        Headers are used when displaying feescale in a treeview
        '''
        LOGGER.debug("loading section headers")
        self.headers = {}
        for node in self.dom.getElementsByTagName("header"):
            id = node.getAttribute("id")
            text = node.childNodes[0].data.strip(" \n")
            self.headers[id] = text
        LOGGER.debug("section headers = %s" % sorted(self.headers))

    def setTableDescription(self):
        '''
        a user friendly description of the table
        '''
        LOGGER.debug("loading feescale description")
        node = self.dom.getElementsByTagName("feescale_description")[0]
        text = node.childNodes[0].data.strip(" \n")
        self.description = text
        LOGGER.info("Feetable description = %s" % self.description)

    def setStartDate(self):
        '''
        the date the feetable started (can be in the future)
        '''
        LOGGER.debug("loading startdate")
        start_node = self.dom.getElementsByTagName("start")[0]
        day = start_node.getElementsByTagName("day")[0].childNodes[0].data
        month = start_node.getElementsByTagName("month")[0].childNodes[0].data
        year = start_node.getElementsByTagName("year")[0].childNodes[0].data
        self.startDate = datetime.date(int(year), int(month), int(day))
        LOGGER.debug("startDate = %s" % self.startDate)

    def setEndDate(self):
        '''
        the date the feetable became obsolete (can be in the past)
        '''
        LOGGER.debug("loading enddate")
        try:
            end_node = self.dom.getElementsByTagName("end")[0]
        except IndexError:
            self.endDate = None
            LOGGER.debug("feescale is open ended (no end date)")
            return
        day = end_node.getElementsByTagName("day")[0].childNodes[0].data
        month = end_node.getElementsByTagName("month")[0].childNodes[0].data
        year = end_node.getElementsByTagName("year")[0].childNodes[0].data
        self.endDate = datetime.date(int(year), int(month), int(day))
        LOGGER.debug("endDate = %s" % self.endDate)

    @property
    def is_current(self):
        '''
        a boolean value based the table start and end dates
        '''
        return self.endDate is None or \
            self.startDate <= datetime.date.today() <= self.endDate

    def get_ui_buttons(self, tagname):
        for ix, node in enumerate(self.dom.getElementsByTagName(tagname)):
            chart_button = namedtuple('Button', ("ix",
                                                 "shortcut",
                                                 "description",
                                                 "tooltip"))
            chart_button.ix = ix
            chart_button.description = node.getAttribute("description")
            chart_button.tooltip = node.getAttribute("tooltip")
            chart_button.shortcut = node.getAttribute("shortcut")
            yield (chart_button)

    def load_from_xml(self):
        '''
        now load the fee items and shortcuts
        '''
        shortcut_nodes = self.dom.getElementsByTagName("complex_shortcut")
        for shortcut_node in shortcut_nodes:
            complex_shortcut = ComplexShortcut(shortcut_node)
            self.complex_shortcuts.append(complex_shortcut)

        for item_node in self.dom.getElementsByTagName("item"):
            item_code = item_node.getAttribute("id")
            fee_item = FeeItem(self, item_code, item_node)
            self.feesDict[item_code] = fee_item

            if fee_item.usercode is None:
                pass
            elif fee_item.is_regex:
                # use pre-compiled regex as the key
                key = re.compile(fee_item.usercode)
                if fee_item.pt_attribute == "chart":
                    self.chartRegexCodes[key] = item_code
                else:
                    self.otherRegexCodes[key] = item_code
            else:
                if fee_item.pt_attribute == "chart":
                    self.chartPlainCodes[fee_item.usercode] = item_code
                else:
                    self.treatmentCodes[fee_item.usercode] = item_code

        for modifier_node in self.dom.getElementsByTagName("modifier"):
            self.item_modifiers.append(Modifier(modifier_node))

        for button in self.get_ui_buttons("crown_chart_button"):
            self.ui_lists["crown_buttons"].append(button)

        for button in self.get_ui_buttons("post_chart_button"):
            self.ui_lists["post_buttons"].append(button)

        for button in self.get_ui_buttons("fs_chart_button"):
            self.ui_lists["fs_buttons"].append(button)

        for button in self.get_ui_buttons("endo_chart_button"):
            self.ui_lists["endo_buttons"].append(button)

        for button in self.get_ui_buttons("surgical_chart_button"):
            self.ui_lists["surgical_buttons"].append(button)

        for button in self.get_ui_buttons("implant_chart_button"):
            self.ui_lists["implant_buttons"].append(button)

        self.dom.unlink()

    def getToothCode(self, tooth, shortcut):
        '''
        converts fillings into four digit codes used in the feescale
        eg "MOD" -> "1404" (both are strings)
        shortcut will be something like "CR,GO" or "MOD,CO"
        if not found, "-----" will be returned
        '''
        LOGGER.debug("getToothCode for %s%s" % (tooth, shortcut))

        for key in self.chartRegexCodes:
            if key.match(tooth + shortcut):
                return self.chartRegexCodes[key]
        return self.chartPlainCodes.get(shortcut, "-----")

    def getItemCodeFromUserCode(self, arg):
        '''
        return the itemcode associated with it, otherwise, return "-----"
        '''
        LOGGER.debug("looking up usercode %s" % arg)
        for key in self.otherRegexCodes:
            if key.match(arg):
                return self.otherRegexCodes[key]

        return self.treatmentCodes.get(arg, "-----")

    def _getFees(self, itemcode, pt, csetype, shortcut):
        '''
        returns a tuple of (fee, ptfee) for an item
        '''
        LOGGER.debug("%s %s %s" % ('looking up a fee for', itemcode, shortcut))

        try:
            fee_item = self.feesDict[itemcode]
        except KeyError:
            LOGGER.warning("itemcode %s not found in feetable %s" % (
                itemcode, self.database_ix))
            return (0, 0)

        if fee_item.is_simple:
            return fee_item.get_fees(1)

        if fee_item.has_fee_shortcuts:
            return fee_item.get_fees_from_fee_shortcuts(shortcut)

        # complex codes have a different fee if there are multiple
        # in the estimate already
        existing_no = 0
        for existing_est in pt.estimates:
            if (existing_est.itemcode == itemcode and
               csetype == existing_est.csetype):
                existing_no += 1

        return fee_item.get_fees(existing_no + 1)

    def getFees(self, itemcode, pt, csetype, shortcut):
        '''
        a wrapper for the old function
        '''
        LOGGER.debug((itemcode, pt, csetype, shortcut))
        gross, charge = self._getFees(itemcode, pt, csetype, shortcut)
        return self.apply_modifiers(gross, charge, itemcode, pt)

    def recalc_fee(self, pt, itemcode, item_no):
        '''
        returns a tuple of (fee, ptfee) for an item
        '''
        LOGGER.debug("recalculating fee for itemcode %s with %d items" % (
            itemcode, item_no))

        try:
            fee_item = self.feesDict[itemcode]
        except KeyError:
            LOGGER.warning("itemcode %s not found in feetable %s" % (
                itemcode, self.database_ix))
            return (0, 0)

        gross, charge = fee_item.get_fees(item_no)
        return self.apply_modifiers(gross, charge, itemcode, pt)

    def apply_modifiers(self, gross, charge, itemcode, pt):
        for modifier in self.item_modifiers:
            LOGGER.debug("checking modifier %s" % modifier)
            if modifier.condition_met(pt) and modifier.item_id_match(itemcode):
                return modifier.gross_mod(gross), modifier.charge_mod(charge)
        return gross, charge

    def getItemDescription(self, itemcode, usercode):
        '''
        returns the patient readable (ie. estimate ready) description of the
        item
        '''
        try:
            return self.feesDict[itemcode].description
        except KeyError:
            return "%s (%s)" % (_("OTHER TREATMENT"), usercode)

    @property
    def other_shortcuts(self):
        '''
        shortcuts which are used in association with 'other' items
        '''
        items = {}
        for item in list(self.feesDict.values()):
            if item.pt_attribute == "other":
                items[item.description.lower()] = item.shortcut
        for key in sorted(items.keys()):
            yield ("other", items[key])


class FeeItem(object):

    '''
    this class handles the calculation of fees
    part of the challenge is recognising the fact that
    2x an item is not necessarily
    the same as double the fee for a single item etc..
    '''

    def __init__(self, table, itemcode, element):
        self.table = table
        self.itemcode = itemcode

        self.section = getTextFromNode(element, "section")
        try:
            self.obscurity = int(element.getAttribute("obscurity"))
        except ValueError:
            self.obscurity = 0
        self.fees = []
        self.ptFees = []
        self.brief_descriptions = []
        self.conditions = []
        self.shortcut = None
        self.is_regex = False
        self._forbid_reason = None
        self.fee_shortcuts = []

        try:
            shortcut_node = element.getElementsByTagName("shortcut")[0]
            self.is_regex = shortcut_node.getAttribute("type") == "regex"
            self.pt_attribute = shortcut_node.getAttribute("att")
            try:
                self.shortcut = shortcut_node.childNodes[0].data
            except IndexError:
                self.shortcut = None
        except IndexError:
            self.pt_attribute = "other"
            self.is_regex = False
            self.shortcut = None

        if not self.pt_attribute:
            self.pt_attribute = "other"

        self.description = getTextFromNode(element, "description")

        try:
            node = element.getElementsByTagName("feescale_forbid")[0]
            self.allow_feescale_add = False
            reason_nodes = node.getElementsByTagName("reason")
            if reason_nodes:
                self._forbid_reason = reason_nodes[0].childNodes[0].data
        except IndexError:
            self.allow_feescale_add = True

        for node in element.getElementsByTagName("fee"):
            bd = getTextFromNode(node, "brief_description")
            self.brief_descriptions.append(bd)

            fee = int(getTextFromNode(node, "gross"))
            self.fees.append(fee)

            try:  # charge is an optional field.
                charge = int(getTextFromNode(node, "charge"))
                self.ptFees.append(charge)
            except ValueError:
                pass

            condition = _stripped(node.getAttribute("condition"))
            self.conditions.append(condition)

            shortcut_match = node.getAttribute("shortcut_match")
            if shortcut_match:
                self.fee_shortcuts.append(re.compile(shortcut_match))

    def __repr__(self):
        return "FeeItem '%s' %s %s %s %s" % (
            self.itemcode,
            self.description,
            str(self.fees),
            str(self.ptFees),
            str(self.brief_descriptions)
        )

    @property
    def has_pt_fees(self):
        return len(self.ptFees) > 0

    @property
    def is_simple(self):
        '''
        a boolean which is true if n items costs n* fee
        many items the cost goes down with multiples, or there is a maximum fee
        '''
        return len(self.fees) == 1

    @property
    def has_fee_shortcuts(self):
        return self.fee_shortcuts != []

    def fee_shortcut_for_display(self, index):
        try:
            fsfd = self.fee_shortcuts[index].pattern
            if self.pt_attribute == "chart":
                return fsfd
            return "%s %s" % (self.pt_attribute, fsfd)
        except IndexError:
            pass
        except AttributeError:  # not regex? I can't see this happening?
            pass
        return self.usercode

    @property
    def usercode(self):
        if self.shortcut is None:
            return None
        if self.pt_attribute == "chart":
            return self.shortcut
        return"%s %s" % (self.pt_attribute, self.shortcut)

    @property
    def forbid_reason(self):
        if self._forbid_reason is None:
            return _("No reason given by feescale author.")
        return self._forbid_reason

    def get_fees(self, item_no=1):
        '''
        convenience wrapper for getFee function
        returns a tuple fee, ptfee
        '''
        fee = self.get_fee(item_no)
        ptFee = self.get_fee(item_no, charge=True)

        if ptFee is None:
            return (fee, fee)
        else:
            return (fee, ptFee)

    def get_fees_from_fee_shortcuts(self, shortcut):
        '''
        this was introduced to handle the case where a single item code
        has different fees
        specifically, SR_P/R321,L1 is a 4 toothed partial denture
        but that has only 1 itemcode on NHS feescale :(
        '''
        for i, compiled_regex in enumerate(self.fee_shortcuts):
            LOGGER.debug("Comparing '%s' with regex '%s'" % (
                         shortcut, compiled_regex.pattern))

            if compiled_regex.match(shortcut):
                fee = self.fees[i]
                try:
                    charge = self.ptFees[i]
                except IndexError:
                    charge = fee
                return fee, charge

        LOGGER.warning(
            "error getting fee from fee_shortcut. returning default")
        return self.get_fees()

    def get_fee(self, item_no=1, charge=False):
        '''
        get a fee for the xth item of this type
        if charge is true, then return the "charge" rather than the gross fee
        '''
        LOGGER.debug(
            "FeeItem.get_fee(item_no=%d, charge=%s)" % (item_no, charge))
        if charge:
            if self.ptFees == []:
                return None
            feeList = self.ptFees
        else:
            feeList = self.fees

        if self.is_simple or item_no == 1:
            fee = feeList[0]
            LOGGER.debug("simple addition of 1st item, fee=%s" % fee)
            return fee

        LOGGER.warning("Complex FeeItem fee lookup, item_no=%d" % item_no)
        for i, condition in enumerate(self.conditions):
            LOGGER.debug("checking condition '%s'" % condition)
            if condition == "item_no=%d" % item_no:
                fee = feeList[i]
                LOGGER.debug("condition met '%s' fee=%s" % (condition, fee))
                return fee
            m = re.match("item_no>(\d+)", condition)
            if m and item_no > int(m.groups()[0]):
                fee = feeList[i]
                LOGGER.debug("condition met '%s' fee=%s" % (condition, fee))
                return fee
            m = re.match("item_no<(\d+)", condition)
            if m and item_no < int(m.groups()[0]):
                fee = feeList[i]
                LOGGER.debug("condition met '%s' fee=%s" % (condition, fee))
                return fee
            m = re.match("(\d+)<item_no<(\d+)", condition)
            if m and int(m.groups()[0]) < item_no < int(m.groups()[1]):
                fee = feeList[i]
                LOGGER.debug("condition met '%s' fee=%s" % (condition, fee))
                return fee

        # if all has failed.... go with the simple one
        LOGGER.debug("no conditions met... returning simple fee")
        return feeList[0]


class ComplexShortcut(object):

    '''
    this class allows complex logic to be placed into an xml feescale
    complex shortcuts are checked for a match with treatment items
    before the simple one-to-one feeitems are considered.
    '''

    def __init__(self, element):

        shortcut_node = element.getElementsByTagName("shortcut")[0]
        self.is_regex = shortcut_node.getAttribute("type") == "regex"
        self.pt_attribute = shortcut_node.getAttribute("att")

        shortcut = shortcut_node.childNodes[0].data
        LOGGER.debug("Complex shortcut %s %s" % (self.pt_attribute, shortcut))
        if self.pt_attribute != "chart":
            shortcut = "%s %s" % (self.pt_attribute, shortcut)
        if self.is_regex:
            self.shortcut = re.compile(shortcut)
        else:
            self.shortcut = shortcut

        self.addition_cases, self.removal_cases = [], []

        try:
            addition_node = element.getElementsByTagName("addition")[0]
            for case_node in addition_node.getElementsByTagName("case"):
                case_action = CaseAction(case_node)
                self.addition_cases.append(case_action)
                LOGGER.debug(case_action)
        except IndexError:
            LOGGER.debug("no removal cases")

        try:
            removal_node = element.getElementsByTagName("removal")[0]
            for case_node in removal_node.getElementsByTagName("case"):
                case_action = CaseAction(case_node)
                self.removal_cases.append(case_action)
                LOGGER.debug(case_action)
        except IndexError:
            LOGGER.debug("no removal cases")

    def matches(self, att, shortcut):
        '''
        check to see if condition is met
        '''
        if re.match("[ul][lr][1-8A-E]", att):
            if self.is_regex:
                return self.shortcut.match("%s%s" % (att, shortcut))
            return self.shortcut == shortcut
        else:
            usercode = "%s %s" % (att, shortcut)
            if self.is_regex:
                return self.shortcut.match(usercode)
            return self.shortcut == usercode

    def __repr__(self):
        return ("Complex shortcut, '%s'" % (
            self.shortcut if not self.is_regex else self.shortcut.pattern))


class CaseAction(object):

    '''
    a simple class to store what should be performed when a ComplexShortcut
    is matched
    '''
    # some constants to make the code readable
    FULLY_HANDLED = 2
    PARTIALLY_HANDLED = 1
    NOT_HANDLED = 0

    def __init__(self, case_node):
        self.removals = []
        self.additions = []
        self.alterations = []
        self.shortcut_substitution = None

        self.condition = _stripped(case_node.getAttribute("condition"))

        handled = case_node.getAttribute("handled")
        if handled == "no":
            self._is_handled = self.NOT_HANDLED
        elif handled == "part":
            self._is_handled = self.PARTIALLY_HANDLED
        else:  # default is fully handled!
            self._is_handled = self.FULLY_HANDLED

        removal_nodes = case_node.getElementsByTagName("remove_item")
        for removal_node in removal_nodes:
            self.removals.append(removal_node.getAttribute("id"))

        addition_nodes = case_node.getElementsByTagName("add_item")
        for addition_node in addition_nodes:
            self.additions.append(addition_node.getAttribute("id"))

        alteration_nodes = case_node.getElementsByTagName("alter_item")
        for alt_node in alteration_nodes:
            self.alterations.append(alt_node.getAttribute("id"))

        try:
            sub_node = case_node.getElementsByTagName(
                "shortcut_substitution")[0]
            self.shortcut_substitution = \
                sub_node.getAttribute("find"), sub_node.getAttribute("replace")
        except IndexError:
            pass

        self.message = getTextFromNode(case_node, "message")

    @property
    def is_handled(self):
        return self._is_handled

    def __repr__(self):
        return "CaseAction '%s' '%s'" % (self.condition, self.message)


class Modifier(object):

    '''
    feescales can have modifier elements.
    An example of this is you may wish to not charge for some items on certain
    age groups.
    '''

    def __init__(self, modifier_node):
        self.conditions = []
        self.item_ids = []
        self.item_id_regexes = []
        self._gross_fee = None
        self._charge_fee = None

        for node in modifier_node.getElementsByTagName("condition"):
            self.conditions.append(_stripped(node.firstChild.data))
        for node in modifier_node.getElementsByTagName("item_id"):
            item_id = node.firstChild.data
            if node.getAttribute("type") == "regex":
                self.item_id_regexes.append(re.compile(item_id))
            else:
                self.item_ids.append(item_id)
        try:
            self._gross_fee = int(modifier_node.getElementsByTagName(
                                  "gross")[0].firstChild.data)
        except IndexError:
            pass  # no gross fee modification
        try:
            self._charge_fee = int(modifier_node.getElementsByTagName(
                                   "charge")[0].firstChild.data)
        except IndexError:
            pass  # no charge fee modication

    def item_id_match(self, item_id):
        LOGGER.debug(item_id)
        for regex in self.item_id_regexes:
            LOGGER.debug(regex)
            if regex.match(item_id):
                return True
        for id in self.item_ids:
            LOGGER.debug(id)
            if id == item_id:
                return True
        LOGGER.debug("no match")
        return False

    def condition_met(self, pt):
        for condition in self.conditions:
            m = re.match("age<(/d+)$", condition)
            if m and pt.ageYears() < int(m.groups()[0]):
                return True
            m = re.match("age<(\d+)years(\d+)months", condition)
            if m:
                years, months = pt.age_course_start
                years_, months_ = int(m.groups()[0]), int(m.groups()[1])
                if years < years_ or (years == years_ and months < months_):
                    return True
            m = re.match("cset=(.*)$", condition)
            if m and pt.cset == m.groups()[0]:
                return True

        return False

    def gross_mod(self, fee):
        '''
        modify the original fee supplied by the feescale
        this function could do more.. eg %age increases etc?
        '''
        if self._gross_fee is not None:
            return self._gross_fee
        return fee

    def charge_mod(self, fee):
        '''
        modify the original fee supplied by the feescale
        this function could do more.. eg %age increases etc?
        '''
        if self._charge_fee is not None:
            return self._charge_fee
        return fee

    def __repr__(self):
        return "Modifier conditions = %s" % self.conditions


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)

    fts = FeeTables()

    table = fts.default_table
    for id_, fee_item in table.feesDict.items():
        print(id_, fee_item)

    print(table.hasPtCols)
    for i, complex_shortcut in enumerate(table.complex_shortcuts):
        print("looking for SP in complex_shortcut %d" % i)
        if complex_shortcut.matches("perio", "SP"):
            print("    match found")

    print(table.categories)
    print(table.ui_lists)
    print(fts.ui_crown_chart_buttons)
    print(fts.ui_implant_chart_buttons)
