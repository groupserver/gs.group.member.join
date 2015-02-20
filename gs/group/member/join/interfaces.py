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
from zope.interface import Interface
from zope.schema import Choice
from . import GSMessageFactory as _
from Products.GSProfile.interfaces import deliveryVocab


class IGSJoiningUser(Interface):

    def join(groupInfo):
        '''Join a group.

        Description
        ===========

        This method joins the user to the group, so the user becomes a
        member.

        Arguments
        =========

        `groupInfo`: The group to join.

        Returns
        =======

        None.

        Side Effects
        ============

        * The user becomes a member of the group.
        * The new member is sent a Welcome message
        * If not already a member of the site user-group, the user
          becomes a member of the site.
        * If required by the group, the new member becomes a moderated
          member of the group. Unless the new member is a administrator
          for the site, in which case the new member is *not* moderated.
        * The group administrators are email to tell them that a new
          member has joined.'''


class IGSJoinGroup(Interface):
    delivery = Choice(
        title=_('join-form-delivery-settings', 'Message delivery settings'),
        description=_('join-form-delivery-settings-help',
                      'Your message delivery settings.'),
        vocabulary=deliveryVocab,
        default='email')
