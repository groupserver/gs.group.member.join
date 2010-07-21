# coding=utf-8
from zope.component import createObject
from gs.profile.notify.interfaces import IGSNotifyUser
from gs.group.member.base.utils import member_id, user_member_of_site,\
    user_division_admin_of_group
from audit import JoinAuditor, JOIN_GROUP, JOIN_SITE, MODERATED

class JoiningUser(object):
    def __init__(self, userInfo):
        self.userInfo = userInfo
        self.context = userInfo.user
        
    def join(self, groupInfo):
        auditor = JoinAuditor(self.context, groupInfo, self.userInfo)
        self.join_group(groupInfo, auditor)
        self.send_welcome(groupInfo)
        self.join_site(groupInfo.siteInfo, auditor)
        self.set_moderation(groupInfo, auditor)
        self.tell_admin(groupInfo)
        
    def join_group(self, groupInfo, auditor):
        # Beware of regressions 
        #   <https://projects.iopen.net/groupserver/ticket/303>
        self.join_member_group(member_id(groupInfo.id))
        auditor.info(JOIN_GROUP)

    def join_member_group(self, member_group_id):
        site_root = self.userInfo.user.site_root()
        acl_users = getattr(site_root, 'acl_users')
        assert acl_users, 'ACL Users not found in site_root'
        groupNames = acl_users.getGroupNames()
        assert member_group_id in groupNames, \
            '%s not in %s' % (group, groupNames)
        acl_users.addGroupsToUser([member_group_id], self.userInfo.id)
   
    def send_welcome(self, groupInfo):
        # The user only gets a welcome message for joining a group,
        #    not for joining a site 
        #    <https://projects.iopen.net/groupserver/ticket/346>
        # TODO: <https://projects.iopen.net/groupserver/ticket/414>
        notifiedUser = IGSNotifyUser(self.userInfo)
        ndict = {}
        notifiedUser.send_notification('', '')
    
    def join_site(self, siteInfo, auditor):
        if not user_member_of_site(self.userInfo, siteInfo.siteObj):
            self.join_member_group(member_id(siteInfo.id))
            auditor.info(JOIN_SITE)
        assert user_member_of_site(self.userInfo, siteInfo.siteObj)
        
    def set_moderation(self, groupInfo, auditor):
        # This is tricky:
        #     <https://projects.iopen.net/groupserver/ticket/235>
        mailingList = createObject('groupserver.MailingListInfo',
                        self.context, groupInfo.id)
        isDivisionAdmin = user_division_admin_of_group(self.userInfo, 
                            groupInfo)
        if (mailingList.is_moderated and
            not(isDivisionAdmin) and
            mailingList.is_moderate_new):
            # TODO: Rip this code out into a utility that can be called
            #   by manage members
            mList = mailingList.mlist
            moderatedIds = [ m.id for m in mailingList.moderatees ]
            assert self.userInfo.id not in moderatedIds, \
                '%s was marked for moderation in %s (%s), but is '\
                'already moderated.' % \
                (self.userInfo.id, groupInfo.name, groupInfo.id)
            moderatedIds.append(self.userInfo.id)
            if mlist.hasProperty('moderated_members'):
                groupList.manage_changeProperties(moderated_members=moderatedIds)
            else:
                groupList.manage_addProperty('moderated_members', 
                    moderatedIds, 'lines')
            auditor.info(MODERATE)

    def tell_admin(self, groupInfo):
        # TODO: Tell all group admins
        #  <https://projects.iopen.net/groupserver/ticket/410>
        for admin in groupInfo.group_admins:
            notifiedUser = IGSNotifyUser(admin)
            # TODO: Send a message

