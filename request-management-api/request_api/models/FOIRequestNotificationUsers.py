from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from datetime import datetime as datetime2, time
from sqlalchemy.orm import relationship,backref, aliased
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.functions import coalesce
from sqlalchemy import or_, and_, text, func, literal, cast, case, nullslast, nullsfirst, desc, asc, extract
from sqlalchemy.sql.sqltypes import String
from sqlalchemy.sql.expression import distinct
from sqlalchemy import text
from flask import current_app
import pytz
import logging
import json
f = open('common/notificationtypes.json', encoding="utf8")
notificationtypes_cache = json.load(f)


from .FOIRequestApplicantMappings import FOIRequestApplicantMapping
from .FOIRequestApplicants import FOIRequestApplicant
from .FOIRequestStatus import FOIRequestStatus
from .ApplicantCategories import ApplicantCategory
from .FOIRequestWatchers import FOIRequestWatcher
from .FOIRequests import FOIRequest
from .FOIRestrictedMinistryRequests import FOIRestrictedMinistryRequest
from .ProgramAreas import ProgramArea
from request_api.utils.enums import ProcessingTeamWithKeycloackGroup, IAOTeamWithKeycloackGroup
from .FOIAssignees import FOIAssignee
from .FOIRequestExtensions import FOIRequestExtension
from request_api.utils.enums import RequestorType
from request_api.utils.enums import StateName
from .FOIMinistryRequestSubjectCodes import FOIMinistryRequestSubjectCode
from .SubjectCodes import SubjectCode
from .FOIRequestStatus import FOIRequestStatus

from .FOIRawRequestNotifications import FOIRawRequestNotification
from .FOIRawRequestNotificationUsers import FOIRawRequestNotificationUser
from request_api.models.views.FOINotifications import FOINotifications
from request_api.models.views.FOIRequests import FOIRequests


class FOIRequestNotificationUser(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequestNotificationUsers' 
    # Defining the columns
    notificationuserid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    notificationid = db.Column(db.Integer,ForeignKey('FOIRequestNotifications.notificationid'))
    userid = db.Column(db.String(100), unique=False, nullable=True)
    isdeleted = db.Column(db.Boolean, unique=False, nullable=True, default=False)
    created_at = db.Column(db.DateTime, default=datetime2.now)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    notificationusertypelabel = db.Column(db.String(100),nullable=False)
    notificationusertypeid = db.Column(db.Integer,nullable=False)


    @classmethod
    def dismissnotification(cls, notificationuserid, userid='system'):
        exists = bool(db.session.query(FOIRequestNotificationUser.notificationuserid).filter_by(notificationuserid=notificationuserid).first())
        if exists == False:
            return DefaultMethodResult(False,'Invalid ID',notificationuserid)
        db.session.query(FOIRequestNotificationUser).filter(FOIRequestNotificationUser.notificationuserid == notificationuserid).update({FOIRequestNotificationUser.isdeleted: True, FOIRequestNotificationUser.updatedby: userid,
                            FOIRequestNotificationUser.updated_at: datetime2.now()})
        db.session.commit()  
        return DefaultMethodResult(True,'Notification deleted',notificationuserid)
    
    @classmethod
    def dismissnotificationbyuser(cls, userid):
        db.session.query(FOIRequestNotificationUser).filter(FOIRequestNotificationUser.userid == userid).update({FOIRequestNotificationUser.isdeleted: True, FOIRequestNotificationUser.updatedby: userid,
                            FOIRequestNotificationUser.updated_at: datetime2.now()})
        db.session.commit()  
        return DefaultMethodResult(True,'Notifications deleted for user',userid)

    @classmethod
    def dismissnotificationbyuserandtype(cls, userid, notificationusertypelabel):
        db.session.query(FOIRequestNotificationUser).filter(FOIRequestNotificationUser.userid == userid, FOIRequestNotificationUser.notificationusertypelabel == notificationusertypelabel).update({FOIRequestNotificationUser.isdeleted: True, FOIRequestNotificationUser.updatedby: userid,
                            FOIRequestNotificationUser.updated_at: datetime2.now()})
        db.session.commit()  
        return DefaultMethodResult(True,'Notifications deleted for user',userid)
    
    @classmethod
    def dismissbynotificationid(cls, notificationids, userid='system'):
        db.session.query(FOIRequestNotificationUser).filter(FOIRequestNotificationUser.notificationid.in_(notificationids)).update({FOIRequestNotificationUser.isdeleted: True, FOIRequestNotificationUser.updatedby: userid,
                            FOIRequestNotificationUser.updated_at: datetime2.now()}, synchronize_session=False)
        db.session.commit()  
        return DefaultMethodResult(True,'Notifications deleted for id',notificationids)  
    
    @classmethod 
    def getnotificationsbyid(cls, notificationuserid):
        notifications = []
        try:
            sql = """select notificationid, count(1) as relcount from "FOIRequestNotificationUsers" frnu 
                    where notificationid in (select notificationid from "FOIRequestNotificationUsers" frnu  where notificationuserid  = :notificationuserid) group by notificationid """
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
            sql = """select notificationid, count(1) as relcount from "FOIRequestNotificationUsers" frnu 
                    where notificationid in (select notificationid from "FOIRequestNotificationUsers" frnu  where userid = :userid) group by notificationid """
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
    def getnotificationsbyuserandtype(cls, userid, notificationusertypelabel):
        notifications = []
        try:
            sql = """select notificationid, count(1) as relcount from "FOIRequestNotificationUsers" frnu 
                    where notificationid in (select notificationid from "FOIRequestNotificationUsers" frnu  where userid = :userid and notificationusertypelabel = :notificationusertypelabel) group by notificationid """
            rs = db.session.execute(text(sql), {'userid': userid, 'notificationusertypelabel':notificationusertypelabel})
            for row in rs:
                notifications.append({"notificationid": row["notificationid"], "count" : row["relcount"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return notifications  
    
    @classmethod
    def getnotificationidsbyuserandid(cls, userid, notificationids):
        ids = []
        try:
            sql = """select notificationid from "FOIRequestNotificationUsers" where userid = :userid and notificationid = ANY(:notificationids) """
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
    def geteventsubquery(cls, daterangetype, fromdate, todate, groups, filterfields, keyword, additionalfilter, userid, requestby='IAO', isiaorestrictedfilemanager=False, isministryrestrictedfilemanager=False):
        #for queue/dashboard
        _session = db.session

        #aliase for getting ministry restricted flag from FOIRestrictedMinistryRequest
        ministry_restricted_requests = aliased(FOIRestrictedMinistryRequest)      
        #ministry filter for group/team
        ministryfilter = FOIRequestNotificationUser.getgroupfilters(groups)

        if daterangetype == 'eventDate' and (not fromdate or not todate):
            return _session.query().filter(False)

        if daterangetype == 'eventDate':
            pacific = pytz.timezone(current_app.config['LEGISLATIVE_TIMEZONE'])

            if isinstance(fromdate, str):
                fromdate = datetime2.strptime(fromdate, "%Y-%m-%d").date()
            if isinstance(todate, str):
                todate = datetime2.strptime(todate, "%Y-%m-%d").date()

            fromdate = pacific.localize(datetime2.combine(fromdate, time.min)).astimezone(pytz.utc)
            todate = pacific.localize(datetime2.combine(todate, time.max)).astimezone(pytz.utc)
        else:
            fromdate = None
            todate = None

        #filter/search
        if(len(filterfields) > 0 and keyword is not None):
            filtercondition = []
            if(keyword != "restricted"):
                for field in filterfields:
                    _keyword = FOIRequestNotificationUser.getfilterkeyword(keyword, field)       
                    filtercondition.append(FOIRequestNotificationUser.findfield(field).ilike('%'+_keyword+'%'))
            else:
                if(requestby == 'IAO'):
                    filtercondition.append(FOIRestrictedMinistryRequest.isrestricted == True)
                else:
                    filtercondition.append(ministry_restricted_requests.isrestricted == True)

        selectedcolumns = [  
            FOIRequests.crtid.label('crtid'),                          
            FOIRequests.axisrequestid.label('axisRequestId'),
            FOIRequests.rawrequestid.label('rawrequestid'),
            FOIRequests.foirequest_id.label('requestid'),
            FOIRequests.foiministryrequestid.label('ministryrequestid'),
            FOIRequests.status.label('status'),
            FOIRequests.assignedtoformatted.label('assignedToFormatted'),
            FOIRequests.ministryassignedtoformatted.label('ministryAssignedToFormatted'),          
            FOIRequests.description,
            FOINotifications.notificationtype.label('notificationtype'),
            FOINotifications.notification.label('notification'),                 
            FOINotifications.created_at.label('createdat'),  
            FOINotifications.createdatformatted.label('createdatformatted'),  
            FOINotifications.userformatted.label('userFormatted'),
            FOINotifications.creatorformatted.label('creatorFormatted'),
            FOINotifications.id.label('id')        
        ]

        notification_join_conditions = [FOINotifications.axisnumber == FOIRequests.axisrequestid]
        if fromdate:
            notification_join_conditions.append(FOINotifications.created_at >= fromdate)
        if todate:
            notification_join_conditions.append(FOINotifications.created_at <= todate)

        basequery = _session.query(
                                *selectedcolumns
                            ).join(
                                FOIRestrictedMinistryRequest,
                                and_(
                                    FOIRestrictedMinistryRequest.ministryrequestid == FOIRequests.foiministryrequestid,
                                    FOIRestrictedMinistryRequest.type == 'iao',
                                    FOIRestrictedMinistryRequest.isactive == True),
                                isouter=True
                            ).join(
                                ministry_restricted_requests,
                                and_(
                                    ministry_restricted_requests.ministryrequestid == FOIRequests.foiministryrequestid,
                                    ministry_restricted_requests.type == 'ministry',
                                    ministry_restricted_requests.isactive == True),
                                isouter=True
                            ).join(
                                FOINotifications,    
                                and_(*notification_join_conditions),
                            ).filter(FOIRequests.requeststatuslabel != StateName.closed.name)
            
        if(additionalfilter == 'watchingRequests'):
            #watchby
            #activefilter = and_(FOIMinistryRequest.isactive == True, FOIRequestStatus.isactive == True)

            subquery_watchby = FOIRequestWatcher.getrequestidsbyuserid(userid)
            dbquery = basequery.join(subquery_watchby, subquery_watchby.c.ministryrequestid == FOIRequests.foiministryrequestid)#.filter(activefilter)
        elif(additionalfilter == 'myRequests'):
            #myrequest
            if(requestby == 'IAO'):
                dbquery = basequery.filter(or_(and_(FOIRequests.assignedto == userid, ministryfilter),and_(FOINotifications.userid == userid, FOINotifications.notificationtypelabel == notificationtypes_cache['taggedusercomments']['notificationtypelabel'])))
            else:
                dbquery = basequery.filter(or_(and_(FOIRequests.assignedministryperson == userid, ministryfilter),and_(FOINotifications.userid == userid, FOINotifications.notificationtypelabel == notificationtypes_cache['taggedusercomments']['notificationtypelabel'])))
        else:
            if(isiaorestrictedfilemanager == True or isministryrestrictedfilemanager == True):
                dbquery = basequery
            else:
                if(requestby == 'IAO'):
                    dbquery = basequery.filter(or_(or_(FOIRestrictedMinistryRequest.isrestricted == False, FOIRestrictedMinistryRequest.isrestricted == None), and_(FOIRestrictedMinistryRequest.isrestricted == True, FOIRequests.assignedto == userid))).filter(ministryfilter)
                else:
                    dbquery = basequery.filter(or_(or_(ministry_restricted_requests.isrestricted == False, ministry_restricted_requests.isrestricted == None), and_(ministry_restricted_requests.isrestricted == True, FOIRequests.assignedministryperson == userid))).filter(ministryfilter)
                
        if(keyword is None):
            return dbquery
        else:
            return dbquery.filter(or_(*filtercondition))

    
    @classmethod
    def getgroupfilters(cls, groups):
        #ministry filter for group/team
        if groups is None:
            #ministryfilter = FOIMinistryRequest.isactive == True
            ministryfilter = None
        else:
            groupfilter = []
            for group in groups:
                if (group == IAOTeamWithKeycloackGroup.flex.value or group in ProcessingTeamWithKeycloackGroup.list()):
                    groupfilter.append(
                        and_(
                            FOIRequests.assignedgroup == group
                        )
                    )
                elif (group == IAOTeamWithKeycloackGroup.intake.value):
                    groupfilter.append(
                        or_(
                            FOIRequests.assignedgroup == group,
                            and_(
                                FOIRequests.assignedgroup == IAOTeamWithKeycloackGroup.flex.value,
                                FOIRequests.requeststatuslabel.in_([StateName.open.name])
                            )
                        )
                    )
                else:
                    groupfilter.append(
                        or_(
                            FOIRequests.assignedgroup == group,
                            and_(
                                FOIRequests.assignedministrygroup == group,
                                FOIRequests.requeststatuslabel.in_([StateName.callforrecords.name,StateName.recordsreview.name,StateName.feeestimate.name,StateName.consult.name,StateName.ministrysignoff.name,StateName.onhold.name,StateName.deduplication.name,StateName.harmsassessment.name,StateName.response.name,StateName.tagging.name,StateName.readytoscan.name,StateName.onholdother.name])
                            )
                        )
                    )

            ministryfilter = and_(
                                    or_(*groupfilter)
                                )
        
        return ministryfilter
    
    @classmethod
    def getfilterkeyword(cls, keyword, field):
        _newkeyword = keyword
        if(field == 'idNumber'):
            _newkeyword = _newkeyword.replace('u-00', '')
        return _newkeyword

    @classmethod
    def getsorting(cls, sortingitems, sortingorders):
        #sorting
        sortingcondition = []
        if(len(sortingitems) > 0 and len(sortingorders) > 0 and len(sortingitems) == len(sortingorders)):
            for field in sortingitems:
                order = sortingorders.pop(0)
                sortingcondition.append(FOIRequestNotificationUser.getfieldforsorting(field, order))

        #default sorting
        if(len(sortingcondition) == 0):
            sortingcondition.append(FOIRequestNotificationUser.findfield('createdat').desc())

        #always sort by created_at last to prevent pagination collisions
        sortingcondition.append(asc('created_at'))
        
        return sortingcondition
    
    @classmethod
    def getfieldforsorting(cls, field, order):
        if(order == 'desc'):
            return nullslast(FOIRequestNotificationUser.findfield(field).desc())
        else:
            return nullsfirst(FOIRequestNotificationUser.findfield(field).asc())

    @classmethod
    def findfield(cls, x):
        #add more fields here if need sort/filter/search more columns
        return {
            'axisRequestId' : FOIRequests.axisrequestid,
            'createdat': FOINotifications.created_at,
            'createdatformatted': FOINotifications.createdatformatted,
            'notification': FOINotifications.notification,
            'assignedToFormatted': FOIRequests.assignedtoformatted,
            'ministryAssignedToFormatted': FOIRequests.ministryassignedtoformatted,
            'userFormatted': FOINotifications.userformatted,
            'creatorFormatted': FOINotifications.creatorformatted
        }.get(x,  cast(FOIRequests.axisrequestid, String))
    
    # End of Dashboard functions
        
class FOIRequestNotificationUserSchema(ma.Schema):
    class Meta:
        fields = ('notificationid', 'userid','notificationusertypeid', 'notificationusertypelabel','created_at','createdby','updated_at','updatedby') 