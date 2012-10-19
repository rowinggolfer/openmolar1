#! /usr/bin/python

from openmolar import connect
from openmolar.ptModules import notes

try:
    from collections import OrderedDict
except ImportError:
    #OrderedDict only came in python 2.7
    print "using openmolar.backports for OrderedDict"
    from openmolar.backports import OrderedDict


def get_notes(sno):
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute('''SELECT line from notes where serialno = %s
    order by lineno''', sno)
    results = cursor.fetchall()
    cursor.close()

    notes_dict = OrderedDict()
    ndate, op = "", ""

    #a line is like ('\x01REC\x0c\x08m\x0c\x08m\n\x08',)
    for line, in results:
        ntype, note, operator, date2 = notes.decipher_noteline(line)
        if date2 != "":
            ndate = date2
        if operator != "":
            op = operator

        key = (ndate, op)
        if notes_dict.has_key(key):
            notes_dict[key].append((ntype, note))
        else:
            notes_dict[key] = [(ntype, note)]

    return notes_dict


def transfer(sno):
    print "transferring notes for serialnos %s"% sno,
    notes_dict = get_notes(sno)
    query = '''insert into formatted_notes
    (serialno, ndate, op1 , op2 , ntype, note)
    values (%s, %s, %s, %s, %s, %s)'''

    values = []
    for key in notes_dict:
        date, ops = key
        op2=None
        if "/" in ops:
            op1, op2 = ops.split("/")
        else:
            op1=ops

        for ntype, note in notes_dict[key]:
            values.append((sno, date, op1, op2, ntype, note))
    if values:
        db = connect.connect()
        cursor = db.cursor()
        rows = cursor.executemany(query, values)
        print "%d rows of notes inserted"% rows
        cursor.close()
        db.commit()
    else:
        print "no notes inserted"

def get_max_sno():
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute("select max(serialno) from notes")
    max_sno = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return max_sno

if __name__ == "__main__":
    max_sno = get_max_sno()
    print "modding notes up to maximum found", max_sno
    sno = 0
    while sno < max_sno:
        transfer(sno)
