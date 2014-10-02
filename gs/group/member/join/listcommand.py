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
from gs.group.member.base import user_member_of_group
from gs.group.privacy.visibility import GroupVisibility
from gs.profile.email.base import EmailUser
from gs.profile.email.verify import EmailVerificationUser
from .audit import (JoinAuditor, CONFIRM)
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
                try:
                    self.join(confirmationInfo, request)
                except GroupMember:
                    # TODO: Already a member notification
                    pass
                retval = CommandResult.commandStop
            elif not confirmationInfo:
                # Found an "ID-" in the confirmation-email, but no matching
                # confirmation ID in the database.
                m = 'No confirmation information found in command from '\
                    '<{addr}>: {subject}'
                msg = m.format(addr=addr, subject=email['Subject'])
                log.info(msg)
                # TODO: Cannot confirm notification
                retval = CommandResult.commandStop
            else:  # confirmationInfo['email'] != addr
                m = 'Email address <{addr}> does not match that in the '\
                    'confirmation info <{confirmationAddr}>: {subject}'
                msg = m.format(addr=addr,
                               confirmationAddr=confirmationInfo['email'],
                               subject=email['Subject'])
                log.info(msg)
                # TODO: Cannot confirm notification
                retval = CommandResult.commandStop
        else:
            # Assume it is a normal email.
            m = 'No confirmation ID found in command from <{addr}>: '\
                '{subject}'
            msg = m.format(addr=addr, subject=email['Subject'])
            log.info(msg)
            retval = CommandResult.notACommand
        return retval

    def verify_address(self, userInfo, addr):
        # TODO: Now the Add code and this code does this. Cut 'n' paste
        #       software engineereing for now, but the verification code
        #       should provide this as a utility.
        eu = EmailUser(self.context, userInfo)
        if not eu.is_address_verified(addr):
            evu = EmailVerificationUser(self.context, userInfo, addr)
            verificationId = evu.create_verification_id()
            evu.add_verification_id(verificationId)
            evu.verify_email(verificationId)

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

        if user_member_of_group(userInfo, groupInfo):
            raise GroupMember('Already a member of the group')

        auditor = JoinAuditor(site, groupInfo, userInfo)
        auditor.info(CONFIRM)

        self.verify_address(userInfo, confirmationInfo['email'])

        join(groupInfo.groupObj, request, userInfo, groupInfo)
        self.query.clear_confirmations(userInfo.id, groupInfo.id)
