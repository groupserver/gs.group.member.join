# coding=utf-8
from zope.component import createObject
from Products.CustomUserFolder.interfaces import IGSUserInfo
from gs.profile.notify.interfaces import IGSNotifyUser
from utils import member_id, user_member_of_site, user_division_admin_of_group

class JoiningUser(object):
    def __init__(self, userInfo):
        self.userInfo = userInfo
        
    def join(self, groupInfo):
        self.join_group(groupInfo)
        self.send_welcome(groupInfo)
        self.join_site(groupInfo.siteInfo)
        self.set_moderation(groupInfo)
        self.tell_admin(groupInfo)
        
    def join_group(self, groupInfo):
        # Beware of regressions 
        #   <https://projects.iopen.net/groupserver/ticket/303>
        self.join_member_group(member_id(groupInfo))
        # TODO: Audit

    def join_member_group(self, member_group_id):
        site_root = self.userInfo.user.site_root()
        acl_users = getattr(site_root, 'acl_users')
        assert acl_users, 'ACL Users not found in site_root'
        groupNames = acl_users.getGroupNames()
        assert member_group_id in groupNames, \
            '%s not in %s' % (group, groupNames)
        try:
            acl_users.addGroupsToUser([member_group_id], self.userInfo.id)
        except:
            # TODO: Get RRW to explain to mpj17 why we do this
            return 0
        # TODO: Audit
    
    def send_welcome(self, groupInfo):
        # The user only gets a welcome message for joining a group,
        #    not for joining a site 
        #    <https://projects.iopen.net/groupserver/ticket/346>
        notifiedUser = IGSNotifyUser(self.userInfo)
        # Construct a message
        # Send a message
    
    def join_site(self, siteInfo):
        if not user_member_of_site(siteInfo.siteObj):
            self.join_member_group(member_id(siteInfo))
        assert user_member_of_site(siteInfo.siteObj)
        
    def set_moderation(self, groupInfo):
        mailingList = createInfo('groupserver.MailingListInfo',
                        groupInfo.groupObj, groupInfo.id)
        assert mailingList
        isDivisionAdmin = user_division_admin_of_group(self.userInfo, 
                            groupInfo)
        # This is tricky:
        #     <https://projects.iopen.net/groupserver/ticket/235>
        if mailingList.is_moderated and
            not(isDivisionAdmin) and
            mailingList.is_moderate_new:
            # TODO: add to moderation
            # TODO: Audit

    def tell_admin(self, groupInfo):
        # TODO: Tell all group admins
        #  <https://projects.iopen.net/groupserver/ticket/410>
        for admin in groupInfo.group_admins:
            notifiedUser = IGSNotifyUser(admin)
            # TODO: Send a message

