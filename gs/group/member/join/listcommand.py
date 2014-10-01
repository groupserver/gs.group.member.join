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
import shlex
from zope.component import createObject
from zope.cachedescriptors.property import Lazy
from gs.group.list.command import CommandResult, CommandABC
from gs.group.privacy.visibility import GroupVisibility
from .interfaces import IJoiner
from .listcommandjoiners import CannotJoin, GroupMember
from .notify import NotifyCannotJoin
from .queries import ConfirmationQuery
from .utils import join


class SubscribeCommand(CommandABC):
    'The ``subscribe`` command.'

    @Lazy
    def groupInfo(self):
        retval = createObject('groupserver.GroupInfo', self.group)
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
        addr = parseaddr(email['From'])[1]
        userInfo = self.get_userInfo(addr)
        groupVisibility = GroupVisibility(self.groupInfo)
        joiner = IJoiner(groupVisibility)
        try:
            joiner.join(userInfo, email, request)
            retval = CommandResult.commandStop
        except CannotJoin as cj:
            groupsFolder = self.groupInfo.groupObj.aq_parent
            notifier = NotifyCannotJoin(groupsFolder, request)
            notifier.notify(cj, addr, self.groupInfo)
            retval = CommandResult.commandStop
        except GroupMember:
            m = 'Ignorning the "subscribe" command from {user.name} '\
                '({user.id}) <{addr}> because the person is already a '\
                'member of {group.name} ({group.id}) on {site.name} '\
                '({site.id}).'
            msg = m.format(user=userInfo, addr=addr, group=self.groupInfo,
                           site=self.groupInfo.siteInfo)
            log.info(msg)
            retval = CommandResult.notACommand
        return retval


class ConfirmCommand(CommandABC):
    'The ``confirm subscription`` command.'

    @Lazy
    def query(self):
        retval = ConfirmationQuery()
        return retval

    @staticmethod
    def get_confirmation_id(email):
        '''Get the confirmation ID from the subject line of the email

:param email.message.Message email: The email to process.
:returns: The confirmation-identifier from the ``Subject`` if present,
          ``None`` otherwise.
:rtype: str'''
        # Use shlex.split rather than self.get_command_components because
        # it is important that we are case-preserving.
        idComponents = [idc for idc in shlex.split(email['Subject'])
                        if idc[:3] == 'ID-']
        retval = idComponents[0].split('-')[1] if idComponents else None
        return retval

    def process(self, email, request):
        'Process the subscription confirmation'
        addr = parseaddr(email['From'])[1]
        confirmationId = self.get_confirmation_id(email)
        if confirmationId:
            confirmationInfo = self.query.get_confirmation(
                addr, confirmationId)
            if confirmationInfo and (confirmationInfo['email'] == addr):
                self.join(confirmationInfo, request)
                retval = CommandResult.commandStop
            elif not confirmationInfo:
                # Found an "ID-" in the confirmation-email, but no matching
                # confirmation ID in the database.
                m = 'No confirmation information found in command from '\
                    '<{addr}>: {subject}'
                msg = m.format(addr=addr, subject=email['Subject'])
                log.info(msg)
                # TODO: notification
                retval = CommandResult.commandStop
            else:  # confirmationInfo['email'] != addr
                m = 'Email address <{addr}> does not match that in the '\
                    'confirmation info <{confirmationAddr}>: {subject}'
                msg = m.format(addr=addr,
                               confirmationAddr=confirmationInfo['email'],
                               subject=email['Subject'])
                log.info(msg)
                # TODO: notification
                retval = CommandResult.commandStop
        else:
            # Assume it is a normal email.
            m = 'No confirmation ID found in command from <{addr}>: '\
                '{subject}'
            msg = m.format(addr=addr, subject=email['Subject'])
            log.info(msg)
            retval = CommandResult.notACommand
        return retval

    def join(self, confirmationInfo, request):
        # Because the email comes into Support we may be on a totally
        # different site. Get the correct site as the context.
        siteRoot = self.group.site_root()
        site = getattr(siteRoot.Content, confirmationInfo['siteId'])
        # Get the user and group with the right context.
        userInfo = createObject('groupserver.UserFromId', site,
                                confirmationInfo['userId'])
        groupInfo = createObject('groupserver.GroupInfo', site,
                                 confirmationInfo['groupId'])
        # Member check?
        join(groupInfo.groupObj, request, userInfo, groupInfo)
        self.query.clear_confirmations(userInfo.id, groupInfo.id)
