# -*- coding: utf-8 -*-
# Copyright (c) 2009 Neil Wallace. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. See the GNU General Public License for more details.


import datetime
import logging

from openmolar.connect import connect

CHECK_INTERVAL = 300 #update phrasebook every 5 minutes

BLANK_PHRASEBOOK = '''<?xml version="1.0" ?>
    <phrasebook>
        <section>
            <header>Example</header>
            <phrase>An Example Phrase!</phrase>
            <phrase>Another Phrase</phrase>
        </section>
        <section>
            <header>Perio</header>
            <phrase>An Example Phrase!</phrase>
        </section>
    </phrasebook>'''

ALL_BOOKS_QUERY = "select distinct clinician_id from phrasebook"

QUERY = "select phrases from phrasebook where clinician_id=%s"

UPDATE_QUERY = "update phrasebook set phrases = %s where clinician_id = %s"
INSERT_QUERY = "insert into phrasebook (phrases, clinician_id) values(%s, %s)"

LOGGER = logging.getLogger("openmolar")

class Phrasebooks(object):
    _books = {}

    @property
    def global_phrasebook(self):
        return self.book(0)

    def book(self, index):
        book = self._books.get(index, None)
        if book is None:
            book = Phrasebook(index)
            self._books[index] = book
        return book

    def has_book(self, index):
        return self._books.has_key(index)

    def has_phrasebook(self, index):
        return self.book(index).has_data

    def get_all_books(self):
        self._books = {} #forget any loaded books
        db = connect()
        cursor = db.cursor()
        cursor.execute(ALL_BOOKS_QUERY)
        rows = cursor.fetchall()
        ixs = []
        for row in rows:
            ixs.append(row[0])
        cursor.close()
        for ix in ixs:
            yield self.book(ix)

    def update_database(self, xml, clinician_id):
        db = connect()
        cursor = db.cursor()
        result = cursor.execute(UPDATE_QUERY, (xml, clinician_id))
        cursor.close()
        self._books = {} #forget any loaded books
        return result

    def create_book(self, clinician_id):
        db = connect()
        cursor = db.cursor()
        result = cursor.execute(INSERT_QUERY, (BLANK_PHRASEBOOK, clinician_id))
        cursor.close()
        self._books = {} #forget any loaded books
        return result


class Phrasebook(object):
    _xml = None
    _time = datetime.datetime.now()

    def __init__(self, ix):
        self.ix = ix

    @property
    def loaded(self):
        return self._xml is not None

    @property
    def refresh_needed(self):
        now = datetime.datetime.now()
        return now - self._time > datetime.timedelta(0, CHECK_INTERVAL)

    @property
    def xml(self):
        if not self.loaded or self.refresh_needed:
            LOGGER.info("(re)loading phrasebook %s from database"% self.ix)
            db = connect()
            cursor = db.cursor()
            cursor.execute(QUERY, (self.ix,))
            rows = cursor.fetchone()
            self._xml = rows[0] if rows else BLANK_PHRASEBOOK
            cursor.close()
            self._time = datetime.datetime.now()
        return self._xml

    @property
    def has_data(self):
        return self.xml != BLANK_PHRASEBOOK

PHRASEBOOKS = Phrasebooks()


if __name__ == "__main__":
    print PHRASEBOOKS.global_phrasebook
    print PHRASEBOOKS.book(1)