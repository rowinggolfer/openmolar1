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
import re
import shutil

from collections import namedtuple

from openmolar import connect
from openmolar.settings import localsettings

LOGGER = logging.getLogger("openmolar")

def write_readme():
    LOGGER.info("creating directory %s"% FEESCALE_DIR)
    os.makedirs(FEESCALE_DIR)
    f = open(os.path.join(FEESCALE_DIR, "README.txt"), "w")
    f.write('''
This folder is created by openmolar to store xml copies of the feescales in
your database (see feescales table).
Filenames herein are IMPORTANT!
feescale1.xml relates to the xml stored in row 1 of that table
feescale2.xml relates to the xml stored in row 2 of that table

whilst you are free to edit these files using an editor of your choice,
validation against feescale_schema.xsd is highly recommended.

note - openmolar has a build in application for doing this.
    ''')
    f.close()


FEESCALE_DIR = os.path.join(localsettings.localFileDirectory, "feescales")
if not os.path.exists(FEESCALE_DIR):
    write_readme()

QUERY = 'select ix, xml_data from feescales'

UPDATE_QUERY = "update feescales set xml_data = %s where ix = %s"

NEW_FEESCALE_QUERY = "insert into feescales (xml_data) values(%s)"

class FeescaleHandler(object):

    def get_feescales_from_database(self,
    in_use_only=True, priority_order=True):
        '''
        connects and get the data from feetable_key
        '''
        query = QUERY
        if in_use_only:
            query += ' where in_use = True'
        if priority_order:
            query += ' order by priority desc'
        db = connect.connect()
        cursor = db.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        LOGGER.debug("%d feescales retrieved"% len(rows))
        return rows

    def save_file(self, ix, xml_data):
        file_path = self.index_to_local_filepath(ix)
        LOGGER.debug("writing %s"% file_path)
        f = open(file_path, "w")
        f.write(xml_data)
        f.close()

    def _xml_data_and_filepaths(self):
        for ix, xml_data in self.get_feescales_from_database(False):
            xml_file = namedtuple("XmlFile", ("data", "filepath"))
            xml_file.data = xml_data
            xml_file.filepath = self.index_to_local_filepath(ix)

            yield xml_file

            #self.save_file(ix, xml_data)
        #LOGGER.info("feescales data written to local filesystem")

    def non_existant_and_modified_local_files(self):
        '''
        returns 2 lists
        [local files which have been created]
        [local files which differ from stored data]
        '''
        unwritten, modified = [], []
        for xml_file in self._xml_data_and_filepaths():
            if not os.path.isfile(xml_file.filepath):
                unwritten.append(xml_file)
            else:
                f = open(xml_file.filepath, "r")
                if f.read().strip() != xml_file.data:
                    modified.append(xml_file)
                f.close()
        return unwritten, modified

    def index_to_local_filepath(self, ix):
        return os.path.join(FEESCALE_DIR, "feescale_%d.xml"% ix)

    @property
    def local_files(self):
        for file_ in sorted(os.listdir(FEESCALE_DIR)):
            m = re.match(".*(\d+)\.xml$", file_)
            if m:
                ix = int(m.groups()[0])
                yield ix, os.path.join(FEESCALE_DIR, file_)

    def update_db_all(self):
        '''
        apply all local file changes to the database.
        '''
        message = ""
        for ix, filepath in self.local_files:
            message += self.update_db(ix)

        return message

    def update_db(self, ix):
        message = ""
        filepath = self.index_to_local_filepath(ix)
        LOGGER.debug("updating database ix %s"% ix)
        if not os.path.isfile(filepath):
            message = "FATAL %s does not exist!"% filepath
        else:
            db = connect.connect()
            cursor = db.cursor()

            f = open(filepath)
            data = f.read()
            f.close()

            values = (data, ix)
            result =  cursor.execute(UPDATE_QUERY, values)

            r_message = "commiting feescale '%s' to database."% filepath
            message = "updating feescale %d    result = %s\n"% (
                ix, "OK" if result else "No Change applied")

            db.close()
            LOGGER.info(r_message + " " + message)

        return message

    def save_xml(self, ix, xml):
        file_path = self.index_to_local_filepath(ix)
        LOGGER.info("saving %s"% file_path)

        LOGGER.debug("creating backup")
        try:
            shutil.copy(file_path, file_path+"~")
        except IOError:
            LOGGER.warning("no backup file created")

        f = open(file_path, "w")
        f.write(xml)
        f.close()
        return True


feescale_handler = FeescaleHandler()

if __name__ == "__main__":
    logging.basicConfig()
    LOGGER.setLevel(logging.DEBUG)

    fh = FeescaleHandler()
    fh.get_feescales_from_database()
    print fh.non_existant_and_modified_local_files()
