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
from zope.cachedescriptors.property import Lazy
from zope.component import createObject
from zope.formlib import form
from zope.i18n import translate
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.content.form.base import radio_widget
from gs.group.base.form import GroupForm
from gs.group.member.base import user_member_of_group
from gs.profile.email.base.emailuser import EmailUser
from Products.XWFCore.XWFUtils import get_the_actual_instance_from_zope
from . import GSMessageFactory as _
from .interfaces import IGSJoinGroup
from .utils import join


class JoinForm(GroupForm):
    pageTemplateFileName = 'browser/templates/join.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(IGSJoinGroup, render_context=False)

    def __init__(self, context, request):
        super(JoinForm, self).__init__(context, request)
        self.form_fields['delivery'].custom_widget = radio_widget

    @Lazy
    def label(self):
        retval = _('join-group', 'Join ${groupName}',
                   mapping={'groupName': self.groupInfo.name})
        return retval

    @property
    def ctx(self):
        return get_the_actual_instance_from_zope(self.context)

    @Lazy
    def mailingListInfo(self):
        retval = createObject('groupserver.MailingListInfo', self.ctx)
        return retval

    @property
    def canJoin(self):
        retval = (not(self.loggedInUser.anonymous)
                  and not(self.isMember)
                  and self.hasEmail
                  and self.mailingListInfo.get_property('subscribe', False))
        return retval

    @property
    def willPost(self):
        postingMembers = self.mailingListInfo.get_property(
            'posting_members', [])
        retval = not(bool(postingMembers))
        return retval

    @property
    def isMember(self):
        return user_member_of_group(self.loggedInUser, self.groupInfo)

    @Lazy
    def hasEmail(self):
        eu = EmailUser(self.context, self.loggedInUser)
        retval = (len(eu.get_verified_addresses()) > 0)
        return retval

    @property
    def emailSettingsPhrase(self):
        settingsUrl = '{0}/emailsettings.html'.format(self.loggedInUser.url)
        retval = _(
            'email-settings-phrase',
            'Visit <a href="${link}">your email settings page</a> to '
            'verify your address, or add a new address.',
            mapping={'link': settingsUrl})
        return retval

    @form.action(name='join', label=_('join-button', 'Join'),
                 failure='handle_join_action_failure')
    def handle_join(self, action, data):
        assert self.canJoin

        join(self.context, self.request, self.loggedInUser, self.groupInfo)

        if data['delivery'] == 'email':
            # --=mpj17=-- The default is one email per post
            deliveryMsg = _(
                'join-delivery-email',
                'You will receive an email message every time someone '
                'posts to ${groupName}.',
                mapping={'groupName': self.groupInfo.name})
        elif data['delivery'] == 'digest':
            self.loggedInUser.user.set_enableDigestByKey(self.groupInfo.id)
            deliveryMsg = _(
                'join-delivery-digest',
                'You will receive a daily digest of topics from '
                '${groupName}.',
                mapping={'groupName': self.groupInfo.name})

        elif data['delivery'] == 'web':
            self.loggedInUser.user.set_disableDeliveryByKey(
                self.groupInfo.id)
            deliveryMsg = _(
                'join-delivery-web',
                'You will not receive any email when someone posts to'
                '${groupName}.',
                mapping={'groupName': self.groupInfo.name})
        assert deliveryMsg

        g = '<a class="group" href="{url}">{name}</a>'
        groupLink = g.format(url=self.groupInfo.relativeURL,
                             name=self.groupInfo.name)
        joinConfirm = _(
            'join-confirm',
            'You have joined ${groupLink}.',
            mapping={'groupLink': groupLink, })
        self.status = '<p>{0} {1}</p>'.format(translate(joinConfirm),
                                              translate(deliveryMsg))

    def handle_join_action_failure(self, action, data, errors):
        if len(errors) == 1:
            e = _('join-page-single-error', 'There is an error:')
        else:
            e = _('join-page-multiple-errors', 'There are errors:')
        self.status = '<p>{0}</p>'.format(translate(e))
