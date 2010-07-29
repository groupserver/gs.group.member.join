# coding=utf-8
from pytz import UTC
from datetime import datetime
from zope.component import createObject
from zope.component.interfaces import IFactory
from zope.interface import implements, implementedBy
from Products.XWFCore.XWFUtils import munge_date
from Products.CustomUserFolder.userinfo import userInfo_to_anchor
from Products.CustomUserFolder.interfaces import IGSUserInfo
from Products.GSAuditTrail import IAuditEvent, BasicAuditEvent, AuditQuery
from Products.GSAuditTrail.utils import event_id_from_data

SUBSYSTEM = 'gs.group.member.join'
import logging
log = logging.getLogger(SUBSYSTEM) #@UndefinedVariable

UNKNOWN        = '0'  # Unknown is always "0"
JOIN_GROUP     = '1'
JOIN_SITE      = '2'
MODERATED      = '3'

class JoinAuditEventFactory(object):
    """A Factory for joining events.
    """
    implements(IFactory)

    title=u'GroupServer Joining Audit Event Factory'
    description=u'Creates a GroupServer event auditor for joining events'

    def __call__(self, context, event_id, code, date,
        userInfo, instanceUserInfo, siteInfo, groupInfo,
        instanceDatum='', supplementaryDatum='', subsystem=''):
        """Create an event
        """
        assert subsystem == SUBSYSTEM, 'Subsystems do not match'
        
        if code == JOIN_GROUP:
            event = JoinEvent(context, event_id, date, instanceUserInfo,
                                siteInfo, groupInfo)
        elif code == JOIN_SITE:
            event = JoinSiteEvent(context, event_id, date, 
                        instanceUserInfo, siteInfo, groupInfo)
        elif code == MODERATED:
            event = ModerateEvent(context, event_id, date,
                                    instanceUserInfo, siteInfo, 
                                    groupInfo)
        else:
            event = BasicAuditEvent(context, event_id, UNKNOWN, date, 
              userInfo, instanceUserInfo, siteInfo, groupInfo, 
              instanceDatum, supplementaryDatum, SUBSYSTEM)
        assert event
        return event
    
    def getInterfaces(self):
        return implementedBy(BasicAuditEvent)
  
class JoinEvent(BasicAuditEvent):
    ''' An audit-trail event representing a person joining a group.
    '''
    implements(IAuditEvent)

    def __init__(self, context, id, d, instanceUserInfo, 
                  siteInfo, groupInfo):
        """ Create a join event
        """
        BasicAuditEvent.__init__(self, context, id,  JOIN_GROUP, d, None,
          instanceUserInfo, siteInfo, groupInfo, None, None, 
          SUBSYSTEM)
          
    def __str__(self):
        retval = u'%s (%s) joined the group %s (%s) on %s (%s).' %\
           (self.instanceUserInfo.name, self.instanceUserInfo.id,
            self.groupInfo.name,        self.groupInfo.id,
            self.siteInfo.name,         self.siteInfo.id)
        retval = retval.encode('ascii', 'ignore')
        return retval
    
    @property
    def xhtml(self):
        cssClass = u'audit-event groupserver-group-member-join-%s' %\
          self.code
        retval = u'<span class="%s">Joined %s</span>'%\
          (cssClass, self.groupInfo.name)
        
        retval = u'%s (%s)' % \
          (retval, munge_date(self.context, self.date))
        return retval

class JoinSiteEvent(BasicAuditEvent):
    ''' An audit-trail event representing a person joining a site.
    '''
    implements(IAuditEvent)

    def __init__(self, context, id, d, instanceUserInfo, 
                  siteInfo, groupInfo):
        """ Create a join event
        """
        BasicAuditEvent.__init__(self, context, id,  JOIN_SITE, d, None,
          instanceUserInfo, siteInfo, groupInfo, None, None, 
          SUBSYSTEM)
          
    def __str__(self):
        retval = u'%s (%s) joined the site %s (%s).' %\
           (self.instanceUserInfo.name, self.instanceUserInfo.id,
            self.siteInfo.name,         self.siteInfo.id)
        retval = retval.encode('ascii', 'ignore')
        return retval
    
    @property
    def xhtml(self):
        cssClass = u'audit-event groupserver-group-member-join-%s' %\
          self.code
        retval = u'<span class="%s">Joined %s</span>'%\
          (cssClass, self.siteInfo.name)
        
        retval = u'%s (%s)' % \
          (retval, munge_date(self.context, self.date))
        return retval


class ModerateEvent(BasicAuditEvent):
    ''' An audit-trail event representing a person being moderated
    when joining a group.
    '''
    implements(IAuditEvent)

    def __init__(self, context, id, d, instanceUserInfo, 
                  siteInfo, groupInfo):
        """ Create a join event
        """
        BasicAuditEvent.__init__(self, context, id,  MODERATED, d, None,
          instanceUserInfo, siteInfo, groupInfo, None, None, 
          SUBSYSTEM)
          
    def __str__(self):
        retval = u'%s (%s) will be moderated when posting to '\
            u'%s (%s) on %s (%s).' %\
           (self.instanceUserInfo.name, self.instanceUserInfo.id,
            self.groupInfo.name,        self.groupInfo.id,
            self.siteInfo.name,         self.siteInfo.id)
        retval = retval.encode('ascii', 'ignore')
        return retval
    
    @property
    def xhtml(self):
        cssClass = u'audit-event groupserver-group-member-join-%s' %\
          self.code
        retval = u'<span class="%s">Being set to moderated %s</span>'%\
          (cssClass, self.groupInfo.name)
        
        retval = u'%s (%s)' % \
          (retval, munge_date(self.context, self.date))
        return retval

class JoinAuditor(object):
    """An auditor for joining a group.
    """
    def __init__(self, context, groupInfo, instanceUserInfo):
        """Create a status auditor.
        """
        self.context = context
        self.instanceUserInfo = instanceUserInfo
        self.__siteInfo = None
        self.groupInfo = groupInfo
        self.__factory = None
        self.__queries = None

    @property
    def siteInfo(self):
        if self.__siteInfo == None:
            self.__siteInfo =\
              createObject('groupserver.SiteInfo', self.context)
        return self.__siteInfo

    @property
    def factory(self):
        if self.__factory == None:
            self.__factory = JoinAuditEventFactory()
        return self.__factory
        
    @property
    def queries(self):
        if self.__queries == None:
            self.__queries = AuditQuery(self.context.zsqlalchemy)
        return self.__queries

    def info(self, code, instanceDatum='', supplementaryDatum=''):
        """Log an info event to the audit trail.
            * Creates an ID for the new event,
            * Writes the instantiated event to the audit-table, and
            * Writes the event to the standard Python log.
        """
        d = datetime.now(UTC)
        eventId = event_id_from_data(self.instanceUserInfo,
                    self.instanceUserInfo, self.siteInfo, code, 
                    instanceDatum, 
                    '%s-%s' % (self.groupInfo.name, self.groupInfo.id))
            
        e = self.factory(self.context, eventId,  code, d,
                self.instanceUserInfo, self.instanceUserInfo, 
                self.siteInfo, self.groupInfo, instanceDatum, 
                supplementaryDatum, SUBSYSTEM)
            
        self.queries.store(e)
        log.info(e)
        return e

