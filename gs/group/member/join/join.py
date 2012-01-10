# coding=utf-8
from zope.component import createObject
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from gs.profile.email.base.emailuser import EmailUser
from gs.group.base.form import GroupForm
from gs.group.member.join.interfaces import IGSJoiningUser
from gs.content.form.radio import radio_widget
from Products.GSGroupMember.groupmembership import user_member_of_group
from Products.XWFCore.XWFUtils import get_the_actual_instance_from_zope
from interfaces import IGSJoinGroup
from notify import NotifyNewMember

class JoinForm(GroupForm):
    label = u'Join'
    pageTemplateFileName = 'browser/templates/join.pt'
    template = ZopeTwoPageTemplateFile(pageTemplateFileName)
    form_fields = form.Fields(IGSJoinGroup, render_context=False)

    def __init__(self, context, request):
        GroupForm.__init__(self, context, request)
        self.__userInfo = self.__mailingListInfo = self.__hasEmail = None
        self.form_fields['delivery'].custom_widget = radio_widget

    @property 
    def ctx(self):
        return get_the_actual_instance_from_zope(self.context)        
        
    @property
    def userInfo(self):
        if self.__userInfo == None:
            self.__userInfo = createObject('groupserver.LoggedInUser',
                                  self.ctx)
        return self.__userInfo

    @property
    def mailingListInfo(self):
        if self.__mailingListInfo == None:
            self.__mailingListInfo = createObject(
                'groupserver.MailingListInfo', self.ctx)
        return self.__mailingListInfo
        
    @property
    def canJoin(self):
        retval = not(self.userInfo.anonymous) \
                    and not(self.isMember) \
                    and self.hasEmail \
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
        
    @property
    def hasEmail(self):
        if self.__hasEmail == None:
            eu = EmailUser(self.context, self.userInfo)
            self.__hasEmail = (len(eu.get_verified_addresses()) > 0)
        return self.__hasEmail
        
    @form.action(label=u'Join', failure='handle_join_action_failure')
    def handle_invite(self, action, data):
        assert self.canJoin
        
        joiningUser = IGSJoiningUser(self.userInfo)
        joiningUser.silent_join(self.groupInfo)
        notifier = NotifyNewMember(self.context, self.request)
        notifier.notify(self.userInfo, self.groupInfo)
        
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

