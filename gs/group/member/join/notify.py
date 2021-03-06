# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2013, 2014, 2016 OnlineGroups.net and Contributors.
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
from __future__ import unicode_literals, absolute_import, print_function
from logging import getLogger
from zope.i18n import translate
from gs.content.email.base import (GroupNotifierABC)
from gs.profile.email.base.emailuser import EmailUser
from gs.profile.notify import MessageSender
from . import GSMessageFactory as _

#: The logger for warnings
log = getLogger('gs.group.member.join.notify')


class NotifyNewMember(GroupNotifierABC):
    '''The "Welcome" notification'''
    textTemplateName = 'new-member-msg.txt'
    htmlTemplateName = 'new-member-msg.html'

    def notify(self, userInfo):
        subject = _('welcome-subject', 'Welcome to ${groupName}',
                    mapping={'groupName': self.groupInfo.name})
        translatedSubject = translate(subject)
        emailUser = EmailUser(userInfo.user, userInfo)
        text = self.textTemplate(userInfo=userInfo, userEmail=emailUser)
        html = self.htmlTemplate(userInfo=userInfo, userEmail=emailUser)
        ms = MessageSender(self.context, userInfo)
        ms.send_message(translatedSubject, text, html)
        self.reset_content_type()


class NotifyAdmin(GroupNotifierABC):
    'The notification telling the admin about the new member'
    textTemplateName = 'new-member-admin-msg.txt'
    htmlTemplateName = 'new-member-admin-msg.html'

    def notify(self, adminInfo, userInfo):
        subject = _('new-member-subject',
                    '${userName} has joined ${groupName}',
                    mapping={'userName': userInfo.name,
                             'groupName': self.groupInfo.name})
        translatedSubject = translate(subject)
        emailUser = EmailUser(userInfo.user, userInfo)
        text = self.textTemplate(adminInfo=adminInfo, userInfo=userInfo,
                                 userEmail=emailUser)
        html = self.htmlTemplate(adminInfo=adminInfo, userInfo=userInfo,
                                 userEmail=emailUser)
        ms = MessageSender(self.context, adminInfo)
        try:
            ms.send_message(translatedSubject, text, html)
        except ValueError:
            m = 'Could not send a "New member" notification to %s (%s) in the group %s (%s) on '\
                '%s (%s) because they lack a verified email address. Skipping the notification.'
            log.warn(m, adminInfo.name, adminInfo.id, self.groupInfo.name, self.groupInfo.id,
                     self.groupInfo.siteInfo.name, self.groupInfo.siteInfo.id)
        self.reset_content_type()
