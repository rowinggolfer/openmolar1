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

from openmolar import connect
from openmolar.settings import localsettings

headers = [_("Subject"), "db_index", _("From"), _("To"),
           _("Date"), _("Message"), _("Message")]  # , "parent"]

HIGHESTID = 0


class ForumPost(object):
    ix = None
    parent_ix = None
    inits = ""
    recipient = None
    date = None
    topic = ""
    comment = ""
    briefcomment = ""
    open = True


def commitPost(post):
    # use a different connection for forum, as it runs in a separate thread

    db = connect.connect()
    cursor = db.cursor()
    columns = "parent_ix,inits,recipient,fdate,topic,comment"

    values = (post.parent_ix, post.inits, post.recipient,
              post.topic, post.comment.replace("\n", " "))

    query = \
        "insert into forum (%s) VALUES (%%s,%%s,%%s,NOW(),%%s,%%s)" % columns

    cursor.execute(query, values)
    db.commit()


def deletePost(ix):
    db = connect.connect()
    cursor = db.cursor()
    query = "update forum set open=False where ix=%s"
    cursor.execute(query, (ix,))
    db.commit()
    cursor.close()


def setParent(ix, parent_ix):
    db = connect.connect()
    cursor = db.cursor()
    query = "update forum set parent_ix=%s where ix=%s"
    cursor.execute(query, (parent_ix, ix))
    db.commit()
    cursor.close()


def newPosts():
    '''
    returns a boolean as to whether there have been new posts in the forum
    since the last visit of the current users.
    '''
    users = localsettings.operator.split("/")
    if users == []:  # shouldn't happen!!
        return
    db = connect.connect()
    cursor = db.cursor()
    query = 'select max(ix) from forum'
    cursor.execute(query)
    max_id = cursor.fetchone()[0]
    query = ('select min(id) from '
             '(select max(id) as id, op from forumread where %s group by op) '
             'as t' % " or ".join(["op=%s" for user in users]))
    cursor.execute(query, users)
    max_id2 = cursor.fetchone()[0]
    cursor.close()
    try:
        return max_id > max_id2
    except TypeError:  # max_id2 may be None
        pass
    return True


def updateReadHistory():
    users = localsettings.operator.split("/")
    # print "updating forumread for new posts for ", users
    if users == []:
        return
    db = connect.connect()
    cursor = db.cursor()
    query = "insert into forumread set id=%s, op=%s, readdate=NOW()"
    for user in users:
        values = (HIGHESTID, user)
        cursor.execute(query, values)

    cursor.close()


def getPosts(user=None, include_closed=False):
    '''
    gets all active rows from a forum table
    '''
    global HIGHESTID
    conditions, values = ["open"], [not include_closed]
    if user:
        conditions.append('recipient')
        values.append(user)
    db = connect.connect()
    cursor = db.cursor()
    query = ('SELECT ix, parent_ix, topic, inits, fdate, recipient, comment '
             'FROM forum where %s ORDER BY parent_ix, ix' % " and ".join(
                 ["%s=%%s" % val for val in conditions]))

    cursor.execute(query, values)
    rows = cursor.fetchall()
    cursor.close()

    retarg = []
    update = False
    for row in rows:
        newpost = ForumPost()
        newpost.ix = row[0]
        if newpost.ix > HIGHESTID:
            HIGHESTID = newpost.ix
            update = True
        newpost.parent_ix = row[1]
        newpost.topic = row[2]
        newpost.inits = row[3]
        newpost.date = row[4]
        newpost.recipient = row[5]
        newpost.comment = row[6]
        newpost.briefcomment = row[6][:40]
        if newpost.comment != newpost.briefcomment:
            newpost.briefcomment += "...."
        retarg.append(newpost)

    if update:
        updateReadHistory()
    return retarg


if __name__ == "__main__":
    forumposts = getPosts(user="NW")
    for post_ in forumposts:
        print(post_.parent_ix, post_.ix, post_.topic)
