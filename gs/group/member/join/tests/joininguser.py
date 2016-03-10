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
