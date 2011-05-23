# coding=utf-8
from zope.cachedescriptors.property import Lazy
from gs.group.member.base.viewlet import MemberViewlet

class JoinLinkViewlet(MemberViewlet):
    def __init__(self, group, request, view, manager):
        MemberViewlet.__init__(self, group, request, view, manager)

    @Lazy
    def show(self):
        # Show the Join links if the user is not a member, and the 
        #   group is public.
        retval = not(self.isMember) and self.viewTopics
        return retval

