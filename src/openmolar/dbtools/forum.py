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

import logging

from openmolar import connect
from openmolar.settings import localsettings

LOGGER = logging.getLogger("openmolar")

headers = [_("Subject"), "db_index", _("From"), _("To"),
           _("Date"), _("Message"), ]

QUERY = '''select ix, forum.parent_ix, topic, inits,fdate, recipient, comment
from forum left join (select parent_ix, max(fdate) as maxdate from forum
where forum.open group by parent_ix) as t on forum.parent_ix = t.parent_ix
%s order by maxdate'''

PARENTS_QUERY = '''update forum set parent_ix = ix where parent_ix is NULL'''

READPOSTS_QUERY = "select id from forumread where op=%s"

READPOSTS_UNREAD_QUERY = "delete from forumread where op=%s and id=%s"

READPOSTS_UPDATE_QUERY = '''insert into forumread (op, id, readdate)
values (%s, %s, NOW())'''

UNREAD_POSTS_QUERY = '''select count(*) from forum where open and ix not in
(select id from forumread where op=%s)'''

INSERT_QUERY = '''
insert into forum (parent_ix, inits, recipient, fdate, topic, comment)
VALUES (%s, %s, %s, NOW(), %s, %s)'''

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


def is_fully_read():
    users = localsettings.operator.split("/")
    if users == []:  # shouldn't happen!!
        return True
    unread_posts = 0
    for user in users:
        unread_posts += number_of_unread_posts(user)
    return unread_posts == 0


def number_of_unread_posts(user):
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(UNREAD_POSTS_QUERY, (user,))
    unread_posts = cursor.fetchone()[0]
    cursor.close()
    LOGGER.debug("%s has %s unread posts", user, unread_posts)
    return unread_posts


def commitPost(post):
    '''
    commit a post to the database, and mark it as read by the person posting it
    '''
    values = (post.parent_ix, post.inits, post.recipient, post.topic,
              post.comment)
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(INSERT_QUERY, values)
    ix = db.insert_id()
    cursor.execute(READPOSTS_UPDATE_QUERY, (post.inits, ix))
    db.commit()
    return ix


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


def update_forum_read(user, read_ids):
    if not read_ids:
        return
    db = connect.connect()
    cursor = db.cursor()
    cursor.executemany(
             READPOSTS_UPDATE_QUERY,
             [(user, id) for id in read_ids])
    cursor.close()
    db.commit()


def mark_as_unread(user, id):
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(READPOSTS_UNREAD_QUERY, (user, id))
    cursor.close()
    db.commit()


def get_read_post_ids(user):
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(READPOSTS_QUERY, (user,))
    for row in cursor.fetchall():
        yield(row[0])
    cursor.close()


def getPosts(include_closed=False):
    '''
    gets all active rows from a forum table
    '''
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(PARENTS_QUERY)
    db.commit()
    cursor.execute(QUERY % ("" if include_closed else 'where forum.open'))
    rows = cursor.fetchall()
    cursor.close()

    retarg = []
    update = False
    for row in rows:
        newpost = ForumPost()
        newpost.ix = row[0]
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

    return retarg


if __name__ == "__main__":
    forumposts = getPosts()
    for post_ in forumposts:
        print(post_.parent_ix, post_.ix, post_.topic)
