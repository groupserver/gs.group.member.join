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
from __future__ import unicode_literals
from zope.i18n import translate
from gs.content.email.base import (NotifierABC, GroupNotifierABC,
                                   AnonymousNotifierABC)
from gs.email import send_email
from gs.profile.email.base.emailuser import EmailUser
from gs.profile.notify import MessageSender
from . import GSMessageFactory as _
UTF8 = 'utf-8'


class NotifyNewMember(GroupNotifierABC):
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


# And the equivilent class for telling the admin

class NotifyAdmin(GroupNotifierABC):
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
        ms.send_message(translatedSubject, text, html)
        self.reset_content_type()


# The email asking someone to confirm they want to be in a group.


class ConfirmationNotifier(GroupNotifierABC):
    textTemplateName = 'gs-group-member-join-confirm.txt'
    htmlTemplateName = 'gs-group-member-join-confirm.html'

    def notify(self, userInfo, confirmationId):
        subject = _('confirm-subject',
                    'Confirm you want to join ${groupName} (action '
                    'required) ID-${confirmationId}',
                    mapping={'groupName': self.groupInfo.name,
                             'confirmationId': confirmationId})
        translatedSubject = translate(subject)
        emailUser = EmailUser(userInfo.user, userInfo)
        text = self.textTemplate(userInfo=userInfo, userEmail=emailUser)
        html = self.htmlTemplate(userInfo=userInfo, userEmail=emailUser)
        ms = MessageSender(self.context, userInfo)
        ms.send_message(translatedSubject, text, html)
        self.reset_content_type()


# The email telling someone that they cannot be in the group


class NotifyCannotJoin(AnonymousNotifierABC):
    textTemplateName = 'gs-group-member-join-refuse.txt'
    htmlTemplateName = 'gs-group-member-join-refuse.html'

    def notify(self, addr, groupInfo):
        subject = _('refuse-subject',
                    'Cannot join ${groupName}',
                    mapping={'groupName': self.groupInfo.nam})
        translatedSubject = translate(subject)
        text = self.textTemplate(emailAddress=addr, groupInfo=groupInfo)
        html = self.htmlTemplate(emailAddress=addr, groupInfo=groupInfo)

        fromAddr = self.fromAddr(groupInfo.siteInfo)
        message = self.create_message(addr, fromAddr, translatedSubject,
                                      text, html)
        send_email(groupInfo.siteInfo.get_support_email(), addr, message)
        self.reset_content_type()


# The email telling the member that he or she has already confirmed


class NotifyConfirmed(NotifierABC):
    textTemplateName = 'gs-group-member-join-confirmed.txt'
    htmlTemplateName = 'gs-group-member-join-confirmed.html'

    def notify(self, userInfo, groupInfo):
        subject = _('confirmed-subject',
                    'Already joined ${groupName}',
                    mapping={'groupName': self.groupInfo.nam})
        translatedSubject = translate(subject)
        text = self.textTemplate(groupInfo=groupInfo)
        html = self.htmlTemplate(groupInfo=groupInfo)

        ms = MessageSender(self.context, userInfo)
        ms.send_message(translatedSubject, text, html)
        self.reset_content_type()
