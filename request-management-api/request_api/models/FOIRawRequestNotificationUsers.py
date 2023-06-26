from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from datetime import datetime as datetime2, timezone
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.expression import distinct
from sqlalchemy import text
import logging
import json
from sqlalchemy.sql.sqltypes import DateTime, String, Date
from sqlalchemy.orm import relationship, backref, aliased
from sqlalchemy import insert, and_, or_, text, func, literal, cast, asc, desc, case, nullsfirst, nullslast, TIMESTAMP, extract
from .FOIAssignees import FOIAssignee
from .FOIRawRequests import FOIRawRequest
from .FOIMinistryRequests import FOIMinistryRequest
#from .FOIRequestNotificationUsers import FOIRequestNotificationUser
from .FOIRawRequestNotifications import FOIRawRequestNotification
from .FOIRawRequestWatchers import FOIRawRequestWatcher
from .FOIUsers import FOIUser
from .NotificationTypes import NotificationType

class FOIRawRequestNotificationUser(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRawRequestNotificationUsers' 
    # Defining the columns
    notificationuserid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    notificationid = db.Column(db.Integer,ForeignKey('FOIRawRequestNotifications.notificationid'))
    userid = db.Column(db.String(100), unique=False, nullable=True)
    isdeleted = db.Column(db.Boolean, unique=False, nullable=True, default=False)
    created_at = db.Column(db.DateTime, default=datetime2.now)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    notificationusertypeid = db.Column(db.Integer,nullable=False)


    @classmethod
    def dismissnotification(cls, notificationuserid, userid='system'):
        exists = bool(db.session.query(FOIRawRequestNotificationUser.notificationuserid).filter_by(notificationuserid=notificationuserid).first())
        if exists == False:
            return DefaultMethodResult(False,'Invalid ID',notificationuserid)
        db.session.query(FOIRawRequestNotificationUser).filter(FOIRawRequestNotificationUser.notificationuserid == notificationuserid).update({FOIRawRequestNotificationUser.isdeleted: True, FOIRawRequestNotificationUser.updatedby: userid,
                            FOIRawRequestNotificationUser.updated_at: datetime2.now()})
        db.session.commit()  
        return DefaultMethodResult(True,'Notification deleted',notificationuserid)

    @classmethod
    def dismissnotificationbyuser(cls, userid):
        db.session.query(FOIRawRequestNotificationUser).filter(FOIRawRequestNotificationUser.userid == userid).update({FOIRawRequestNotificationUser.isdeleted: True, FOIRawRequestNotificationUser.updatedby: userid,
                            FOIRawRequestNotificationUser.updated_at: datetime2.now()})
        db.session.commit()  
        return DefaultMethodResult(True,'Notifications deleted for user',userid)

    @classmethod
    def dismissnotificationbyuserandtype(cls, userid, notificationusertypeid):
        db.session.query(FOIRawRequestNotificationUser).filter(FOIRawRequestNotificationUser.userid == userid, FOIRawRequestNotificationUser.notificationusertypeid == notificationusertypeid).update({FOIRawRequestNotificationUser.isdeleted: True, FOIRawRequestNotificationUser.updatedby: userid,
                            FOIRawRequestNotificationUser.updated_at: datetime2.now()})
        db.session.commit()  
        return DefaultMethodResult(True,'Notifications deleted for user',userid)

    @classmethod 
    def getnotificationsbyid(cls, notificationuserid):
        notifications = []
        try:
            sql = """select notificationid, count(1) as relcount from "FOIRawRequestNotificationUsers" frnu 
                        where notificationid in (select notificationid from "FOIRawRequestNotificationUsers" frnu  where notificationuserid  = :notificationuserid) group by notificationid """
            rs = db.session.execute(text(sql), {'notificationuserid': notificationuserid})
            for row in rs:
                notifications.append({"notificationid": row["notificationid"], "count" : row["relcount"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return notifications
    
    @classmethod 
    def getnotificationsbyuser(cls, userid):
        notifications = []
        try:
            sql = """select notificationid, count(1) as relcount from "FOIRawRequestNotificationUsers" frnu 
                        where notificationid in (select notificationid from "FOIRawRequestNotificationUsers" frnu  where userid = :userid) group by notificationid """
            rs = db.session.execute(text(sql), {'userid': userid})
            for row in rs:
                notifications.append({"notificationid": row["notificationid"], "count" : row["relcount"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return notifications

    @classmethod 
    def getnotificationsbyuserandtype(cls, userid, notificationusertypeid):
        notifications = []
        try:
            sql = """select notificationid, count(1) as relcount from "FOIRawRequestNotificationUsers" frnu 
                        where notificationid in (select notificationid from "FOIRawRequestNotificationUsers" frnu  where userid = :userid and notificationusertypeid = :notificationusertypeid) group by notificationid """
            rs = db.session.execute(text(sql), {'userid': userid, 'notificationusertypeid': notificationusertypeid})
            for row in rs:
                notifications.append({"notificationid": row["notificationid"], "count" : row["relcount"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return notifications

    @classmethod
    def dismissbynotificationid(cls, notificationids, userid='system'):
        db.session.query(FOIRawRequestNotificationUser).filter(FOIRawRequestNotificationUser.notificationid.in_(notificationids)).update({FOIRawRequestNotificationUser.isdeleted: True, FOIRawRequestNotificationUser.updatedby: userid,
                            FOIRawRequestNotificationUser.updated_at: datetime2.now()}, synchronize_session=False)
        db.session.commit()  
        return DefaultMethodResult(True,'Notifications deleted for id',notificationids)  
     
    @classmethod
    def getnotificationidsbyuserandid(cls, userid, notificationids):
        ids = []
        try:
            sql = """select notificationid from "FOIRawRequestNotificationUsers" where userid = :userid and notificationid = ANY(:notificationids) """
            rs = db.session.execute(text(sql), {'userid': userid, 'notificationids': notificationids})
            for row in rs:
                ids.append(row["notificationid"])
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return ids
    
    # Begin of Dashboard functions

    @classmethod
    def getbasequery(cls, foiuser, foicreator, additionalfilter=None, userid=None, isiaorestrictedfilemanager=False):
        _session = db.session

        #rawrequests
        #subquery for getting the latest version
        subquery_maxversion = _session.query(FOIRawRequest.requestid, func.max(FOIRawRequest.version).label('max_version')).group_by(FOIRawRequest.requestid).subquery()
        joincondition = [
            subquery_maxversion.c.requestid == FOIRawRequest.requestid,
            subquery_maxversion.c.max_version == FOIRawRequest.version,
        ]

        subquery_ministry_maxversion = _session.query(FOIMinistryRequest.foiministryrequestid, FOIMinistryRequest.axisrequestid, func.max(FOIMinistryRequest.version).label('max_version')).group_by(FOIMinistryRequest.foiministryrequestid, FOIMinistryRequest.axisrequestid).subquery()
        joincondition_ministry = [
            subquery_ministry_maxversion.c.foiministryrequestid == FOIMinistryRequest.foiministryrequestid,
            subquery_ministry_maxversion.c.max_version == FOIMinistryRequest.version
        ]

        

        ministry_closed_query = _session.query(
                                   FOIMinistryRequest.axisrequestid
                                ).join(
                                        subquery_ministry_maxversion, and_(*joincondition_ministry)
                                ).filter(FOIMinistryRequest.requeststatusid == 3)
        
        subquery_tag_notification = _session.query(
                                        FOIRawRequestNotification.axisnumber,
                                        FOIRawRequestNotification.notificationid, 
                                        FOIRawRequestNotification.notification, 
                                        FOIRawRequestNotificationUser.created_at,
                                        FOIRawRequestNotificationUser.createdby,
                                        FOIRawRequestNotificationUser.userid
                                        ).join(
                                        FOIRawRequestNotificationUser,
                                        and_(FOIRawRequestNotificationUser.notificationid == FOIRawRequestNotification.notificationid, 
                                             FOIRawRequestNotificationUser.userid == userid),
                                        ).join(
                                        NotificationType,
                                        and_(FOIRawRequestNotification.notificationtypeid == NotificationType.notificationtypeid, NotificationType.name == 'Tagged User Comments'),
                                        ).subquery()
        
        axisrequestid = case([
            (FOIRawRequest.axisrequestid.is_(None),
            'U-00' + cast(FOIRawRequest.requestid, String)),
            ],
            else_ = cast(FOIRawRequest.axisrequestid, String)).label('axisRequestId')

        assignedtoformatted = case([
                            (and_(FOIAssignee.lastname.isnot(None), FOIAssignee.firstname.isnot(None)),
                             func.concat(FOIAssignee.lastname, ', ', FOIAssignee.firstname)),
                            (and_(FOIAssignee.lastname.isnot(None), FOIAssignee.firstname.is_(None)),
                             FOIAssignee.lastname),
                            (and_(FOIAssignee.lastname.is_(None), FOIAssignee.firstname.isnot(None)),
                             FOIAssignee.firstname),
                            (and_(FOIAssignee.lastname.is_(None), FOIAssignee.firstname.is_(None), FOIRawRequest.assignedgroup.is_(None)),
                             'Unassigned'),
                           ],
                           else_ = FOIRawRequest.assignedgroup).label('assignedToFormatted')
        
        userformatted = case([
                            (and_(foiuser.lastname.isnot(None), foiuser.firstname.isnot(None)),
                             func.concat(foiuser.lastname, ', ', foiuser.firstname)),
                            (and_(foiuser.lastname.isnot(None), foiuser.firstname.is_(None)),
                             foiuser.lastname),
                            (and_(foiuser.lastname.is_(None), foiuser.firstname.isnot(None)),
                             foiuser.firstname),
                           ],
                           else_ = FOIRawRequestNotificationUser.userid).label('userformatted')


        creatorformatted = case([
                            (and_(foicreator.lastname.isnot(None), foicreator.firstname.isnot(None)),
                             func.concat(foicreator.lastname, ', ', foicreator.firstname)),
                            (and_(foicreator.lastname.isnot(None), foicreator.firstname.is_(None)),
                             foicreator.lastname),
                            (and_(foicreator.lastname.is_(None), foicreator.firstname.isnot(None)),
                             foicreator.firstname),                          ],
                           else_ = FOIRawRequestNotificationUser.createdby).label('creatorformatted')

        messageformatted = case([
                            (FOIRawRequestNotification.notification["message"].astext.cast(String).isnot(None),
                             FOIRawRequestNotification.notification["message"].astext.cast(String)),                            
                           ],
                           else_ = None).label('notification')

        typeformatted = case([
                            ( NotificationType.name.isnot(None),
                             NotificationType.name),                            
                           ],
                           else_ = None).label('notificationtype')

        description = case([
                            (FOIRawRequest.status == 'Unopened',
                             FOIRawRequest.requestrawdata['descriptionTimeframe']['description'].astext),
                           ],
                           else_ = FOIRawRequest.requestrawdata['description'].astext).label('description')
        

        selectedcolumns = [
            axisrequestid,  
            FOIRawRequest.status.label('status'),          
            #FOIRawRequestNotification.notification["message"].label('notification'),
            messageformatted,
            FOIRawRequestNotificationUser.userid.label('to'),
            FOIRawRequestNotificationUser.createdby.label('createdby'),
            FOIRawRequestNotificationUser.created_at.label('createdat'),
            FOIRawRequest.assignedgroup.label('assignedGroup'),
            FOIRawRequest.assignedto.label('assignedTo'),
            literal(None).label('assignedministrygroup'),
            literal(None).label('assignedministryperson'),
            FOIAssignee.firstname.label('assignedToFirstName'),
            FOIAssignee.lastname.label('assignedToLastName'),            
            literal(None).label('assignedministrypersonFirstName'),
            literal(None).label('assignedministrypersonLastName'),
            assignedtoformatted,
            literal(None).label('ministryAssignedToFormatted'),
            FOIRawRequestNotificationUser.notificationuserid.label('id'),
            FOIRawRequest.requestid.label('rawrequestid'),
            literal(None).label('requestid'),
            literal(None).label('ministryrequestid'),
            FOIRawRequestNotification.idnumber.label('idnumber'),
            foiuser.firstname.label('userFirstName'),
            foiuser.lastname.label('userLastName'),
            foicreator.firstname.label('creatorFirstName'),
            foicreator.lastname.label('creatorLastName'),
            #NotificationType.name.label('notificationtype'),
            typeformatted,
            userformatted.label('userFormatted'),
            creatorformatted.label('creatorFormatted'),
            description
        ]

        basequery = _session.query(
                                        *selectedcolumns
                                ).join(
                                        subquery_maxversion, and_(*joincondition)
                                ).join(
                                        FOIAssignee, FOIAssignee.username == FOIRawRequest.assignedto, isouter=True
                                ).join(
                                        FOIRawRequestNotification,
                                        and_(FOIRawRequestNotification.idnumber == 'U-00' + cast(FOIRawRequest.requestid, String), 
                                             FOIRawRequestNotification.axisnumber.notin_(ministry_closed_query)),
                                    isouter=True  
                                ).join(
                                        FOIRawRequestNotificationUser,
                                        and_(FOIRawRequestNotificationUser.notificationid == FOIRawRequestNotification.notificationid),
                                    isouter=True  
                                ).join(
                                        NotificationType,
                                        and_(FOIRawRequestNotification.notificationtypeid == NotificationType.notificationtypeid, NotificationType.name != 'Tagged User Comments'),
                                ).join(
                                        foiuser, foiuser.preferred_username == FOIRawRequestNotificationUser.userid, isouter=True  
                                ).join(
                                        foicreator, foicreator.preferred_username == FOIRawRequestNotificationUser.createdby, isouter=True  
                                ).join(
                                subquery_tag_notification, 
                                and_(subquery_tag_notification.c.userid == FOIRawRequestNotificationUser.userid), 
                                isouter=True  
                            )
        
        if additionalfilter is None:
            if(isiaorestrictedfilemanager == True):
                return basequery.filter(FOIRawRequest.status.notin_(['Archived']))
            else:
                subquery_watchby = FOIRawRequestWatcher.getrequestidsbyuserid(userid)

                return basequery.join(
                                    subquery_watchby,
                                    subquery_watchby.c.requestid == FOIRawRequest.requestid,
                                    isouter=True
                                ).filter(
                                    and_(
                                        FOIRawRequest.status.notin_(['Archived']),
                                        or_(
                                            FOIRawRequest.isiaorestricted == False,
                                            and_(FOIRawRequest.isiaorestricted == True, FOIRawRequest.assignedto == userid),
                                            and_(FOIRawRequest.isiaorestricted == True, subquery_watchby.c.watchedby == userid))))
        else:
            if(additionalfilter == 'watchingRequests' and userid is not None):
                #watchby
                subquery_watchby = FOIRawRequestWatcher.getrequestidsbyuserid(userid)
                return basequery.join(subquery_watchby, subquery_watchby.c.requestid == FOIRawRequest.requestid).filter(FOIRawRequest.status.notin_(['Archived']))
            elif(additionalfilter == 'myRequests'):
                #myrequest
                return basequery.filter(and_(FOIRawRequest.status.notin_(['Archived']), or_(FOIRawRequest.assignedto == userid, subquery_tag_notification.c.userid == userid)))
            else:
                if(isiaorestrictedfilemanager == True):
                    return basequery.filter(FOIRawRequest.status.notin_(['Archived']))
                else:
                    return basequery.filter(
                        and_(
                            FOIRawRequest.status.notin_(['Archived']),
                            or_(FOIRawRequest.isiaorestricted == False, and_(FOIRawRequest.isiaorestricted == True, FOIRawRequest.assignedto == userid))))


    @classmethod
    def getrequestssubquery(cls, foiuser, foicreator, filterfields, keyword, additionalfilter, userid, isiaorestrictedfilemanager):
        basequery = FOIRawRequestNotificationUser.getbasequery(foiuser, foicreator, additionalfilter, userid, isiaorestrictedfilemanager)
        basequery = basequery.filter(FOIRawRequest.status != 'Unopened').filter(FOIRawRequest.status != 'Closed')
        #filter/search
        if(len(filterfields) > 0 and keyword is not None):
            filtercondition = FOIRawRequestNotificationUser.getfilterforrequestssubquery(filterfields, keyword)
            return basequery.filter(filtercondition)
        else:
            return basequery
        
    @classmethod
    def getfilterforrequestssubquery(cls, filterfields, keyword):
        keyword = keyword.lower()

        #filter/search
        filtercondition = []
        if(keyword != 'restricted'):
            for field in filterfields:
                _keyword = FOIRawRequestNotificationUser.getfilterkeyword(keyword, field)
                #if(field == 'idNumber'):
                    #keyword = keyword.replace('u-00', '')
                if(field == 'notification'):
                    filtercondition.append(FOIRawRequestNotification.notification["message"].astext.cast(String).ilike('%'+_keyword+'%'))
                elif(field == 'createdat'):
                    vkeyword = keyword.split('@')
                    _keyword = FOIRawRequestNotificationUser.getfilterkeyword(vkeyword[0], field)
                    _datevalue = _keyword.split('-')
                    _vkeyword = vkeyword[1].split(' ')
                    datecriteria = []
                    for n  in range(len(_datevalue)):
                        if '%Y' in _vkeyword[n]:
                            datecriteria.append(extract('year', FOIRawRequestNotificationUser.created_at) == _datevalue[n])
                        if '%b' in _vkeyword[n]:
                            datecriteria.append(extract('month', FOIRawRequestNotificationUser.created_at) == _datevalue[n])
                        if '%d' in _vkeyword[n]:
                            datecriteria.append(extract('day', FOIRawRequestNotificationUser.created_at) == _datevalue[n])
                    if len(datecriteria) > 0:
                        filtercondition.append(and_(*datecriteria))   
                else:
                    filtercondition.append(FOIRawRequestNotificationUser.findfield(field).ilike('%'+_keyword+'%'))
                
            filtercondition.append(FOIRawRequest.isiaorestricted == True)

        return or_(*filtercondition)
    
    
    
    @classmethod
    def getfilterkeyword(cls, keyword, field):
        _newkeyword = keyword
        if field != 'createdat':
            _newkeyword = _newkeyword.replace('@%Y %b %d','')
            _newkeyword = _newkeyword.replace('@%Y %b','')
            _newkeyword = _newkeyword.replace('@%Y','')
        if(field == 'idNumber'):
            _newkeyword = _newkeyword.replace('u-00', '')
        return _newkeyword
        
    @classmethod
    def findfield(cls, x):
        return {
            'to': FOIRawRequestNotificationUser.userid,
            'createdby' : FOIRawRequestNotificationUser.createdby,
            'axisRequestId' : cast(FOIRawRequest.axisrequestid, String),
            'assignedTo': FOIRawRequest.assignedto,
            'assignedToFirstName': FOIAssignee.firstname,
            'assignedToLastName': FOIAssignee.lastname,
            'description': FOIRawRequest.requestrawdata['description'].astext,
        }.get(x, cast(FOIRawRequest.requestid, String))
    
    """
    @classmethod
    def geteventpagination(cls, groups, page, size, sortingitems, sortingorders, filterfields, keyword, additionalfilter, userid, isiaorestrictedfilemanager, isministryrestrictedfilemanager=False):
        #ministry requests
        iaoassignee = aliased(FOIAssignee)
        ministryassignee = aliased(FOIAssignee)
        foiuser = aliased(FOIUser)
        foicreator = aliased(FOIUser)

        subquery_ministry_queue = FOIRequestNotificationUser.geteventsubquery(groups, filterfields, keyword, additionalfilter, userid, iaoassignee, ministryassignee, foiuser, foicreator, 'IAO', isiaorestrictedfilemanager, isministryrestrictedfilemanager)

        #sorting
        sortingcondition = FOIRawRequestNotificationUser.getsorting(sortingitems, sortingorders)
        #rawrequests
        if "Intake Team" in groups or groups is None:                
            subquery_rawrequest_queue = FOIRawRequestNotificationUser.getrequestssubquery(foiuser, foicreator, filterfields, keyword, additionalfilter, userid, isiaorestrictedfilemanager)
            query_full_queue = subquery_rawrequest_queue.union(subquery_ministry_queue)
            return query_full_queue.order_by(*sortingcondition).paginate(page=page, per_page=size)
        else:
            return subquery_ministry_queue.order_by(*sortingcondition).paginate(page=page, per_page=size)
    """
    @classmethod
    def getsorting(cls, sortingitems, sortingorders):
        sortingcondition = []
        if(len(sortingitems) > 0 and len(sortingorders) > 0 and len(sortingitems) == len(sortingorders)):
            for field in sortingitems:
                if(FOIRawRequestNotificationUser.validatefield(field)):
                    order = sortingorders.pop(0)
                    if(order == 'desc'):
                        sortingcondition.append(nullslast(desc(field)))
                    else:
                        sortingcondition.append(nullsfirst(asc(field)))
        #default sorting
        if(len(sortingcondition) == 0):
            sortingcondition.append(desc('createdat'))

        #always sort by created_at last to prevent pagination collisions
        sortingcondition.append(desc('createdat'))
        
        return sortingcondition
    
    @classmethod
    def validatefield(cls, x):
        validfields = [
            'notification',
            'createdby',
            'to',
            'axisRequestId',
            'createdat',
            'assignedTo',
            'assignedToFirstName',
            'assignedToLastName',
            'assignedToFormatted',
            'ministryAssignedToFormatted',
            'userFirstName',
            'userLastName',
            'userFormatted',
            'creatorFirstName',
            'creatorLastName',
            'creatorFormatted'      
        ]
        if x in validfields:
            return True
        else:
            return False
    # End of Dashboard functions
        
class FOIRawRequestNotificationUserSchema(ma.Schema):
    class Meta:
        fields = ('notificationid', 'userid','notificationusertypeid','created_at','createdby','updated_at','updatedby') 