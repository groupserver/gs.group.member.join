.. sectnum::

============
Introduction
============

This part of the code contains the code that allows people to join 
groups. It consists of a little-used `join page`_ and the heavily used
`IGSJoiningUser`_ interface.

=========
Join Page
=========

The ``join.html`` page, in a group, is used by people who are **logged**
**in** to join a group. The new member selects a message delivery
setting from the list provided, and clicks the lovely *Join* button. The
`IGSJoinUser`_ code performs the mechanics of joining.

==================
``IGSJoiningUser``
==================

To join the new member to the group the code in this module is used
to adapt a ``IGSUserInfo`` to a  ``IGSJoiningUser``. The adapted
instance has a ``join`` method. When invoked the new member will be
joined to the group, the site, and all the requisite people will be
sent a notification saying that the new member has joined.

This code is used by both the ``gs.profile.signup`` and 
``gs.profile.invite`` modules.

