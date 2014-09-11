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
from .interfaces import IGSJoiningUser
from .notify import NotifyNewMember, NotifyAdmin


def join(context, request, userInfo, groupInfo):
    joiningUser = IGSJoiningUser(userInfo)
    joiningUser.silent_join(groupInfo)
    notifier = NotifyNewMember(context, request)
    notifier.notify(userInfo)

    notifier = NotifyAdmin(context, request)
    for adminInfo in groupInfo.group_admins:
        notifier.notify(adminInfo, userInfo)
