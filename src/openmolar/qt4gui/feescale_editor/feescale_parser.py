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

from gettext import gettext as _

import logging
import os
import re
from xml.dom import minidom

from PyQt5 import QtCore
from PyQt5.QtXmlPatterns import (
    QXmlSchemaValidator,
    QXmlSchema,
    QAbstractMessageHandler)

from openmolar.settings.localsettings import resources_location

LOGGER = logging.getLogger("openmolar")

STYLESHEET = os.path.join(
    resources_location, "feescales", "feescale_schema.xsd")


class MessageHandler(QAbstractMessageHandler):
    last_error = ""

    def __init__(self, parent=None):
        QAbstractMessageHandler.__init__(self, parent)

    def handleMessage(self, type_, descr, id_, source):
        position = "line %s column %d" % (source.line(), source.column())

        LOGGER.debug("xml message - type =        '%s'" % type_)
        LOGGER.debug("xml message - description = '%s'" % descr)
        LOGGER.debug("xml message - id =          '%s'" % id_)
        LOGGER.debug("xml message - source      = %s" % position)

        self.last_error = descr.replace(
            "</body>", "<p>%s</p></body>" %
            position)

    def reset(self):
        self.last_error = ""


class FeescaleParser(object):

    def __init__(self, filepath, ix):
        self._edited_text = None
        self._items = None
        self._c_scuts = None
        self.filepath = filepath
        self.ix = ix
        LOGGER.info("parsing feescale %s" % filepath)
        self.orig_modified = self.last_modified
        self.dom = minidom.Document()
        self.dom.appendChild(self.dom.createElement("feescale"))
        self.document_element = self.dom.childNodes[0]
        self.saved_xml = self.text
        self.message_handler = MessageHandler()

    def parse_file(self):
        try:
            self.dom = minidom.parse(self.filepath)
            self._edited_text = None
            self.document_element = self.dom.childNodes[0]
            self.saved_xml = self.text
        except Exception as exc:
            f = open(self.filepath, "r")
            self._edited_text = f.read()
            f.close()
            LOGGER.exception("unable to parse %s" % self.filepath)
            raise exc

    @property
    def label_text(self):
        return "%s %d" % (_("feescale"), self.ix)

    @property
    def detailed_label_text(self):
        return "%s %s" % (self.label_text, self.tablename)

    @property
    def is_externally_modified(self):
        return self.last_modified > self.orig_modified

    @property
    def is_deleted(self):
        return not os.path.isfile(self.filepath)

    @property
    def last_modified(self):
        return os.path.getmtime(self.filepath)

    def reset_orig_modified(self):
        self.orig_modified = self.last_modified

    def refresh(self):
        LOGGER.info("refreshing feescale %s" % self.filepath)
        self._edited_text = None
        self._items = None
        self.dom = minidom.parse(self.filepath)
        self.document_element = self.dom.childNodes[0]
        self.saved_xml = self.text
        self.reset_orig_modified()

    def check_validity(self, xml):
        '''
        check that the dom validates
        '''
        self.message_handler.reset()

        LOGGER.debug("checking phrasebook xml against %s", STYLESHEET)

        f = QtCore.QFile(STYLESHEET)
        f.open(QtCore.QIODevice.ReadOnly)
        schema = QXmlSchema()
        schema.load(f)

        validator = QXmlSchemaValidator(schema)
        validator.setMessageHandler(self.message_handler)
        result = validator.validate(xml)

        if result:
            LOGGER.debug("Feescale complies with stylesheet!")
        else:
            LOGGER.warning(
                "Feescale does not comply with stylesheet %s" % STYLESHEET)
        return (result, self.message_handler.last_error)

    def is_valid(self):
        LOGGER.debug("checking validity of %s" % self.dom)
        return self.check_validity(self.text)

    @property
    def items(self):
        if self._items is None:
            self._items = self.dom.getElementsByTagName("item")
            LOGGER.debug("%d items" % len(self._items))
        return self._items

    def item_ids(self, index):
        '''
        returns the id attibute of the item at position index in the list
        '''
        item_node = self.items[index]
        return item_node.getAttribute("id")

    def itemnode_from_id(self, id, ignore_prefix=False):
        '''
        returns the itemnode which contains the item with specified id,
        or a blank node if node exists
        '''
        def remove_prefix(s):
            return s.groups()[1]
        if ignore_prefix:
            id = re.sub("([^\d]*)(\d+)$", remove_prefix, id)
        LOGGER.debug("looking for %s" % id)
        for itemnode in self.items:
            node_id = itemnode.getAttribute("id")
            if ignore_prefix:
                node_id = re.sub("([^\d]*)(\d+)$", remove_prefix, node_id)
            if node_id == id:
                return itemnode

    @property
    def complex_shortcuts(self):
        if self._c_scuts is None:
            self._c_scuts = self.dom.getElementsByTagName("complex_shortcut")
            LOGGER.debug("%d complex shortcuts" % len(self._c_scuts))
        return self._c_scuts

    @property
    def feenodes(self):
        for item in self.items:
            for feenode in item.getElementsByTagName("fee"):
                yield feenode

    def roundup_charges(self, precision, up=False, down=False):
        self.roundup_fees(precision, up=False, down=False, att="charge")

    def roundup_fees(self, precision, up=False, down=False, att="gross"):
        LOGGER.debug((precision, up, down, att))

        def round_to_value(pence, r_up=False, r_down=False):
            offset = pence % precision
            LOGGER.debug(offset)
            if offset == 0:
                return int(pence)
            if r_up:
                return int(pence + (precision - offset))
            if r_down:
                return int(pence - offset)
            if offset < (precision + 1) // 2:
                return round_to_value(pence, r_down=True)
            else:
                return round_to_value(pence, r_up=True)

        for node in self.dom.getElementsByTagName(att):
            fee = node.firstChild.data
            new_fee = str(round_to_value(int(fee), up, down))
            message = "%s %s changed to %s" % (
                att.ljust(8, " "), fee.rjust(8, " "), new_fee.rjust(8, " "))
            node.firstChild.replaceWholeText(new_fee)

        self._edited_text = None
        LOGGER.debug(message)

    def increase_charges(self, percentage):
        self.increase_fees(percentage, att="charge")

    def increase_fees(self, percentage, att="gross"):
        def increase(pence):
            return int((pence * mult) // 100)

        mult = 100 + percentage
        for node in self.dom.getElementsByTagName(att):
            fee = node.firstChild.data
            new_fee = str(increase(int(fee)))
            message = "%s %s increased to %s" % (
                att.ljust(8, " "), fee.rjust(8, " "), new_fee.rjust(8, " "))
            node.firstChild.replaceWholeText(new_fee)

            LOGGER.debug(message)

        self._edited_text = None
        LOGGER.info("%s %s fees increased by %s%%",
                    (self.description, att, percentage))

    def relate_charges_to_gross_fees(self, percentage,
                                     leave_zeros_untouched=False):
        def get_charge(pence):
            return int(pence * percentage // 100)

        for node in self.dom.getElementsByTagName("gross"):
            charge_nodes = node.parentNode.getElementsByTagName("charge")
            if charge_nodes == []:
                continue
            charge_node = charge_nodes[0]
            fee = node.firstChild.data
            charge = charge_node.firstChild.data
            if charge == "0" and leave_zeros_untouched:
                continue
            new_charge = str(get_charge(int(fee)))
            message = "Fee %s has a charge of %s" % (
                fee.rjust(8, " "), new_charge.rjust(8, " "))
            charge_node.firstChild.replaceWholeText(new_charge)

            LOGGER.debug(message)

        self._edited_text = None

    def zero_charges(self):
        for node in self.dom.getElementsByTagName("charge"):
            # fee = node.firstChild.data
            node.firstChild.replaceWholeText("0")

        self._edited_text = None
        LOGGER.info("%s patient charges zeroed" % self.description)

    @property
    def tablename(self):
        try:
            node = self.dom.getElementsByTagName("tablename")[0]
            return node.firstChild.data
        except:
            LOGGER.exception("unable to get tablename from Feescale Parser")
            return _("Unknown TableName")

    @property
    def description(self):
        try:
            description_nodes = self.dom.getElementsByTagName(
                "feescale_description")
            return description_nodes[0].childNodes[0].data
        except:
            LOGGER.exception("unable to get description from Feescale Parser")
            return _("Unknown Description")

    def code_text(self, index):
        node = self.items[index]
        id_ = node.getAttribute("id")
        try:
            name = node.getElementsByTagName(
                "description")[0].firstChild.data
        except AttributeError:
            name = ""
        return "%s - %s" % (id_, name)

    def complex_shortcut_text(self, index):
        node = self.complex_shortcuts[index]
        shortcut_node = node.getElementsByTagName("shortcut")[0]
        att = shortcut_node.getAttribute("att")
        shortcut = shortcut_node.firstChild.data
        return "%s - %s" % (att, shortcut)

    def set_edited_text(self, text):
        self._edited_text = str(text)
        try:
            dom = minidom.parseString(self._edited_text)
            self.dom = dom
            if len(self.dom.getElementsByTagName("item")) != len(self._items):
                self._items = None
                return True
        except Exception:  # should be ExpatError, but can't find it yet!
            pass
        return False

    @property
    def text(self):
        '''
        the full text of feescale
        '''
        if self._edited_text is not None:
            return self._edited_text
        return self.dom.toxml()

    @property
    def is_dirty(self):
        return self.text != self.saved_xml


def _test():
    LOGGER.debug("running _test")

    example_path = os.path.join(
        resources_location, "feescales", "example_feescale.xml")
    fp = FeescaleParser(example_path, 1)
    fp.parse_file()

    return fp


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtCore.QCoreApplication([])

    fp = _test()
    fp.is_valid()
    LOGGER.info(fp.message_handler.last_error)
    fp.increase_fees(2.51)
    LOGGER.debug("script has finished")
