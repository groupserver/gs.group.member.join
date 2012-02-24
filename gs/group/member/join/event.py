# coding=utf-8
from zope.component.interfaces import ObjectEvent
from zope.component.interfaces import IObjectEvent
from zope.interface import Attribute, implements

class IGSJoinGroupEvent(IObjectEvent):
    """ An event issued after someone has joined a group."""
    groupInfo   = Attribute(u'The group that is being joined')
    memberInfo  = Attribute(u'The new group member')

class GSJoinGroupEvent(ObjectEvent):
    implements(IGSJoinGroupEvent)
    
    def __init__(self, context, groupInfo, memberInfo):
        ObjectEvent.__init__(self, context)
        self.groupInfo = groupInfo
        self.memberInfo = memberInfo

