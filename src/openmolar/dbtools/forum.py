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

headers = [_("Subject"), _("From"), _("To"), _("Date"), _("Message"), ]

QUERY = '''select ix, ancestor, topic, inits, fdate, recipient, comment,
important_id from forum left join
(select max(parent_id) as ancestor, child_id from forum join forum_parents
on ix=parent_id %s group by child_id) t on ix=t.child_id
left join (select important_id from forum_important where op=%%s) t1
on important_id = ix %s order by ix, ancestor'''

READPOSTS_QUERY = "select id from forumread where op=%s"

READPOSTS_UNREAD_QUERY = "delete from forumread where op=%s and id=%s"

READPOSTS_UPDATE_QUERY = '''insert into forumread (op, id, readdate)
values (%s, %s, NOW())'''

UNREAD_POSTS_QUERY = '''select count(*) from forum where open and ix not in
(select id from forumread where op=%s)'''

INSERT_QUERY = '''
insert into forum (inits, recipient, fdate, topic, comment)
VALUES (%s, %s, NOW(), %s, %s)'''

ORPHANED_POST_QUERY = 'delete from forum_parents where child_id = %s'

INSERT_PARENT_QUERY = \
    'insert into forum_parents (child_id, parent_id) values (%s, %s)'

ANCESTORS_QUERY = '''
insert ignore into forum_parents (child_id, parent_id)
(select t1.child_id, t2.parent_id from forum_parents t1 join forum_parents t2
on t1.parent_id=t2.child_id where t1.child_id = %s)'''

MAKE_IMPORTANT_QUERY = '''
INSERT INTO forum_important (op, important_id) values (%s, %s)'''

REMOVE_IMPORTANT_QUERY = '''
DELETE from forum_important where important_id=%s and op=%s'''

class ForumPost(object):
    ix = None
    parent_ix = None
    inits = ""
    recipient = None
    date = None
    topic = ""
    comment = ""
    open = True
    important = False

    def __repr__(self):
        return "ForumPost ix=%s ancestor=%s topic=%s" % (
            self.ix, self.parent_ix, self.topic)

    @property
    def briefcomment(self):
        bc = self.comment[:20].replace("\n", " ")
        return bc if bc == self.comment else "%s...." % bc


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
    values = (post.inits, post.recipient, post.topic, post.comment)
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(INSERT_QUERY, values)
    ix = db.insert_id()
    if post.parent_ix:
        # make the forum_parent table aware of ALL ancestors
        # in case a reply from the middle of the thread is deleted.
        cursor.execute(INSERT_PARENT_QUERY, (ix, post.parent_ix))
        cursor.execute(ANCESTORS_QUERY, (ix,))
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


def setParent(child_id, new_parent_ix):
    LOGGER.debug("setParent %s %s", child_id, new_parent_ix)
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(ORPHANED_POST_QUERY, (child_id,))
    cursor.execute(INSERT_PARENT_QUERY, (child_id, new_parent_ix))
    cursor.execute(ANCESTORS_QUERY, (child_id,))
    db.commit()
    cursor.close()


def update_forum_read(user, read_ids):
    if not read_ids:
        return
    db = connect.connect()
    cursor = db.cursor()
    cursor.executemany(READPOSTS_UPDATE_QUERY,
                       [(user, id_) for id_ in read_ids])
    cursor.close()
    db.commit()


def mark_as_unread(user, id):
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(READPOSTS_UNREAD_QUERY, (user, id))
    cursor.close()
    db.commit()


def update_important_posts(user, important_posts_dict):
    new_important_values = [(user, ix)
        for ix, important in important_posts_dict.items() if important]
    new_non_important_values = [(ix, user)
        for ix, important in important_posts_dict.items() if not important]
    db = connect.connect()
    cursor = db.cursor()
    cursor.executemany(MAKE_IMPORTANT_QUERY, new_important_values)
    cursor.executemany(REMOVE_IMPORTANT_QUERY, new_non_important_values)
    cursor.close()
    db.commit()


def get_read_post_ids(user):
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(READPOSTS_QUERY, (user,))
    for row in cursor.fetchall():
        yield(row[0])
    cursor.close()


def getPosts(user, include_closed=False):
    '''
    gets all active rows from a forum table
    '''
    query = QUERY % (("", "") if include_closed else ('AND open', 'WHERE open'))
    db = connect.connect()
    cursor = db.cursor()
    cursor.execute(query, (user,))
    rows = cursor.fetchall()
    cursor.close()

    retarg = []
    update = False
    for row in rows:
        newpost = ForumPost()
        newpost.ix = row[0]
        newpost.parent_ix = row[1] if row[1] is not None else row[0]
        newpost.topic = row[2]
        newpost.inits = row[3]
        newpost.date = row[4]
        newpost.recipient = row[5]
        newpost.comment = row[6]
        newpost.important = row[7] is not None
        retarg.append(newpost)

    return retarg


if __name__ == "__main__":
    forumposts = getPosts("NW")
    for post_ in forumposts:
        print(post_.parent_ix, post_.ix, post_.topic, post_.important)
