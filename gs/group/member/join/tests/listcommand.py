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
from gs.group.member.join.listcommand import (
    SubscribeCommand, ConfirmCommand)
import gs.group.member.join.listcommand  # lint:ok
from gs.group.list.command.result import CommandResult
from gs.group.list.command.tests.faux import FauxGroup


class FauxSiteInfo(object):
    name = 'An Example Site'
    id = 'example'


class FauxGroupInfo(object):
    name = 'An Example Group'
    id = 'example_group'
    siteInfo = FauxSiteInfo()


class FauxUserInfo(object):
    name = 'An Example user'
    id = 'exampleuser'


class TestSubscribeCommand(TestCase):
    subscribeSubject = 'Subscribe'

    def setUp(self):
        self.fauxGroup = FauxGroup()
        self.fauxGroupInfo = FauxGroupInfo()

    @staticmethod
    def get_email(subject):
        retval = Parser().parsestr(
            'From: <member@example.com>\n'
            'To: <group@example.com>\n'
            'Subject: {0}\n'
            '\n'
            'Body would go here\n'.format(subject))
        return retval

    def test_generate_confirmation_id(self):
        'Test the generation of the confirmation ID'
        c = SubscribeCommand(self.fauxGroup)
        with patch.object(gs.group.member.join.listcommand,
                          'createObject') as MockedCreateObject:
            MockedCreateObject.return_value = self.fauxGroupInfo
            r1 = c.generate_confirmation_id('This is not an email')
            r2 = c.generate_confirmation_id('This is not a pipe')

        self.assertEqual(6, len(r1))
        self.assertEqual(6, len(r2))
        self.assertNotEqual(r1, r2)

    def test_subscribe_member(self):
        'Are subscribe requests from existing users ignored?'
        with patch.object(SubscribeCommand,
                          'get_userInfo') as mockGetUserInfo:
            with patch.object(SubscribeCommand, 'groupInfo') as mockGI:
                with patch(
                    'gs.group.member.join.listcommand.user_member_of_group'
                ) as mockUserMemberOfGroup:
                    mockGetUserInfo.return_value = FauxUserInfo()
                    mockGI.return_value = FauxGroupInfo()
                    mockUserMemberOfGroup.return_value = True

                    c = SubscribeCommand(self.fauxGroup)
                    e = self.get_email(self.subscribeSubject)
                    r = c.process(e, None)

        self.assertEqual(CommandResult.notACommand, r)

    # FIXME: Pathetically inadequate testing. The code needs to be
    # refactored. See the SubscribeCommand.process() method for how.


class TestConfirmCommand(TestCase):
    confirmSubject = 'Confirm some text ID-1a2b3c'
    confirmNoIdSubject = 'Confirm subject without an identifier'

    def setUp(self):
        self.fauxGroup = FauxGroup()

    @staticmethod
    def get_email(subject):
        retval = Parser().parsestr(
            'From: <member@example.com>\n'
            'To: <group@example.com>\n'
            'Subject: {0}\n'
            '\n'
            'Body would go here\n'.format(subject))
        return retval

    def test_get_confirmation_id_true(self):
        'Can the confirmation ID be extracted from the subject?'
        c = ConfirmCommand(self.fauxGroup)
        e = self.get_email(self.confirmSubject)
        r = c.get_confirmation_id(e)

        self.assertEqual('1a2b3c', r)

    def test_get_confirmation_id_false(self):
        'Is None returned when ther e is no ID in the subject?'
        c = ConfirmCommand(self.fauxGroup)
        e = self.get_email(self.confirmNoIdSubject)
        r = c.get_confirmation_id(e)

        self.assertIs(None, r)

    def test_not_id(self):
        'Is an email without an ID seen as not a command?'
        c = ConfirmCommand(self.fauxGroup)
        e = self.get_email(self.confirmNoIdSubject)
        r = c.process(e, None)
        self.assertEqual(CommandResult.notACommand, r)

    @patch.object(ConfirmCommand, 'query')
    def test_no_info_found(self, mockQuery):
        'Is a stop called if there is no confirmation info found?'
        mockQuery.get_confirmation.return_value = None
        e = self.get_email(self.confirmSubject)
        c = ConfirmCommand(self.fauxGroup)
        r = c.process(e, None)

        self.assertEqual(CommandResult.commandStop, r)

    @patch.object(ConfirmCommand, 'query')
    def test_info_found_addr_missmatch(self, mockQuery):
        'Is a stop called if there is confirmation info found?'
        mockQuery.get_confirmation.return_value = {
            'email': 'missmatch',
        }
        e = self.get_email(self.confirmSubject)
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
        e = self.get_email(self.confirmSubject)
        with patch.object(ConfirmCommand, 'join') as patchedJoin:
            c = ConfirmCommand(self.fauxGroup)
            r = c.process(e, None)
            patchedJoin.assert_called_with(
                mockQuery.get_confirmation.return_value, None)

        self.assertEqual(CommandResult.commandStop, r)