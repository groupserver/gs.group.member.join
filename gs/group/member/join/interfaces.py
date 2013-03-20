# coding=utf-8
from zope.interface import Interface
from zope.schema import Choice
from Products.GSProfile.interfaces import deliveryVocab


class IGSJoiningUser(Interface):

    def join(groupInfo):
        '''Join a group.

        Description
        ===========

        This method joins the user to the group, so the user becomes a
        member.

        Arguments
        =========

        `groupInfo`: The group to join.

        Returns
        =======

        None.

        Side Effects
        ============

        * The user becomes a member of the group.
        * The new member is sent a Welcome message
        * If not already a member of the site user-group, the user
          becomes a member of the site.
        * If required by the group, the new member becomes a moderated
          member of the group. Unless the new member is a administrator
          for the site, in which case the new member is *not* moderated.
        * The group administrators are email to tell them that a new
          member has joined.'''


class IGSJoinGroup(Interface):
    delivery = Choice(title=u'Message Delivery Settings',
      description=u'Your message delivery settings.',
      vocabulary=deliveryVocab,
      default='email')
