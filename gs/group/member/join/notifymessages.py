# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2013, 2014 OnlineGroups.net and Contributors.
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
from urllib import quote
from zope.cachedescriptors.property import Lazy
from gs.content.email.base import GroupEmail, TextMixin
from Products.GSGroup.interfaces import IGSMailingListInfo
from gs.profile.email.base.emailuser import EmailUser
UTF8 = 'utf-8'


class NotifyMemberMessage(GroupEmail):
    @Lazy
    def userEmailInfo(self):
        # possibly this should be called something like testUserEmailInfo,
        # because it is really only used in the test case
        userInfo = self.loggedInUserInfo
        emailUser = EmailUser(userInfo.user, userInfo)
        return emailUser

    @Lazy
    def email(self):
        l = IGSMailingListInfo(self.groupInfo.groupObj)
        retval = l.get_property('mailto')
        return retval

    @Lazy
    def supportEmail(self):
        subject = quote('Group Welcome')
        m = 'Hello,\n\nI received a Welcome message for the group '\
            '{group.name}\n    {group.url}\nand...'
        msg = m.format(group=self.groupInfo)
        body = quote(msg.encode(UTF8))
        retval = 'mailto:%s?Subject=%s&body=%s' % \
            (self.siteInfo.get_support_email(), subject, body)
        return retval


class NotifyMemberMessageText(NotifyMemberMessage, TextMixin):
    def __init__(self, context, request):
        super(NotifyMemberMessageText, self).__init__(context, request)
        filename = 'welcome-to-%s.txt' % self.groupInfo.id
        self.set_header(filename)


# And the equivilent message that is sent to the administrators.


class NotifyAdminMessage(GroupEmail):
    @Lazy
    def userEmailInfo(self):
        # Used by some (E-Democracy.org) to allow group administrators to
        # contact or introduce new members.
        userInfo = self.loggedInUserInfo
        emailUser = EmailUser(userInfo.user, userInfo)
        return emailUser

    @Lazy
    def email(self):
        l = IGSMailingListInfo(self.groupInfo.groupObj)
        retval = l.get_property('mailto')
        return retval

    @Lazy
    def supportEmail(self):
        subject = quote('New Member')
        m = 'Hello,\n\nI am an administrator of the group '\
            '{group.name}\n    {group.url}\nand...'
        msg = m.format(group=self.groupInfo)
        body = quote(msg.encode(UTF8))
        retval = 'mailto:%s?Subject=%s&body=%s' % \
            (self.siteInfo.get_support_email(), subject, body)
        return retval


class NotifyAdminMessageText(NotifyMemberMessage, TextMixin):
    def __init__(self, context, request):
        super(NotifyAdminMessageText, self).__init__(context, request)
        filename = 'new-member-%s.txt' % self.groupInfo.id
        self.set_header(filename)


# And the Subscription Conform message


class ConfirmSubscription(GroupEmail):

    @Lazy
    def supportEmail(self):
        subject = quote('Confirm subscription')
        m = 'Hello,\n\nI received an email asking me to confirm '\
            'my subscription to\n{group.name}\n    {group.url}\nand...'
        msg = m.format(group=self.groupInfo)
        body = quote(msg.encode(UTF8))
        retval = 'mailto:%s?Subject=%s&body=%s' % \
            (self.siteInfo.get_support_email(), subject, body)
        return retval


class ConfirmSubscriptionText(ConfirmSubscription, TextMixin):
    def __init__(self, context, request):
        super(ConfirmSubscriptionText, self).__init__(context, request)
        filename = 'confirm-%s.txt' % self.groupInfo.id
        self.set_header(filename)
