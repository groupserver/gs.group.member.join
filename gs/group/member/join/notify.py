# coding=utf-8
from urllib import quote
from zope.component import createObject, getMultiAdapter
from zope.cachedescriptors.property import Lazy
from gs.group.base.page import GroupPage
from gs.profile.notify.sender import MessageSender
from Products.GSGroup.interfaces import IGSMailingListInfo
UTF8 = 'utf-8'

class NotifyNewMember(object):
    textTemplateName = 'new-member-msg.txt'
    htmlTemplateName = 'new-member-msg.html'
    
    def __init__(self, context, request):
        self.context = context
        self.request = request

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
        
    def notify(self, userInfo, groupInfo):
        subject = (u'Welcome to %s' % (self.groupInfo.name).encode(UTF8))
        text = self.textTemplate(userInfo=userInfo)
        html = self.htmlTemplate(userInfo=userInfo)
        ms = MessageSender(self.context, userInfo)
        ms.send_message(subject, text, html)

class NotifyMemberMessage(GroupPage):
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

