# coding=utf-8
try:
    from five.formlib.formbase import PageForm
except ImportError:
    from Products.Five.formlib.formbase import PageForm
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.group.member.join.interfaces import IGSJoiningUser
from Products.GSGroup.changebasicprivacy import radio_widget
from Products.GSGroupMember.groupmembership import user_member_of_group
from interfaces import IGSJoinGroup

class JoinForm(PageForm):
    label = u'Join'
    pageTemplateFileName = 'browser/templates/join.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(IGSJoinGroup, render_context=False)

    def __init__(self, context, request):
        PageForm.__init__(self, context, request)
        self.__siteInfo = self.__groupInfo = self.__userInfo = None
        self.__mailingListInfo = None
        self.form_fields['delivery'].custom_widget = radio_widget
        
    @property
    def siteInfo(self):
        if self.__siteInfo == None:
            self.__siteInfo = createObject('groupserver.SiteInfo', 
                                self.context.aq_self)
        assert self.__siteInfo
        return self.__siteInfo

    @property
    def groupInfo(self):
        if self.__groupInfo == None:
            self.__groupInfo = createObject('groupserver.GroupInfo', 
                                self.context.aq_self)
        assert self.__groupInfo
        return self.__groupInfo

    @property
    def userInfo(self):
        if self.__userInfo == None:
            self.__userInfo = createObject('groupserver.LoggedInUser',
                                  self.context.aq_self)
        return self.__userInfo

    @property
    def mailingListInfo(self):
        if self.__mailingListInfo == None:
            self.__mailingListInfo = createObject(
                'groupserver.MailingListInfo', self.context.aq_self)
        return self.__mailingListInfo
        
    @property
    def canJoin(self):
        retval = not(self.isMember) \
          and self.mailingListInfo.get_property('subscribe', False)
        return retval
    
    @property
    def willPost(self):
        postingMembers = self.mailingListInfo.get_property('posting_members', [])
        retval = not(bool(postingMembers))
        return retval
        
    @property
    def isMember(self):
        return user_member_of_group(self.userInfo, self.groupInfo)
        
    @form.action(label=u'Join', failure='handle_join_action_failure')
    def handle_invite(self, action, data):
        assert self.canJoin
        
        joiningUser = IGSJoiningUser(self.userInfo)
        joiningUser.join(self.groupInfo)

        if data['delivery'] == 'email':
            # --=mpj17=-- The default is one email per post
            m = u'You will receive an email message every time '\
              u'someone posts to %s.' % self.groupInfo.name
        elif data['delivery'] == 'digest':
            self.userInfo.user.set_enableDigestByKey(self.groupInfo.id)
            m = u'You will receive a daily digest of topics.'
        elif data['delivery'] == 'web':
            self.userInfo.user.set_disableDeliveryByKey(self.groupInfo.id)
            m = 'You will not receive any email from this group.'

        self.status = u'You have joined <a class="group" href="%s">%s</a>. %s' %\
          (self.groupInfo.url, self.groupInfo.name, m)
        assert type(self.status) == unicode
        
    def handle_join_action_failure(self, action, data, errors):
        if len(errors) == 1:
            self.status = u'<p>There is an error:</p>'
        else:
            self.status = u'<p>There are errors:</p>'

