========================
``gs.group.member.join``
========================
~~~~~~~~~~~~~~~~~~~~~~~~
Join a GroupServer group
~~~~~~~~~~~~~~~~~~~~~~~~

:Author: `Michael JasonSmith`_
:Contact: Michael JasonSmith <mpj17@onlinegroups.net>
:Date: 20115-02-20
:Organization: `GroupServer.org`_
:Copyright: This document is licensed under a
  `Creative Commons Attribution-Share Alike 4.0 International License`_
  by `OnlineGroups.net`_.


Introduction
============

This part of the code contains the code that allows people to
join groups. It consists of a little-used `join page`_ and the
heavily used IGSJoiningUser_ interface.

Join Page
=========

The ``join.html`` page, in a group, is used by people who are
**logged in** to join a group. The new member selects a message
delivery setting from the list provided, and clicks the lovely
*Join* button. The IGSJoiningUser_ code performs the mechanics of
joining.

``IGSJoiningUser``
==================

This code is used by the ``gs.profile.signup`` module [#signup]_
and the ``gs.profile.invite`` modules [#invite]_.  To join the
new member to the group the code in this module is used to adapt
a ``IGSUserInfo`` to a ``IGSJoiningUser``:

.. code-block:: python

  joiningUser = IGSJoiningUser(self.loggedInUser)

The adapted instance has a ``join`` method. When invoked the new
member will be joined to the group, the site, and all the
requisite people will be sent a notification saying that the new
member has joined:

.. code-block:: python

  joiningUser.join(self.groupInfo)

If no notification is wanted, then ``silent_join`` can be used:

.. code-block:: python

  joiningUser.silent_join(self.groupInfo)

The `Join page`_ uses the latter, ``silent_join`` because it
sends out its own notifications_.

Notifications
=============

This product sends out two notifications when someone uses the
`Join page`_. First, is the `Group Welcome`_, that is sent to the
new group member. Then the group administrator will get the `New
Member`_ notification.

Group Welcome
-------------

The *Group Welcome* notification is designed to provide the new
member with some useful information about the group, including:

* The URL of the group,
* The email address of the group,
* How to leave the group, and
* The URL of the profile of the new member.

The pages ``new-member-msg.html`` and ``new-member-msg.txt``, in
the Group context, provide this information in HTML and plain
text accordingly. The email message is constructed by the
``gs.group.member.join.notify.NotifyNewMember`` class:

.. code-block:: python

  notifier = NotifyNewMember(group, request)

The message is sent by calling the ``notify`` method:

.. code-block:: python

  notifier.notify(self.loggedInUser)

New Member
----------

Each of the group administrators needs to be notified that there
is a new group member. The *New Member* notification (at
``new-member-admin-msg.html`` or ``new-member-admin-msg.txt`` in
the Group context) does this by providing the following
information:

* The name of the new member,
* The URL of the profile of the new member,
* A link to the *Join and Leave Log* [#log]_, and
* A little explanation as to why the administrator received the
  message.

The email is constructed by the
``gs.group.member.join.notify.NotifyAdmin`` class:

.. code-block:: python

  notifier = NotifyAdmin(group, request)

Usually a loop is used to send the email to every administrator:

.. code-block:: python

  for adminInfo in self.groupInfo.group_admins:
      notifier.notify(adminInfo, self.loggedInUser)

Resources
=========

- Code repository: https://github.com/groupserver/gs.group.member.join
- Translations: https://www.transifex.com/projects/p/gs-group-member-join/
- Questions and comments to http://groupserver.org/groups/development
- Report bugs at https://redmine.iopen.net/projects/groupserver

.. _GroupServer: http://groupserver.org/
.. _GroupServer.org: http://groupserver.org/
.. _OnlineGroups.Net: https://onlinegroups.net
.. _Michael JasonSmith: http://groupserver.org/p/mpj17
..  _Creative Commons Attribution-Share Alike 4.0 International License:
    http://creativecommons.org/licenses/by-sa/4.0/

.. [#signup] See the ``gs.profile.signup.base`` product
             <https://github.com/groupserver/gs.profile.signup.base/>

.. [#invite] See the ``gs.group.member.invite.base`` and
             ``gs.group.member.invite.csv`` products:

             * <https://github.com/groupserver/gs.group.member.invite.base/>
             *  <https://github.com/groupserver/gs.group.member.invite.csv/>

.. [#log] See the ``gs.group.member.log`` product
          <https://github.com/groupserver/gs.group.member.log/>

..  LocalWords:  NotifyNewMember loggedInUser txt msg html groupInfo
..  LocalWords:  joiningUser IGSJoiningUser NotifyAdmin
