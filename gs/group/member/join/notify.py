# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright © 2013 OnlineGroups.net and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
from zope.component import createObject, getMultiAdapter
from zope.cachedescriptors.property import Lazy
from gs.profile.notify.sender import MessageSender
from gs.profile.email.base.emailuser import EmailUser
UTF8 = 'utf-8'


class NotifyNewMember(object):
    textTemplateName = 'new-member-msg.txt'
    htmlTemplateName = 'new-member-msg.html'

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.oldContentType = self.request.response.getHeader('Content-Type')

    @Lazy
    def groupInfo(self):
        retval = createObject('groupserver.GroupInfo', self.context)
        assert retval, 'Could not create the GroupInfo from %s' % self.context
        return retval

    @Lazy
    def textTemplate(self):
        retval = getMultiAdapter((self.context, self.request),
                    name=self.textTemplateName)
        assert retval
        return retval

    @Lazy
    def htmlTemplate(self):
        retval = getMultiAdapter((self.context, self.request),
                    name=self.htmlTemplateName)
        assert retval
        return retval

    def notify(self, userInfo):
        subject = (u'Welcome to %s' % (self.groupInfo.name).encode(UTF8))
        emailUser = EmailUser(userInfo.user, userInfo)
        text = self.textTemplate(userInfo=userInfo, userEmail=emailUser)
        html = self.htmlTemplate(userInfo=userInfo, userEmail=emailUser)
        ms = MessageSender(self.context, userInfo)
        ms.send_message(subject, text, html)
        self.request.response.setHeader('Content-Type', self.oldContentType)


# And the equivilent class for telling the admin

class NotifyAdmin(NotifyNewMember):
    textTemplateName = 'new-member-admin-msg.txt'
    htmlTemplateName = 'new-member-admin-msg.html'

    def notify(self, adminInfo, userInfo):
        subject = (u'%s: New Member' % (self.groupInfo.name).encode(UTF8))
        emailUser = EmailUser(userInfo.user, userInfo)
        text = self.textTemplate(adminInfo=adminInfo, userInfo=userInfo,
                                 userEmail=emailUser)
        html = self.htmlTemplate(adminInfo=adminInfo, userInfo=userInfo,
                                 userEmail=emailUser)
        ms = MessageSender(self.context, adminInfo)
        ms.send_message(subject, text, html)
        self.request.response.setHeader('Content-Type', self.oldContentType)
