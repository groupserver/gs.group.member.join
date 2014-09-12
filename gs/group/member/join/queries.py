# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2014 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################
import datetime
import pytz
import sqlalchemy as sa
from gs.database import getTable, getSession


class ConfirmationQuery(object):
    def __init__(self):
        self.confirmationTable = getTable('confirmation')

    def add_confirmation(self, email, confirmationId, userId, groupId,
                         siteId):
        d = {
            'email': email,
            'confirmation_id': confirmationId,
            'user_id': userId,
            'group_id': groupId,
            'site_id': siteId, }
        i = self.confirmationTable.insert()
        session = getSession()
        session.execute(i, params=d)

    def clear_confirmations(self, userId, groupId):
        ct = self.confirmationTable
        u = ct.update(sa.and_(ct.c.user_id == userId,
                              ct.c.group_id == groupId))

        now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        d = {'response_date': now}

        session = getSession()
        session.execute(u, params=d)

    def get_confirmation(self, email, confirmationId):
        ct = self.confirmationTable
        s = ct.select()
        s.append_whereclause(ct.c.email == email)
        s.append_whereclause(ct.c.confirmation_id == confirmationId)
        s.append_whereclause(ct.c.response_date == None)  # lint: ok
        session = getSession()
        r = session.execute(s).fetchone()
        retval = None
        if r:
            retval = {
                'email': r['email'],
                'confirmationId': r['confirmation_id'],
                'userId': r['user_id'],
                'groupId': r['group_id'],
                'siteId': r['site_id'], }
        return retval
