# -*- coding: utf-8 -*-
##############################################################################
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
##############################################################################
from __future__ import unicode_literals
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
        msg = 'Hi!\n\nI am a member of the group %s\n    %s\nand...' % \
            (self.groupInfo.name, self.groupInfo.url)
        sub = quote('Group Welcome')
        retval = 'mailto:%s?Subject=%s&body=%s' % \
            (self.siteInfo.get_support_email(), sub, quote(msg.encode(UTF8)))
        return retval


class NotifyMemberMessageText(NotifyMemberMessage, TextMixin):
    def __init__(self, context, request):
        NotifyMemberMessage.__init__(self, context, request)
        filename = 'welcome-to-%s.txt' % self.groupInfo.id
        self.set_header(filename)

# And the equivilent message that is sent to the administrators.


class NotifyAdminMessage(GroupEmail):
    @Lazy
    def userEmailInfo(self):
        # possibly this should be called something like testUserEmailInfo,
        # because it is really only used in the test case
        #
        # wpb: Not true. E-Democracy uses userEmailInfo to allow forum managers
        # to contact/introduct new members.
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
        m = 'Hi!\n\nI am an administrator of the group {0}\n    {1}\nand...'
        msg = m.format(self.groupInfo.name, self.groupInfo.url)
        sub = quote('New Member')
        retval = 'mailto:%s?Subject=%s&body=%s' % \
            (self.siteInfo.get_support_email(), sub, quote(msg.encode(UTF8)))
        return retval


class NotifyAdminMessageText(NotifyMemberMessage, TextMixin):
    def __init__(self, context, request):
        NotifyMemberMessage.__init__(self, context, request)
        filename = 'new-member-%s.txt' % self.groupInfo.id
        self.set_header(filename)
