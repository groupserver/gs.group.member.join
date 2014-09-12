:mod:`gs.group.member.join` API
===============================

There are two public components to the API: one for creating a
user that can `join groups`_, and the `join-group event`_ that is
raised when someone joins a group.

Join groups
-----------

.. autoclass:: gs.group.member.join.joininguser.JoiningUser
   :members: joinableGroups, silent_join

Example
~~~~~~~

It is rare that the :class:`JoiningUser` class is instantiated
directly.  Instead a user-instance is *adapted* to a joining
user.

.. code-block:: python

    joiningUser = IGSJoiningUser(userInfo)
    joiningUser.silent_join(groupInfo)

The :class:`gs.group.member.join.interfaces.IGSJoiningUser`
interface is used for the adapter.


Join-group event
----------------

.. autoclass:: gs.group.member.join.event.IGSJoinGroupEvent
   :members:

Example
~~~~~~~

Listen for this event being raised by **subscribing** to the
:class:`IGSJoinGroupEvent` being raised on a user-instance. In
the ZCML this would look like the following:

.. code-block:: xml

  <subscriber
     for="Products.CustomUserFolder.interfaces.ICustomUser
          gs.group.member.join.event.IGSJoinGroupEvent"
     handler=".usergroupadd.member_added" />

The :func:`member_added` function would receive the user-instance
and event-instance as its parameters.

.. code-block:: python

    def member_added(context, event):
        groupInfo = event.groupInfo
        userInfo = event.memberInfo

:See also: `zope.event <http://docs.zope.org/zope.event/>`_
