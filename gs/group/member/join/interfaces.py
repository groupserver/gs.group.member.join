# coding=utf-8
from zope.interface import Interface
from zope.schema import *
from Products.GSProfile.interfaces import deliveryVocab

class IGSJoiningUser(Interface):

    def join(group):
        '''Join the group'''

class IGSJoinGroup(Interface):
    delivery = Choice(title=u'Message Delivery Settings',
      description=u'Your message delivery settings.',
      vocabulary=deliveryVocab,
      default='email')


