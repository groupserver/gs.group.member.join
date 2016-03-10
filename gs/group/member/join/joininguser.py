# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2010, 2011, 2012, 2013, 2014 OnlineGroups.net and
# Contributors.
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
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from zope.event import notify
from gs.group.member.base import member_id, user_division_admin_of_group
from gs.profile.notify.interfaces import IGSNotifyUser
from .audit import JoinAuditor, JOIN_GROUP, MODERATED
from .event import GSJoinGroupEvent


class JoiningUser(object):
    '''An adapter for a :class:`IGSUserInfo` to create a user that can join
groups.

:param userInfo: The user that will join the groups:
:type userInfo: :class:`Products.CustomUser.interfaces.IGSUserInfo`'''
    def __init__(self, userInfo):
        self.userInfo = userInfo
        self.context = userInfo.user

    @Lazy
    def joinableGroups(self):
        'The list of groups that can be joined by a user.'
        groupsInfo = createObject('groupserver.GroupsInfo',
                                  self.context)
        u = self.userInfo.user
        # TODO: --=mpj17=-- This is a silly way to do this. Really,
        #   there should be a simple way of asking a group if it is
        #   joinable by a user.
        retval = groupsInfo.get_joinable_group_ids_for_user(u)
        assert type(retval) == list
        return retval

    def join(self, groupInfo):
        auditor = JoinAuditor(self.context, groupInfo, self.userInfo)
        # The user only gets a welcome message for joining a group,
        #    not for joining a site
        #    <https://projects.iopen.net/groupserver/ticket/346>
        self.join_group(groupInfo, auditor)
        self.send_welcome(groupInfo)
        self.set_moderation(groupInfo, auditor)
        self.tell_admin(groupInfo)
        notify(GSJoinGroupEvent(self.context, groupInfo, self.userInfo))

    def silent_join(self, groupInfo):
        '''Join a group, without sending any notifications out.

:param groupInfo: The group to join.
:type groupInfo: :class:`Products.GSGroup.interface.IGSGroupInfo`

The user will become a **member** of the group, and the new member will be
added to the list of **moderated** members if necessary. Notifications
should be sent by the user-interfaces that start the joining.

In addition an event that implements the
:class:`gs.group.member.join.event.IGSJoinGroupEvent` interface will be
raised at the end of joining. Code that wish to **extend** joining should
listen for that event.

:TODO: Move moderation out of this product.'''
        auditor = JoinAuditor(self.context, groupInfo, self.userInfo)
        self.join_group(groupInfo, auditor)
        self.set_moderation(groupInfo, auditor)
        notify(GSJoinGroupEvent(self.context, groupInfo, self.userInfo))

    def join_group(self, groupInfo, auditor):
        # Beware of regressions
        #   <https://projects.iopen.net/groupserver/ticket/303>
        self.join_member_group(member_id(groupInfo.id))
        auditor.info(JOIN_GROUP)

    @Lazy
    def acl_users(self):
        site_root = self.userInfo.user.site_root()
        retval = getattr(site_root, 'acl_users')
        assert retval, 'ACL Users not found in site_root'
        return retval

    def join_member_group(self, member_group_id):
        groupNames = self.acl_users.getGroupNames()
        if member_group_id not in groupNames:
            m = 'Unknown user-group: %s not in %s' % (member_group_id, groupNames)
            raise ValueError(m)
        self.acl_users.addGroupsToUser([member_group_id], self.userInfo.id)

    def send_welcome(self, groupInfo):
        # TODO: <https://projects.iopen.net/groupserver/ticket/414>
        notifiedUser = IGSNotifyUser(self.userInfo)
        mailingList = createObject('groupserver.MailingListInfo',
                                   self.context, groupInfo.id)
        ptnCoachId = groupInfo.get_property('ptn_coach_id', '')
        ptnCoach = createObject('groupserver.UserFromId',
                                self.context, ptnCoachId)
        n_dict = {
            'groupId': groupInfo.id,
            'groupName': groupInfo.name,
            'siteId': groupInfo.siteInfo.id,
            'siteName': groupInfo.siteInfo.name,
            'canonical': groupInfo.siteInfo.url,
            'grp_email': mailingList.get_property('mailto'),
            'ptnCoachId': groupInfo.get_property('ptn_coach_id', ''),
            'ptnCoach': ptnCoach.name,
            'realLife': groupInfo.get_property('real_life_group', ''),
            'supportEmail': groupInfo.siteInfo.get_support_email(), }
        notifiedUser.send_notification('add_group',
                                       member_id(groupInfo.id), n_dict)

    def set_moderation(self, groupInfo, auditor):
        # TODO: Move to an event-handler. It can react to groups that
        #       have a Moderated Group marker interface.
        # This is tricky:
        #     <https://projects.iopen.net/groupserver/ticket/235>
        mailingList = createObject('groupserver.MailingListInfo', self.context, groupInfo.id)
        isDivisionAdmin = user_division_admin_of_group(self.userInfo, groupInfo)
        if (mailingList.is_moderated and not(isDivisionAdmin) and mailingList.is_moderate_new):
            self.moderate_member(self.userInfo, mailingList, groupInfo, auditor)

    @staticmethod
    def moderate_member(userInfo, mailingList, groupInfo, auditor):
            # TODO: Move this code out into a utility that can be called by manage members
            mList = mailingList.mlist
            moderatedIds = [m.id for m in mailingList.moderatees]
            if userInfo.id in moderatedIds:
                m = '%s was marked for moderation in %s (%s), but is already moderated.'
                msg = m % (userInfo.id, groupInfo.name, groupInfo.id)
                raise ValueError(msg)
            moderatedIds.append(userInfo.id)
            if mList.hasProperty('moderated_members'):
                mList.manage_changeProperties(moderated_members=moderatedIds)
            else:
                mList.manage_addProperty('moderated_members', moderatedIds, 'lines')
            auditor.info(MODERATED)

    def tell_admin(self, groupInfo):
        #  <https://projects.iopen.net/groupserver/ticket/410>
        for admin in groupInfo.group_admins:
            notifiedUser = IGSNotifyUser(admin)
            n_dict = {
                'groupId': groupInfo.id,
                'groupName': groupInfo.name,
                'groupUrl': groupInfo.url,
                'siteName': groupInfo.siteInfo.name,
                'canonical': groupInfo.siteInfo.url,
                'supportEmail': groupInfo.siteInfo.get_support_email(),
                'memberId': self.userInfo.id,
                'memberName': self.userInfo.name,
                'memberUrl': self.userInfo.url,
                'joining_user': self.userInfo.user,
                'joining_group': groupInfo.groupObj,
            }
            notifiedUser.send_notification('join_group_admin', groupInfo.id,
                                           n_dict)
