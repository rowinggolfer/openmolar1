#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ############################################################################ #
# #                                                                          # #
# # Copyright (c) 2009-2014 Neil Wallace <neil@openmolar.com>                # #
# #                                                                          # #
# # This file is part of OpenMolar.                                          # #
# #                                                                          # #
# # OpenMolar is free software: you can redistribute it and/or modify        # #
# # it under the terms of the GNU General Public License as published by     # #
# # the Free Software Foundation, either version 3 of the License, or        # #
# # (at your option) any later version.                                      # #
# #                                                                          # #
# # OpenMolar is distributed in the hope that it will be useful,             # #
# # but WITHOUT ANY WARRANTY; without even the implied warranty of           # #
# # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            # #
# # GNU General Public License for more details.                             # #
# #                                                                          # #
# # You should have received a copy of the GNU General Public License        # #
# # along with OpenMolar.  If not, see <http://www.gnu.org/licenses/>.       # #
# #                                                                          # #
# ############################################################################ #

'''
this module takes the demo dump and creates a database from it with the
correct user permissions.
'''

import logging
import os

import MySQLdb
from openmolar.settings import localsettings

LOGGER = logging.getLogger("openmolar")

DROP_QUERY = "DROP DATABASE IF EXISTS %s"
CREATE_QUERY = "CREATE DATABASE %s"

#-- note for production deployments, only grant
#-- select,insert,update,delete privileges
PRIVS_QUERY = "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%s' IDENTIFIED BY '%s'"


def exists_already(host_, port_, db_name, privileged_user_pass,
privileged_user="root"):
    '''
    returns true if database 'db_name' exists
    '''
    try:
        db = MySQLdb.connect(host=host_,
                             port=port_,
                             user=privileged_user,
                             passwd=privileged_user_pass,
                            db=db_name
                            )
        if db.open:
            db.close()
            return True
    except:
        LOGGER.warning("exists already through error, passing silently")
        pass
    return False

def create_database(host_, port_, user_, pass_wd, db_name,
privileged_user_pass, privileged_user="root"):
    '''
    creates a database called "db_name" on host_, port_, passwd,
    '''
    try:
        #-- connect as mysqlroot to create the database
        db = MySQLdb.connect(host=host_,
                             port=port_,
                             user=privileged_user,
                             passwd=privileged_user_pass
                             )

        cursor = db.cursor()
        LOGGER.info("deleting any existing openmolar_demo database....")
        cursor.execute(DROP_QUERY % db_name)

        LOGGER.info("creating database %s", db_name)
        cursor.execute(CREATE_QUERY % db_name)

        LOGGER.info("setting privileges for '%s'", user_)
        cursor.execute(PRIVS_QUERY % (db_name, user_, host_, pass_wd))
        cursor.close()
        db.commit()
        db.close()
        LOGGER.info("db created successfully")
        return True
    except:
        LOGGER.exception("error creating database")


def create_tables(host_, port_, user_, pass_wd, db_name):
    try:
        wkdir = localsettings.determine_path()
        f = open(os.path.join(wkdir, "resources", "schema.sql"), "r")
        sql_statements = f.read()
        f.close()

        db = MySQLdb.connect(host=host_,
                             port=port_,
                             user=user_,
                             db=db_name,
                             passwd=pass_wd)

        cursor = db.cursor()
        cursor.execute(sql_statements)
        cursor.close()
        db.commit()
        db.close()
        return True
    except:
        LOGGER.exception("error creating database tables")

if __name__ == "__main__":
    root_pass = raw_input("please enter your MySQL root users password :")
    print "exists already", exists_already("localhost",
                       3306,
                       "openmolar_demo",
                       root_pass
                       )

    if create_database("localhost",
                       3306,
                       "openmolar",
                       "password",
                       "openmolar_demo",
                       root_pass
                       ):
        LOGGER.debug("New database created successfully")

        create_tables(
            "localhost",
            3306,
            "openmolar",
            "password",
            "openmolar_demo")

