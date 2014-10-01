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
from gs.group.member.join.listcommand import (ConfirmCommand,
                                              SubscribeCommand)
import gs.group.member.join.listcommand  # lint:ok
from gs.group.list.command.result import CommandResult
from .faux import (FauxGroup, FauxGroupInfo, FauxUserInfo, faux_email)


class TestSubscribeCommand(TestCase):

    @patch.object(SubscribeCommand, 'groupInfo')
    def test_member(self, gi):
        'Test a member sending a "join" command'
        gi.return_value = FauxGroupInfo()
        with patch.object(SubscribeCommand, 'get_userInfo') as g_ui:
            u = FauxUserInfo()
            g_ui.return_value = u
            with patch('gs.group.member.join.listcommand.IJoiner') as j:
                joinInstance = j.return_value
                joinInstance.join.side_effect =\
                    gs.group.member.join.listcommand.GroupMember
                sc = SubscribeCommand(FauxGroup)
                e = faux_email()
                r = sc.process(e, None)
        joinInstance.join.assert_called_once_with(u, e, None)
        self.assertEqual(CommandResult.notACommand, r)

    @patch.object(SubscribeCommand, 'groupInfo')
    def test_cannot(self, gi):
        'Test sending a "join" command to a group that cannot be joined'
        gi.return_value = FauxGroupInfo()
        with patch.object(SubscribeCommand, 'get_userInfo') as g_ui:
            u = FauxUserInfo()
            g_ui.return_value = u
            with patch('gs.group.member.join.listcommand.IJoiner') as j:
                joinInstance = j.return_value
                joinInstance.join.side_effect =\
                    gs.group.member.join.listcommand.CannotJoin
                n = 'gs.group.member.join.listcommand.NotifyCannotJoin'
                with patch(n):
                    sc = SubscribeCommand(FauxGroup)
                    e = faux_email()
                    r = sc.process(e, None)
        joinInstance.join.assert_called_once_with(u, e, None)
        self.assertEqual(CommandResult.commandStop, r)

    @patch.object(SubscribeCommand, 'groupInfo')
    def test_join(self, gi):
        'Test sending a "join" command'
        gi.return_value = FauxGroupInfo()
        with patch.object(SubscribeCommand, 'get_userInfo') as g_ui:
            u = FauxUserInfo()
            g_ui.return_value = u
            with patch('gs.group.member.join.listcommand.IJoiner'):
                sc = SubscribeCommand(FauxGroup)
                e = faux_email()
                r = sc.process(e, None)
        self.assertEqual(CommandResult.commandStop, r)


class TestConfirmCommand(TestCase):
    confirmSubject = 'Confirm some text ID-1a2b3c'
    confirmNoIdSubject = 'Confirm subject without an identifier'

    def setUp(self):
        self.fauxGroup = FauxGroup()

    def test_get_confirmation_id_true(self):
        'Can the confirmation ID be extracted from the subject?'
        c = ConfirmCommand(self.fauxGroup)
        e = faux_email(self.confirmSubject)
        r = c.get_confirmation_id(e)

        self.assertEqual('1a2b3c', r)

    def test_get_confirmation_id_false(self):
        'Is None returned when ther e is no ID in the subject?'
        c = ConfirmCommand(self.fauxGroup)
        e = faux_email(self.confirmNoIdSubject)
        r = c.get_confirmation_id(e)

        self.assertIs(None, r)

    def test_not_id(self):
        'Is an email without an ID seen as not a command?'
        c = ConfirmCommand(self.fauxGroup)
        e = faux_email(self.confirmNoIdSubject)
        r = c.process(e, None)
        self.assertEqual(CommandResult.notACommand, r)

    @patch.object(ConfirmCommand, 'query')
    def test_no_info_found(self, mockQuery):
        'Is a stop called if there is no confirmation info found?'
        mockQuery.get_confirmation.return_value = None
        e = faux_email(self.confirmSubject)
        c = ConfirmCommand(self.fauxGroup)
        r = c.process(e, None)

        self.assertEqual(CommandResult.commandStop, r)

    @patch.object(ConfirmCommand, 'query')
    def test_info_found_addr_missmatch(self, mockQuery):
        'Is a stop called if there is confirmation info found?'
        mockQuery.get_confirmation.return_value = {
            'email': 'missmatch',
        }
        e = faux_email(self.confirmSubject)
        with patch('gs.group.member.join.listcommand.log') as patchedLog:
            c = ConfirmCommand(self.fauxGroup)
            patchedLog.info.return_value = None
            r = c.process(e, None)
            args, varArgs = patchedLog.info.call_args

        self.assertEqual(CommandResult.commandStop, r)
        self.assertIn('does not match', args[0])

    @patch.object(ConfirmCommand, 'query')
    def test_info_found_join(self, mockQuery):
        'Is ConfirmCommand.join called if the address matches?'
        mockQuery.get_confirmation.return_value = {
            'email': 'member@example.com',
        }
        e = faux_email(self.confirmSubject)
        with patch.object(ConfirmCommand, 'join') as patchedJoin:
            c = ConfirmCommand(self.fauxGroup)
            r = c.process(e, None)
            patchedJoin.assert_called_with(
                mockQuery.get_confirmation.return_value, None)

        self.assertEqual(CommandResult.commandStop, r)
