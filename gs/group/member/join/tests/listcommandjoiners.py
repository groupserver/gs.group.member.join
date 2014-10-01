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
#from mock import patch
from unittest import TestCase
from gs.group.member.join.listcommandjoiners import (
    OddJoiner, SecretJoiner, PrivateJoiner, CannotJoin)
import gs.group.member.join.listcommand  # lint:ok
from .faux import FauxVisibility, FauxUserInfo


class FailJoinerTest(TestCase):
    def assertFailJoin(self, j):
        u = FauxUserInfo()
        with self.assertRaises(CannotJoin) as e:
            j.join(u, 'person@example.com', None)
        return e

    def test_odd_join_fail(self):
        'Test that we always fail at joining an odd group'
        j = OddJoiner(FauxVisibility())
        self.assertFailJoin(j)

    def test_secret_join_fail(self):
        'Test that we always fail at joining a secret group'
        j = SecretJoiner(FauxVisibility())
        self.assertFailJoin(j)

    def test_private_join_fail(self):
        'Test that we always fail at joining a secret group'
        j = PrivateJoiner(FauxVisibility())
        e = self.assertFailJoin(j)
        msg = str(e.exception)
        self.assertIn('lists.example.com', msg)
