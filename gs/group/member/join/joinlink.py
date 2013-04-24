# -*- coding: utf-8 -*-
from zope.cachedescriptors.property import Lazy
from gs.group.member.viewlet import MemberViewlet
from gs.group.privacy.interfaces import IGSGroupVisibility


class JoinLinkViewlet(MemberViewlet):
    def __init__(self, group, request, view, manager):
        super(JoinLinkViewlet, self).__init__(group, request, view, manager)

    @Lazy
    def show(self):
        v = IGSGroupVisibility(self.groupInfo)
        retval = not(self.isMember) and v.isPublic
        return retval
