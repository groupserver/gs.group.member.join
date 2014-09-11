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
from zope.cachedescriptors.property import Lazy
from zope.i18n import translate
from gs.content.email.base import GroupEmail, TextMixin
from Products.GSGroup.interfaces import IGSMailingListInfo
from gs.profile.email.base.emailuser import EmailUser
from . import GSMessageFactory as _


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
        subject = _('support-message-group-welcome-subject',
                    'Group welcome')
        translatedSubject = translate(subject)
        body = _('support-message-group-welcome-body',
                 'Hello,\n\nI received a Welcome message for the group '
                 '${groupName}\n    ${groupUrl}\nand...',
                 mapping={'groupName': self.groupInfo.name,
                          'groupUrl': self.groupInfo.url})
        translatedBody = translate(body)
        retval = self.mailto(self.siteInfo.get_support_email(),
                             translatedSubject, translatedBody)
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
        subject = _('support-message-new-member-subject', 'New member')
        translatedSubject = translate(subject)
        body = _('support-message-new-member-body',
                 'Hello,\n\nI am an administrator of the group '
                 '${groupName} \n    ${groupUrl}\nand...',
                 mapping={'groupName': self.groupInfo.name,
                          'groupUrl': self.groupInfo.url})
        translatedBody = translate(body)
        retval = self.mailto(self.siteInfo.get_support_email(),
                             translatedSubject, translatedBody)
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
        subject = _('support-message-confirm-subscription-subject',
                    'Confirm subscription')
        translatedSubject = translate(subject)
        body = _('support-message-confirm-subscription-body',
                 'Hello,\n\nI received an email asking me to confirm '
                 'my subscription to\n${groupName}\n    '
                 '${groupUrl}\nand...',
                 mapping={'groupName': self.groupInfo.name,
                          'groupUrl': self.groupInfo.url})
        translatedBody = translate(body)
        retval = self.mailto(self.siteInfo.get_support_email(),
                             translatedSubject, translatedBody)
        return retval


class ConfirmSubscriptionText(ConfirmSubscription, TextMixin):
    def __init__(self, context, request):
        super(ConfirmSubscriptionText, self).__init__(context, request)
        filename = 'confirm-%s.txt' % self.groupInfo.id
        self.set_header(filename)
