Changelog
=========

3.3.2 (2015-03-11)
------------------

* [FR] Adding a French translation, thanks to `Razique Mahroua`_

.. _Razique Mahroua:
   https://www.transifex.com/accounts/profile/Razique/

3.3.1 (2015-02-20)
------------------

* Updated the translations to better work with Transifex_

_Transifex: https://www.transifex.com/projects/p/gs-group-member-join/


3.3.0 (2014-10-10)
------------------

* Added internationalisation
* Update of the notifications
* Pointed to GitHub_ as the primary code repository
* Renamed the reStructuredText files as such

.. _GitHub: https://github.com/groupserver/gs.group.member.join

3.2.2 (2014-06-13)
------------------

* Switching to Unicode literals
* Following the form base-class to ``gs.content.form.base``

3.2.1 (2014-02-28)
------------------

* Ensure the headers are in ASCII.
* Ensure the old ``Content-type`` is set after the notifications
  are sent

3.2.0 (2013-10-11)
------------------

* Using the new email base-class
* Added notes about ``userEmailInfo`` so it is not deleted!
* Metadata update

3.1.2 (2013-07-17)
------------------

* Fixing the ``Content-type`` header

3.1.1 (2013-05-28)
------------------

* Dropping the old *Join* link from the *Us bar.*

3.1.0 (2013-04-24)
------------------

* Using the standard group-visibility classes

3.0.0 (2013-03-21)
------------------

* Update for the new UI
* Changing the marker-interface that is used
* Code cleanup


2.1.1 (2013-01-22)
------------------

* Making links relative to the base of the site
* Updating where the Admin link goes

2.1.0 (2012-08-02)
------------------

* Add access to the new member's email address
* Update the SQLAlchemy code

2.0.1 (2012-02-22)
------------------

* Fix for the ``join`` event

2.0.0 (2012-01-11)
------------------

* Added new file-system side notifications for
  
  + Welcome
  + New member

* Raise a ``join`` event when someone joins a group.

1.2.0 (2011-04-07)
------------------

* Use the standard code for displaying feedback messages
* Handle corner cases better
* Switch to a standard ``GroupForm`` for the Join page

1.1.0 (2010-11-25)
------------------

* Added an adaptor from a ``CustomUser`` to a ``JoiningUser``.

1.0.3 (2010-10-07)
------------------

* Following the radio-button code

1.0.2 (2010-08-12)
------------------

* Better handling of Anonymous
* Fixing the ``context``

1.0.1 (2010-08-02)
------------------

* Adding the audit-event factory

1.0.0 (2010-07-29)
------------------

* Initial release, moving the page here from ``Products.GSGroupMember``

..  LocalWords:  Changelog Transifex GitHub reStructuredText
