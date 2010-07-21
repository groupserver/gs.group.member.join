# coding=utf-8
from zope.interface import Interface
from zope.schema import *

class IGSJoiningUser(Interface):

    def join(group):
        '''Join the group'''

