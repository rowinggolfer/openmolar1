#! /usr/bin/python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2013, Neil Wallace <neil@openmolar.com>                        ##
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

import logging
import os
from xml.dom import minidom

from PyQt4 import QtCore
from PyQt4.QtXmlPatterns import (
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
        position = "line %s column %d"% (source.line(), source.column())

        LOGGER.debug("xml message - type =        '%s'"% type_)
        LOGGER.debug("xml message - description = '%s'"% descr)
        LOGGER.debug("xml message - id =          '%s'"% id_)
        LOGGER.debug("xml message - source      = %s"% position)

        self.last_error = descr.replace("</body>", "<p>%s</p></body>"% position)

    def reset(self):
        self.last_error = ""

class FeescaleParser(object):
    def __init__(self, filepath):
        self._edited_text = None
        self._items = None
        self.filepath = filepath
        LOGGER.info("parsing feescale %s"% filepath)
        self.orig_modified = self.last_modified
        self.dom = minidom.parse(filepath)

        self.document_element = self.dom.childNodes[0]
        self.saved_xml = self.text

        self.message_handler = MessageHandler()

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
        LOGGER.info("refreshing feescale %s"% self.filepath)
        self._edited_text = None
        self._items = None
        self.dom = minidom.parse(self.filepath)
        self.document_element = self.dom.childNodes[0]
        self.saved_xml = self.text

    def check_validity(self, xml):
        '''
        check that the dom validates
        '''
        self.message_handler.reset()

        f = QtCore.QFile(STYLESHEET)
        f.open(QtCore.QIODevice.ReadOnly)
        schema = QXmlSchema()
        schema.load(f)

        validator = QXmlSchemaValidator(schema)
        validator.setMessageHandler(self.message_handler)
        result = validator.validate(xml)

        if result:
            LOGGER.debug(
                "Feescale complies with stylesheet!")
        else:
            LOGGER.warning(
                "Feescale does not comply with stylesheet %s"% STYLESHEET)
        return (result, self.message_handler.last_error)

    def is_valid(self):
        LOGGER.debug("checking validity of %s"% self.dom)
        return self.check_validity(self.text)

    @property
    def items(self):
        if self._items is None:
            self._items = self.dom.getElementsByTagName("item")
            LOGGER.debug("%d items"% len(self._items))
        return self._items

    @property
    def feenodes(self):
        for item in self.items:
            for feenode in item.getElementsByTagName("fee"):
                yield feenode

    def increase_fees(self, percentage):
        def increase(pence):
            mult = 100 + percentage
            new_pence = pence * mult
            return int(new_pence//100)
        for att in ("gross", "charge"):
            for node in self.dom.getElementsByTagName(att):
                fee = node.firstChild.data
                new_fee = str(increase(int(fee)))
                message = "%s %s increased to %s"% (
                    att.ljust(8, " "), fee.rjust(8," "), new_fee.rjust(8," "))
                node.firstChild.replaceWholeText(str(new_fee))

                LOGGER.debug(message)

        self._edited_text = None
        LOGGER.info("%s fees increased by %s%%"% (self.description,percentage))

    @property
    def description(self):
        try:
            description_nodes = self.dom.getElementsByTagName(
            "feescale_description")
            return description_nodes[0].childNodes[0].data
        except:
            LOGGER.exception("unable to get description from Feescale Parser")
            return _("Unknown TableName")

    def code_text(self, index):
        item_node = self.items[index]
        id_ = item_node.getAttribute("id")
        try:
            name = item_node.getElementsByTagName(
                "description")[0].childNodes[0].data
        except IndexError:
            name = ""
        return "%s - %s"% (id_, name)

    def set_edited_text(self, text):
        self._edited_text = unicode(text)
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
    fp = FeescaleParser(example_path)
    return fp


if __name__ == "__main__":
    LOGGER.setLevel(logging.DEBUG)
    app = QtCore.QCoreApplication([])

    fp = _test()
    fp.is_valid()
    LOGGER.info(fp.message_handler.last_error)
    fp.increase_fees(2.51)
    LOGGER.debug("script has finished")
