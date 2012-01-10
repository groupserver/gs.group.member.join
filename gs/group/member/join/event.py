# coding=utf-8
from zope.interface import implements, implementedBy
from OFS.Folder import Folder
from zope.interface import Interface
from zope.interface import Attribute

from Products.XWFChat.interfaces import IGSGroupFolder

class IGSJoinGroupEvent(Interface):
    """ An event issued after someone has joined a group."""
    context     = Attribute(u'The context of the Start a Group code') 
    request     = Attribute(u'The request for the Start a Group code')
    groupInfo   = Attribute(u'The group that is being joined')
    memberInfo  = Attribute(u'The new group member')

class GSJoinGroupEvent(object):
    implements(IGSJoinGroupEvent)
    
    def __init__(self, groupInfo, memberInfo):
        self.groupInfo = groupInfo
        self.memberInfo = memberInfo

