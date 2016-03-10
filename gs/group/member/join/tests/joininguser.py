# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2016 OnlineGroups.net and Contributors.
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
from __future__ import absolute_import, unicode_literals, print_function
from mock import (MagicMock, patch, PropertyMock)
from unittest import TestCase
from gs.group.member.join.joininguser import (JoiningUser, )


class TestJoiningUser(TestCase):

    @patch.object(JoiningUser, 'acl_users', new_callable=PropertyMock)
    def test_join_member_group_unknown_group(self, m_a_u):
        'Test joining an unknown group'
        m_a_u().getGroupNames.return_value = ['ethel_member', 'frog_member', ]

        j = JoiningUser(MagicMock())
        with self.assertRaises(ValueError):
            j.join_member_group('violence_member')

    @patch.object(JoiningUser, 'acl_users', new_callable=PropertyMock)
    def test_join_member_group(self, m_a_u):
        'Test joining a group'
        acl_users = m_a_u()
        acl_users.getGroupNames.return_value = ['ethel_member', 'frog_member', ]

        userInfo = MagicMock()
        userInfo.id = 'dinsdale'
        j = JoiningUser(userInfo)
        j.join_member_group('ethel_member')

        acl_users.addGroupsToUser.assert_called_once_with(['ethel_member', ], 'dinsdale')

    @patch('gs.group.member.join.joininguser.user_division_admin_of_group')
    @patch('gs.group.member.join.joininguser.createObject')
    @patch.object(JoiningUser, 'moderate_member')
    def test_set_moderation_site_admin(self, m_m_m, m_cO, m_u_d_a_o_g):
        'Ensure that site-administrators are not moderated'
        mailingList = m_cO()
        mailingList.is_moderated = True
        mailingList.is_moderate_new = True
        m_u_d_a_o_g.return_value = True

        userInfo = MagicMock()
        userInfo.id = 'dinsdale'
        j = JoiningUser(userInfo)
        j.set_moderation(MagicMock(), MagicMock())

        self.assertEqual(0, m_m_m.call_count)

    @patch('gs.group.member.join.joininguser.user_division_admin_of_group')
    @patch('gs.group.member.join.joininguser.createObject')
    @patch.object(JoiningUser, 'moderate_member')
    def test_set_moderation_moderate_new(self, m_m_m, m_cO, m_u_d_a_o_g):
        'Ensure that we moderate new members'
        mailingList = m_cO()
        mailingList.is_moderated = True
        mailingList.is_moderate_new = True
        m_u_d_a_o_g.return_value = False

        userInfo = MagicMock()
        userInfo.id = 'dinsdale'
        j = JoiningUser(userInfo)
        groupInfo = MagicMock()
        auditor = MagicMock()
        j.set_moderation(groupInfo, auditor)

        m_m_m.assert_called_once_with(userInfo, mailingList, groupInfo, auditor)

    @patch('gs.group.member.join.joininguser.user_division_admin_of_group')
    @patch('gs.group.member.join.joininguser.createObject')
    @patch.object(JoiningUser, 'moderate_member')
    def test_set_moderation_moderate_some(self, m_m_m, m_cO, m_u_d_a_o_g):
        'Ensure that we skip setting moderation if we only moderate some members'
        mailingList = m_cO()
        mailingList.is_moderated = True
        mailingList.is_moderate_new = False
        m_u_d_a_o_g.return_value = False

        userInfo = MagicMock()
        userInfo.id = 'dinsdale'
        j = JoiningUser(userInfo)
        groupInfo = MagicMock()
        auditor = MagicMock()
        j.set_moderation(groupInfo, auditor)

        self.assertEqual(0, m_m_m.call_count)

    @patch('gs.group.member.join.joininguser.user_division_admin_of_group')
    @patch('gs.group.member.join.joininguser.createObject')
    @patch.object(JoiningUser, 'moderate_member')
    def test_set_moderation_moderate_none(self, m_m_m, m_cO, m_u_d_a_o_g):
        'Ensure that we skip setting moderation if it is off'
        mailingList = m_cO()
        mailingList.is_moderated = False
        mailingList.is_moderate_new = True
        m_u_d_a_o_g.return_value = False

        userInfo = MagicMock()
        userInfo.id = 'dinsdale'
        j = JoiningUser(userInfo)
        groupInfo = MagicMock()
        auditor = MagicMock()
        j.set_moderation(groupInfo, auditor)

        self.assertEqual(0, m_m_m.call_count)
