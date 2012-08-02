# coding=utf-8
from urllib import quote
from zope.cachedescriptors.property import Lazy
from gs.group.base.page import GroupPage
from Products.GSGroup.interfaces import IGSMailingListInfo
from gs.profile.email.base.emailuser import EmailUser
UTF8 = 'utf-8'

class NotifyMemberMessage(GroupPage):
    @Lazy
    def userEmailInfo(self):
        # possibly this should be called something like testUserEmailInfo,
        # because it is really only used in the test case
        userInfo = self.loggedInUserInfo
        emailUser = EmailUser(userInfo.user, userInfo)
        return emailUser
        
    @Lazy
    def email(self):
        l = IGSMailingListInfo(self.groupInfo.groupObj)
        retval = l.get_property('mailto')
        return retval
    
    @Lazy
    def supportEmail(self):
        msg = u'Hi!\n\nI am a member of the group %s\n    %s\nand...' % \
            (self.groupInfo.name, self.groupInfo.url)
        sub = quote('Group Welcome')
        retval = 'mailto:%s?Subject=%s&body=%s' % \
            (self.siteInfo.get_support_email(), sub, quote(msg.encode(UTF8)))
        return retval
        
class NotifyMemberMessageText(NotifyMemberMessage):
    def __init__(self, context, request):
        NotifyMemberMessage.__init__(self, context, request)
        response = request.response
        response.setHeader("Content-Type", 'text/plain; charset=UTF-8')
        filename = 'welcome-to-%s.txt' % self.groupInfo.name
        response.setHeader('Content-Disposition',
                            'inline; filename="%s"' % filename)

# And the equivilent message that is sent to the administrators.

class NotifyAdminMessage(GroupPage):
    @Lazy
    def userEmailInfo(self):
        # possibly this should be called something like testUserEmailInfo,
        # because it is really only used in the test case
        userInfo = self.loggedInUserInfo
        emailUser = EmailUser(userInfo.user, userInfo)
        return emailUser

    @Lazy
    def email(self):
        l = IGSMailingListInfo(self.groupInfo.groupObj)
        retval = l.get_property('mailto')
        return retval
    
    @Lazy
    def supportEmail(self):
        msg = u'Hi!\n\nI am an administrator of the group %s\n    %s\nand...' % \
            (self.groupInfo.name, self.groupInfo.url)
        sub = quote('New Member')
        retval = 'mailto:%s?Subject=%s&body=%s' % \
            (self.siteInfo.get_support_email(), sub, quote(msg.encode(UTF8)))
        return retval
        
class NotifyAdminMessageText(NotifyMemberMessage):
    def __init__(self, context, request):
        NotifyMemberMessage.__init__(self, context, request)
        response = request.response
        response.setHeader("Content-Type", 'text/plain; charset=UTF-8')
        filename = 'new-member-%s.txt' % self.groupInfo.name
        response.setHeader('Content-Disposition',
                            'inline; filename="%s"' % filename)

