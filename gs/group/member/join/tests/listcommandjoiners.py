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
from mock import patch
from unittest import TestCase
from gs.group.member.join.listcommandjoiners import (
    OddJoiner, SecretJoiner, PrivateJoiner, PublicToSiteMemberJoiner,
    CannotJoin)
import gs.group.member.join.listcommandjoiners  # lint:ok
from .faux import FauxVisibility, FauxUserInfo


class FailJoinerTest(TestCase):
    '''Test the joiners that always prevent joining.'''
    def assertFailJoin(self, j, m=''):
        u = FauxUserInfo()
        with self.assertRaises(CannotJoin) as e:
            j.join(u, 'person@example.com', None)
        if m:
            msg = str(e.exception)
            self.assertIn(m, msg)

    def test_odd_join_fail(self):
        'Test that we always fail at joining an odd group'
        j = OddJoiner(FauxVisibility())
        self.assertFailJoin(j, 'odd-group-cannot-join')

    def test_secret_join_fail(self):
        'Test that we always fail at joining a secret group'
        j = SecretJoiner(FauxVisibility())
        self.assertFailJoin(j, 'secret-group-cannot-join')

    def test_private_join_fail(self):
        'Test that we always fail at joining a secret group'
        j = PrivateJoiner(FauxVisibility())
        self.assertFailJoin(j, 'private-group-cannot-join')


class SuccessJoinerTest(TestCase):
    '''Test the joiners that can succeed'''
    def test_ptsm_join_anon(self):
        'Ensure Anonymous cannot join a Public To Site Member site'
        j = PublicToSiteMemberJoiner(FauxVisibility())
        with self.assertRaises(CannotJoin) as e:
            j.join(None, 'person@example.com', None)
        self.assertIn('public-site-group-cannot-join', str(e.exception))

    @patch('gs.group.member.join.listcommandjoiners.user_member_of_site')
    def test_ptsm_join_not_site_member(self, umos):
        'Ensure that people that are not site members are blocked'
        j = PublicToSiteMemberJoiner(FauxVisibility())
        u = FauxUserInfo()
        umos.return_value = False
        with self.assertRaises(CannotJoin) as e:
            j.join(u, 'person@example.com', None)
        self.assertIn('public-site-group-cannot-join', str(e.exception))
