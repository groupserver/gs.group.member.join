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
from email.utils import parseaddr
from logging import getLogger
log = getLogger('gs.group.member.join.listcommand')
from zope.component import createObject
from zope.cachedescriptors.property import Lazy
from gs.core import to_id
from gs.group.list.command import CommandResult, CommandABC
from gs.group.member.base import user_member_of_group
from Products.GSProfile.utils import create_user_from_email
from .notify import ConfirmationNotifier
from .queries import ConfirmationQuery
from .utils import join


class SubscribeCommand(CommandABC):
    'The ``subscribe`` command.'

    @Lazy
    def groupInfo(self):
        retval = createObject('groupserver.GroupInfo', self.group)
        return retval

    @staticmethod
    def get_addr(email):
        retval = parseaddr(email['From'])[1]
        return retval

    @Lazy
    def query(self):
        retval = ConfirmationQuery()
        return retval

    def get_userInfo(self, addr):
        'Get the userInfo from the ``From`` in the email message'
        retval = None
        sr = self.group.site_root()
        u = sr.acl_users.get_userByEmail(addr)
        if u:
            retval = createObject('groupserver.UserFromId', self.group,
                                  u.getId())
        return retval

    def process(self, email, request):
        'Process the email command ``subscribe``'
        addr = self.get_addr(email)
        userInfo = self.get_userInfo(addr)
        if userInfo and user_member_of_group(userInfo, self.group):
            # We are dealing with an existing user.
            retval = CommandResult.notACommand
            m = 'Ignorning the "subscribe" command from {user.name} '\
                '({user.id}) <{addr}> because the person is already a '\
                'member of {group.name} ({group.id}) on {site.name} '\
                '({site.id}).'
            msg = m.format(user=userInfo, addr=addr, group=self.groupInfo,
                           site=self.groupInfo.siteInfo)
            log.info(msg)
        else:  # Not a member of the group, one way or the other.
            if not userInfo:
                userInfo = self.create_user(email['From'])
            # Generate the confirmation ID
            confirmationId = self.generate_confirmation_id(email)
            self.query.add_confirmation(
                addr, confirmationId, userInfo.id, self.groupInfo.id,
                self.groupInfo.siteInfo.id)
            # Send the notification
            notifier = ConfirmationNotifier(self.group, request)
            notifier.notify(userInfo, confirmationId)
            retval = CommandResult.commandStop
        return retval

    def create_user(self, fromHeader):
        'Create a user from the From header, setting the ``fn``.'
        emailLHS, addr = parseaddr(fromHeader)
        user = create_user_from_email(self.group, addr)
        fn = emailLHS if emailLHS else addr.split('@')[0]
        user.manage_changeProperty('fn', fn)
        retval = createObject('groupserver.UserFromId',
                              self.group, user.id)
        assert retval, 'Could not create a user info '\
                       'from {0}'.format(fromHeader)
        return retval

    def generate_confirmation_id(self, email):
        id22 = to_id(str(email) + self.groupInfo.name + self.groupInfo.id)
        retval = id22[:6]
        return retval


class ConfirmCommand(CommandABC):
    'The ``confirm subscription`` command.'

    @staticmethod
    def get_addr(email):
        retval = parseaddr(email['From'])[1]
        return retval

    @Lazy
    def query(self):
        retval = ConfirmationQuery()
        return retval

    def process(self, email, request):
        'Process the subscription confirmation'
        addr = self.get_addr(email)
        idComponents = [idc for idc in self.get_command_components(email)
                        if idc[:3] == 'ID-']
        if idComponents:
            confirmationId = idComponents[0].split('-')[0]
            confirmationInfo = self.query.get_confirmation(addr,
                                                           confirmationId)
            if confirmationInfo and (confirmationInfo['email'] == addr):
                userInfo = createObject('groupserver.UserFromId',
                                        self.group,
                                        confirmationInfo['userId'])
                groupInfo = createObject('groupserver.GroupInfo',
                                         self.group)
                join(self.group, request, userInfo, groupInfo)
                self.query.clear_confirmations(userInfo.id, groupInfo.id)
                retval = CommandResult.commandStop
            else:
                retval = CommandResult.notACommand
        else:
            m = 'No confirmation ID found in command from <{addr}>: '\
                '{subject}'
            msg = m.format(addr=addr, subject=email['Subject'])
            log.info(msg)
            retval = CommandResult.notACommand
        return retval
