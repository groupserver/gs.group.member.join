# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2012, 2013, 2014 OnlineGroups.net and Contributors.
#
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
from zope.component.interfaces import ObjectEvent
from zope.component.interfaces import IObjectEvent
from zope.interface import Attribute, implementer


class IGSJoinGroupEvent(IObjectEvent):
    '''The event raised when someone joins a group.

:cvar groupInfo: Information about the group that was joined.
:type groupInfo: :class:`Products.GSGroup.interface.IGSGroupInfo`
:cvar userInfo: Information about the new member of the grop
:type userInfo: :class:`Products.CustomUser.interfaces.IGSUserInfo`'''
    groupInfo = Attribute('The group that is being joined')
    memberInfo = Attribute('The new group member')


@implementer(IGSJoinGroupEvent)
class GSJoinGroupEvent(ObjectEvent):
    '''The concrete implementation of :class:`IGSJoinGroupEvent`'''
    def __init__(self, context, groupInfo, memberInfo):
        super(GSJoinGroupEvent, self).__init__(context)
        self.groupInfo = groupInfo
        self.memberInfo = memberInfo
