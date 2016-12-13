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

# note for production deployments, only grant
# select,insert,update,delete privileges
PRIVS_QUERY = "GRANT ALL PRIVILEGES ON %s.* TO '%s'@'%s' IDENTIFIED BY '%s'"

CHECK_SUPERVISOR_QUERY = '''
SELECT Create_priv, Drop_priv, Trigger_priv FROM user WHERE User=%s and Host=%s
'''


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
                             db=db_name)
        if db.open:
            db.close()
            return True
    except:
        LOGGER.warning("exists_already threw error, passing silently")
    return False


def check_superuser(host_, port_, passwd, user="root"):
    '''
    returns true if database 'db_name' exists
    '''
    result = False
    messages = []
    try:
        LOGGER.info("Connecting to mysql to check superuser")
        db = MySQLdb.connect(host=host_,
                             port=port_,
                             user=user,
                             passwd=passwd,
                             db='mysql')
        if db.open:
            cursor = db.cursor()
            cursor.execute(CHECK_SUPERVISOR_QUERY, (user, host_))
            rows = cursor.fetchall()
            db.close()
            for create, drop, trigger in rows:
                if create == "Y" and drop =="Y":
                    result = True
                if create == "N":
                    messages.append(
                        "'%s'on'%s' does not have create database privileges")
                if drop == "N":
                    messages.append(
                        "'%s'on'%s' does not have drop database privileges")
                if trigger == "N":
                    messages.append(
                        "'%s'on'%s' does not have trigger privileges")
    except MySQLdb.OperationalError as exc:
        LOGGER.exception("error caught")
        return False, [str(s) for s in exc.args]
    except:
        LOGGER.exception("check_supervisor threw error, passing silently")
        messages.append("%s - %s '%%s' %s '%%s'" % (
            _("Unable to connect to mysql"),
            _("please check password for"),
            _("on")))
    return result, [m % (user, host_) for m in messages]


def create_database(host_, port_, user_, pass_wd, db_name,
                    privileged_user_pass, privileged_user="root"):
    '''
    creates a database called "db_name" on host_, port_, passwd,
    '''
    try:
        LOGGER.info("Connecting to mysql")
        # connect as mysqlroot to create the database
        db = MySQLdb.connect(host=host_,
                             port=port_,
                             user=privileged_user,
                             passwd=privileged_user_pass)

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
        return True, "success"
    except Exception as exc:
        LOGGER.exception("error creating database")
        return False, exc.args[1]


def create_tables(host_, port_, user_, pass_wd, db_name):
    try:
        fp = os.path.join(localsettings.RESOURCE_DIR, "schema.sql")
        f = open(fp, "r")
        sql_statements = f.read()
        f.close()
        LOGGER.info("Connecting to mysql")

        db = MySQLdb.connect(host=host_,
                             port=port_,
                             user=user_,
                             db=db_name,
                             passwd=pass_wd)

        cursor = db.cursor()
        LOGGER.info("Executing sql statements from %s", fp)
        cursor.execute(sql_statements)
        cursor.close()
        db.commit()
        db.close()
        return True
    except:
        LOGGER.exception("error creating database tables")


def insert_data(host_, port_, user_, pass_wd, db_name, minimal_only=False):
    '''
    An openmolar database requires some userdata before the application can
    run.
    if minimal_only is False (the default) a demo patient is installed also.
    '''
    result = False
    try:
        for i, fp in enumerate(("minimal_data.sql", "demo_data.sql")):
            if minimal_only and i == 1:
                continue
            f = open(os.path.join(localsettings.RESOURCE_DIR, fp), "r")
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
        result = True
    except:
        LOGGER.exception("error inserting minimal data")
    return result


if __name__ == "__main__":
    import getpass
    LOGGER.setLevel(logging.DEBUG)
    root_pass = getpass.getpass("please enter your MySQL root users password :")
    print("exists already = %s" %
          exists_already("localhost", 3306, "openmolar_demo", root_pass))

    if create_database("localhost", 3306, "openmolar", "password",
                       "openmolar_demo", root_pass):
        LOGGER.debug("New database created successfully")
        create_tables("localhost", 3306, "openmolar", "password",
                      "openmolar_demo")
        insert_data("localhost", 3306, "openmolar", "password",
                      "openmolar_demo")
