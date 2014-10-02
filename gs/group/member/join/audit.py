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
from __future__ import absolute_import, unicode_literals
from datetime import datetime
SUBSYSTEM = 'gs.group.member.join'
from logging import getLogger
log = getLogger(SUBSYSTEM)
from pytz import UTC
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from zope.component.interfaces import IFactory
from zope.interface import implementer, implementedBy
from Products.XWFCore.XWFUtils import munge_date
from Products.GSAuditTrail import IAuditEvent, BasicAuditEvent, AuditQuery
from Products.GSAuditTrail.utils import event_id_from_data


UNKNOWN = '0'  # Unknown is always "0"
JOIN_GROUP = '1'
JOIN_SITE = '2'
MODERATED = '3'


@implementer(IFactory)
class JoinAuditEventFactory(object):
    """A Factory for joining events."""
    title = 'GroupServer Joining Audit Event Factory'
    description = 'Creates a GroupServer event auditor for joining events'

    def __call__(self, context, event_id, code, date, userInfo,
                 instanceUserInfo, siteInfo, groupInfo, instanceDatum='',
                 supplementaryDatum='', subsystem=''):
        """Create an event"""
        if subsystem != SUBSYSTEM:
            raise ValueError('Subsystems do not match')

        if code == JOIN_GROUP:
            event = JoinEvent(context, event_id, date, instanceUserInfo,
                              siteInfo, groupInfo)
        elif code == JOIN_SITE:
            event = JoinSiteEvent(context, event_id, date,
                                  instanceUserInfo, siteInfo, groupInfo)
        elif code == MODERATED:
            event = ModerateEvent(context, event_id, date,
                                  instanceUserInfo, siteInfo, groupInfo)
        else:
            event = BasicAuditEvent(context, event_id, UNKNOWN, date,
                                    userInfo, instanceUserInfo, siteInfo,
                                    groupInfo, instanceDatum,
                                    supplementaryDatum, SUBSYSTEM)
        assert event
        return event

    def getInterfaces(self):
        return implementedBy(BasicAuditEvent)


@implementer(IAuditEvent)
class JoinEvent(BasicAuditEvent):
    ''' An audit-trail event representing a person joining a group.'''
    def __init__(self, context, eventId, d, instanceUserInfo, siteInfo,
                 groupInfo):
        """ Create a join event"""
        super(JoinEvent, self).__init__(
            context, eventId, JOIN_GROUP, d, None, instanceUserInfo,
            siteInfo,  groupInfo, None, None, SUBSYSTEM)

    def __unicode__(self):
        retval = '%s (%s) joined the group %s (%s) on %s (%s).' % \
            (self.instanceUserInfo.name, self.instanceUserInfo.id,
             self.groupInfo.name, self.groupInfo.id,
             self.siteInfo.name, self.siteInfo.id)
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event groupserver-group-member-join-%s' %\
            self.code
        retval = '<span class="%s">Joined %s</span>' % \
            (cssClass, self.groupInfo.name)

        retval = '%s (%s)' % (retval, munge_date(self.context, self.date))
        return retval


@implementer(IAuditEvent)
class JoinSiteEvent(BasicAuditEvent):
    ''' An audit-trail event representing a person joining a site.'''
    def __init__(self, context, eventId, d, instanceUserInfo,
                 siteInfo, groupInfo):
        """ Create a join event"""
        super(JoinSiteEvent, self).__init__(
            context, eventId,  JOIN_SITE,  d, None, instanceUserInfo,
            siteInfo, groupInfo, None, None, SUBSYSTEM)

    def __unicode__(self):
        retval = '%s (%s) joined the site %s (%s).' %\
            (self.instanceUserInfo.name, self.instanceUserInfo.id,
             self.siteInfo.name, self.siteInfo.id)
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event groupserver-group-member-join-%s' %\
            self.code
        retval = '<span class="%s">Joined %s</span>' %\
            (cssClass, self.siteInfo.name)

        retval = '%s (%s)' % (retval, munge_date(self.context, self.date))
        return retval


@implementer(IAuditEvent)
class ModerateEvent(BasicAuditEvent):
    ''' An audit-trail event representing a person being moderated
    when joining a group.'''
    def __init__(self, context, eventId, d, instanceUserInfo, siteInfo,
                 groupInfo):
        """ Create a join event
        """
        super(ModerateEvent, self).__init__(
            context, eventId,  MODERATED, d, None, instanceUserInfo,
            siteInfo, groupInfo, None, None, SUBSYSTEM)

    def __unicode__(self):
        retval = '%s (%s) will be moderated when posting to '\
            '%s (%s) on %s (%s).' %\
            (self.instanceUserInfo.name, self.instanceUserInfo.id,
             self.groupInfo.name, self.groupInfo.id,
             self.siteInfo.name, self.siteInfo.id)
        return retval

    @property
    def xhtml(self):
        cssClass = 'audit-event groupserver-group-member-join-%s' %\
            self.code
        retval = '<span class="%s">Being set to moderated %s</span>' %\
            (cssClass, self.groupInfo.name)

        retval = '%s (%s)' % (retval, munge_date(self.context, self.date))
        return retval


class JoinAuditor(object):
    """An auditor for joining a group."""
    def __init__(self, context, groupInfo, instanceUserInfo):
        """Create a status auditor."""
        self.context = context
        self.instanceUserInfo = instanceUserInfo
        self.groupInfo = groupInfo

    @Lazy
    def siteInfo(self):
        retval = createObject('groupserver.SiteInfo', self.context)
        return retval

    @Lazy
    def factory(self):
        retval = JoinAuditEventFactory()
        return retval

    @Lazy
    def queries(self):
        retval = AuditQuery()
        return retval

    def info(self, code, instanceDatum='', supplementaryDatum=''):
        """Log an info event to the audit trail.
            * Creates an ID for the new event,
            * Writes the instantiated event to the audit-table, and
            * Writes the event to the standard Python log."""
        d = datetime.now(UTC)
        eventId = event_id_from_data(
            self.instanceUserInfo, self.instanceUserInfo, self.siteInfo,
            code, instanceDatum,
            '%s-%s' % (self.groupInfo.name, self.groupInfo.id))

        e = self.factory(
            self.context, eventId,  code, d, self.instanceUserInfo,
            self.instanceUserInfo, self.siteInfo, self.groupInfo,
            instanceDatum, supplementaryDatum, SUBSYSTEM)

        self.queries.store(e)
        log.info(e)
        return e
