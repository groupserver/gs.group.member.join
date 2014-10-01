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
from email.parser import Parser
from mock import patch
from unittest import TestCase
from gs.group.member.join.listcommandjoiners import (
    OddJoiner, SecretJoiner, PrivateJoiner, PublicToSiteMemberJoiner,
    PublicJoiner, CannotJoin, GroupMember)
import gs.group.member.join.listcommandjoiners  # lint:ok
from .faux import FauxVisibility, FauxUserInfo, faux_email


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
            j.join(None, faux_email(), None)
        self.assertIn('public-site-group-cannot-join', str(e.exception))

    @patch('gs.group.member.join.listcommandjoiners.user_member_of_site')
    def test_ptsm_join_not_site_member(self, umos):
        'Ensure that people that are not site members are blocked'
        j = PublicToSiteMemberJoiner(FauxVisibility())
        u = FauxUserInfo()
        umos.return_value = False
        with self.assertRaises(CannotJoin) as e:
            j.join(u, faux_email(), None)
        self.assertIn('public-site-group-cannot-join', str(e.exception))

    @patch('gs.group.member.join.listcommandjoiners.user_member_of_site')
    def test_ptsm_join_group_member(self, umos):
        'Ensure that group members can join a group'
        j = PublicToSiteMemberJoiner(FauxVisibility())
        u = FauxUserInfo()
        umos.return_value = True
        n = 'gs.group.member.join.listcommandjoiners.user_member_of_group'
        with patch(n) as umog:
            umog.return_value = True
            with self.assertRaises(GroupMember):
                j.join(u, faux_email(), None)

    @patch('gs.group.member.join.listcommandjoiners.user_member_of_site')
    def test_ptsm_join(self, umos):
        'Ensure that group members can join a group'
        u = FauxUserInfo()
        umos.return_value = True
        email = faux_email()
        with patch.object(PublicToSiteMemberJoiner,
                          'send_confirmation') as sc:
            j = PublicToSiteMemberJoiner(FauxVisibility())
            n = 'gs.group.member.join.listcommandjoiners.'\
                'user_member_of_group'
            with patch(n) as umog:
                umog.return_value = False
                j.join(u, email, None)
        sc.assert_called_once_with(email, 'member@example.com', u, None)

    @patch('gs.group.member.join.listcommandjoiners.user_member_of_group')
    def test_public_member(self, umog):
        umog.return_value = True
        u = FauxUserInfo()
        email = faux_email()
        j = PublicJoiner(FauxVisibility())
        with self.assertRaises(GroupMember):
            j.join(u, email, None)

    @patch('gs.group.member.join.listcommandjoiners.user_member_of_group')
    def test_public(self, umog):
        'Test a person with an existing profile joining a group'
        umog.return_value = False
        u = FauxUserInfo()
        email = faux_email()
        with patch.object(PublicJoiner, 'send_confirmation') as sc:
            j = PublicJoiner(FauxVisibility())
            j.join(u, email, None)
        sc.assert_called_once_with(email, 'member@example.com', u, None)

    @patch('gs.group.member.join.listcommandjoiners.user_member_of_group')
    def test_public_new(self, umog):
        'Test a person without an existing profile joining a group'
        umog.return_value = False
        email = faux_email()
        u = FauxUserInfo()
        with patch.object(PublicJoiner, 'send_confirmation') as sc:
            with patch.object(PublicJoiner, 'create_user') as cu:
                cu.return_value = u
                j = PublicJoiner(FauxVisibility())
                j.join(None, email, None)
        sc.assert_called_once_with(email, 'member@example.com', u, None)
        cu.assert_called_once_with('<member@example.com>')


class SendConfirmationTest(TestCase):

    def test_best_fn_no_name(self):
        'Test that we extract the name from the email address'
        j = PublicJoiner(FauxVisibility())
        f = 'From: <member@example.com>'
        r = j.get_best_fn(f)
        self.assertEqual('member', r)

    def test_best_fn_name(self):
        'Test we extract the name from the From header'
        j = PublicJoiner(FauxVisibility())
        f = 'From: A Person <member@example.com>'
        r = j.get_best_fn(f)
        self.assertEqual('A Person', r)

    def test_generate_confirmation_id(self):
        'Test the generation of the confirmation ID'
        j = PublicJoiner(FauxVisibility())
        r1 = j.generate_confirmation_id('This is not an email')
        r2 = j.generate_confirmation_id('This is not a pipe')
        r3 = j.generate_confirmation_id(faux_email())

        self.assertEqual(6, len(r1))
        self.assertEqual(6, len(r2))
        self.assertEqual(6, len(r3))
        self.assertNotEqual(r1, r2)
        self.assertNotEqual(r1, r3)
        self.assertNotEqual(r2, r3)

    @patch.object(PublicJoiner, 'generate_confirmation_id')
    def test_send_confirmation(self, gci):
        gci.return_value = 'a0b1c2'
        e = faux_email()
        u = FauxUserInfo()
        v = FauxVisibility()
        n = 'gs.group.member.join.listcommandjoiners.ConfirmationNotifier'
        with patch(n) as cn:
            with patch.object(PublicJoiner, 'query') as q:
                j = PublicJoiner(v)
                j.send_confirmation(e, 'person@example.com', u, None)
        gci.assert_called_once_with(e)
        q.add_confirmation.assert_called_once_with(
            'person@example.com',  'a0b1c2', u.id, v.groupInfo.id,
            v.groupInfo.siteInfo.id)
        cn.assert_called_once_with('This is not a folder', None)
