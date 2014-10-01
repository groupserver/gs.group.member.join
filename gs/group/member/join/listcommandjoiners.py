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
from abc import ABCMeta, abstractmethod
from email.utils import parseaddr
from zope.cachedescriptors.property import Lazy
from zope.component import createObject, adapter
from zope.interface import implementer
from gs.core import to_id
from gs.group.member.base import user_member_of_site
from gs.group.privacy.interfaces import (IPublic, IPublicToSiteMember,
                                         IPrivate, ISecret, IOdd)
from Products.GSProfile.utils import create_user_from_email
from .interfaces import IJoiner
from .notify import ConfirmationNotifier
from .queries import ConfirmationQuery


class CannotJoin(Exception):
    '''Raised when a person cannot join the group'''


class Joiner(object):
    __metaclass__ = ABCMeta

    def __init__(self, groupVisibility):
        self.groupInfo = groupVisibility.groupInfo

    @abstractmethod
    def join(self, userInfo, email, request):
        '''Join the person to the group.'''


@adapter(IPublic)
@implementer(IJoiner)
class PublicJoiner(Joiner):
    @Lazy
    def query(self):
        retval = ConfirmationQuery()
        return retval

    def join(self, userInfo, email, request):
        ui = userInfo if userInfo else self.create_user(email['From'])
        addr = parseaddr(email['From'])[1]
        self.send_confirmation(email, addr, ui, request)

    def send_confirmation(self, email, addr, userInfo, request):
        # Generate the confirmation ID
        confirmationId = self.generate_confirmation_id(email)
        self.query.add_confirmation(
            addr, confirmationId, userInfo.id, self.groupInfo.id,
            self.groupInfo.siteInfo.id)
        # Send the notification
        notifier = ConfirmationNotifier(self.group, request)
        notifier.notify(userInfo, confirmationId)

    def create_user(self, fromHeader):
        'Create a user from the From header, setting the ``fn``.'
        emailLHS, addr = parseaddr(fromHeader)
        group = self.groupInfo.groupObj
        user = create_user_from_email(group, addr)
        fn = emailLHS if emailLHS else addr.split('@')[0]
        user.manage_changeProperty('fn', fn)
        retval = createObject('groupserver.UserFromId',
                              group, user.id)
        assert retval, 'Could not create a user info '\
                       'from {0}'.format(fromHeader)
        return retval

    def generate_confirmation_id(self, email):
        id22 = to_id(str(email) + self.groupInfo.name + self.groupInfo.id)
        retval = id22[:6]
        return retval


@adapter(IPublicToSiteMember)
@implementer(IJoiner)
class PublicToSiteMemberJoiner(PublicJoiner):
    @Lazy
    def query(self):
        retval = ConfirmationQuery()
        return retval

    def join(self, userInfo, email, request):
        siteInfo = self.groupInfo.siteInfo
        if ((not userInfo) or (not user_member_of_site(userInfo,
                                                       siteInfo))):
            m = 'Only members of {0} can join {1}'
            msg = m.format(siteInfo.name, self.groupInfo.name)
            raise CannotJoin(msg)
        addr = parseaddr(email['From'])[1]
        self.send_confirmation(email, addr, userInfo, request)


@adapter(IPrivate)
@implementer(IJoiner)
class PrivateJoiner(Joiner):
    def join(self, userInfo, email, request):
        m = 'Visit the page for {0} to request membership: {1}'
        msg = m.format(self.groupInfo.name, self.groupInfo.url)
        raise CannotJoin(msg)


@adapter(ISecret)
@implementer(IJoiner)
class SecretJoiner(Joiner):
    def join(self, userInfo, email, request):
        m = 'Only people that have been invited can join {0}'
        msg = m.format(self.groupInfo.name, self.groupInfo.url)
        raise CannotJoin(msg)


@adapter(IOdd)
@implementer(IJoiner)
class OddJoiner(Joiner):
    def join(self, userInfo, email, request):
        m = 'People cannot join {0}'
        msg = m.format(self.groupInfo.name, self.groupInfo.url)
        raise CannotJoin(msg)
