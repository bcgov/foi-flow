from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from datetime import datetime as datetime2
from sqlalchemy.orm import relationship,backref, aliased
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.functions import coalesce
from sqlalchemy import or_, and_, text, func, literal, cast, case, nullslast, nullsfirst, desc, asc, extract
from sqlalchemy.sql.sqltypes import String
from sqlalchemy.sql.expression import distinct
from sqlalchemy import text
import logging
import json


from .FOIRequestApplicantMappings import FOIRequestApplicantMapping
from .FOIRequestApplicants import FOIRequestApplicant
from .FOIRequestStatus import FOIRequestStatus
from .ApplicantCategories import ApplicantCategory
from .FOIRequestWatchers import FOIRequestWatcher
from .FOIMinistryRequests import FOIMinistryRequest
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
from .FOIRequestNotifications import FOIRequestNotification
from .FOIUsers import FOIUser
from .NotificationTypes import NotificationType
from .FOIRequestStatus import FOIRequestStatus

from .FOIRawRequestNotifications import FOIRawRequestNotification
from .FOIRawRequestNotificationUsers import FOIRawRequestNotificationUser


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
    def dismissnotificationbyuserandtype(cls, userid, notificationusertypeid):
        db.session.query(FOIRequestNotificationUser).filter(FOIRequestNotificationUser.userid == userid, FOIRequestNotificationUser.notificationusertypeid == notificationusertypeid).update({FOIRequestNotificationUser.isdeleted: True, FOIRequestNotificationUser.updatedby: userid,
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
    def getnotificationsbyuserandtype(cls, userid, notificationusertypeid):
        notifications = []
        try:
            sql = """select notificationid, count(1) as relcount from "FOIRequestNotificationUsers" frnu 
                    where notificationid in (select notificationid from "FOIRequestNotificationUsers" frnu  where userid = :userid and notificationusertypeid = :notificationusertypeid) group by notificationid """
            rs = db.session.execute(text(sql), {'userid': userid, 'notificationusertypeid':notificationusertypeid})
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
    def geteventsubquery(cls, groups, filterfields, keyword, additionalfilter, userid, iaoassignee, ministryassignee, foiuser, foicreator, requestby='IAO', isiaorestrictedfilemanager=False, isministryrestrictedfilemanager=False):
        #for queue/dashboard
        _session = db.session

        #subquery for getting latest version & proper group/team for FOIMinistryRequest
        subquery_ministry_maxversion = _session.query(FOIMinistryRequest.axisrequestid, FOIMinistryRequest.foiministryrequestid, func.max(FOIMinistryRequest.version).label('max_version')).group_by(FOIMinistryRequest.foiministryrequestid,FOIMinistryRequest.axisrequestid).subquery()
        joincondition_ministry = [
            subquery_ministry_maxversion.c.foiministryrequestid == FOIMinistryRequest.foiministryrequestid,
            subquery_ministry_maxversion.c.max_version == FOIMinistryRequest.version,
        ]

        #aliase for getting ministry restricted flag from FOIRestrictedMinistryRequest
        ministry_restricted_requests = aliased(FOIRestrictedMinistryRequest)
        
         #ministry filter for group/team
        ministryfilter = FOIRequestNotificationUser.getgroupfilters(groups)

        notificationquery = FOIRequestNotificationUser.getnotificationquery(subquery_ministry_maxversion, joincondition_ministry, ministryfilter, additionalfilter, requestby, userid)

        assignedtoformatted = case([
                            (and_(iaoassignee.lastname.isnot(None), iaoassignee.firstname.isnot(None)),
                             func.concat(iaoassignee.lastname, ', ', iaoassignee.firstname)),
                            (and_(iaoassignee.lastname.isnot(None), iaoassignee.firstname.is_(None)),
                             iaoassignee.lastname),
                            (and_(iaoassignee.lastname.is_(None), iaoassignee.firstname.isnot(None)),
                             iaoassignee.firstname),
                           ],
                           else_ = FOIMinistryRequest.assignedgroup).label('assignedToFormatted')

        ministryassignedtoformatted = case([
                            (and_(ministryassignee.lastname.isnot(None), ministryassignee.firstname.isnot(None)),
                             func.concat(ministryassignee.lastname, ', ', ministryassignee.firstname)),
                            (and_(ministryassignee.lastname.isnot(None), ministryassignee.firstname.is_(None)),
                             ministryassignee.lastname),
                            (and_(ministryassignee.lastname.is_(None), ministryassignee.firstname.isnot(None)),
                             ministryassignee.firstname),
                           ],
                           else_ = FOIMinistryRequest.assignedministrygroup).label('ministryAssignedToFormatted')
        
        userformatted = case([
                            (and_(foiuser.lastname.isnot(None), foiuser.firstname.isnot(None)),
                             func.concat(foiuser.lastname, ', ', foiuser.firstname)),
                            (and_(foiuser.lastname.isnot(None), foiuser.firstname.is_(None)),
                             foiuser.lastname),
                            (and_(foiuser.lastname.is_(None), foiuser.firstname.isnot(None)),
                             foiuser.firstname),
                           ],
                           else_ = notificationquery.c.userid).label('userformatted')


        creatorformatted = case([
                            (and_(foicreator.lastname.isnot(None), foicreator.firstname.isnot(None)),
                             func.concat(foicreator.lastname, ', ', foicreator.firstname)),
                            (and_(foicreator.lastname.isnot(None), foicreator.firstname.is_(None)),
                             foicreator.lastname),
                            (and_(foicreator.lastname.is_(None), foicreator.firstname.isnot(None)),
                             foicreator.firstname),
                           ],
                           else_ =  notificationquery.c.createdby).label('creatorformatted')
        
        
        #filter/search
        if(len(filterfields) > 0 and keyword is not None):
            filtercondition = []
            if(keyword != "restricted"):
                for field in filterfields:
                    _keyword = FOIRequestNotificationUser.getfilterkeyword(keyword, field)       
                    if field == "notification":
                        filtercondition.append(FOIRequestNotification.notification["message"].astext.cast(String).ilike('%'+_keyword+'%'))
                    elif field == "createdat":
                        vkeyword = keyword.split('@')
                        _keyword = FOIRequestNotificationUser.getfilterkeyword(vkeyword[0], field)
                        _datevalue = _keyword.split('-')
                        datecriteria = []
                        _vkeyword = vkeyword[1].split(' ')
                        for n  in range(len(_datevalue)):
                            if '%Y' in _vkeyword[n]:
                                datecriteria.append(extract('year',FOIRequestNotificationUser.created_at) == _datevalue[n])
                            if '%b' in _vkeyword[n]:
                                datecriteria.append(extract('month', FOIRequestNotificationUser.created_at) == _datevalue[n])
                            if '%d' in _vkeyword[n]:
                                datecriteria.append(extract('day', FOIRequestNotificationUser.created_at) == _datevalue[n])
                        if len(datecriteria) > 0:
                            filtercondition.append(and_(*datecriteria)) 
                    else:
                        filtercondition.append(FOIRequestNotificationUser.findfield(field, iaoassignee, ministryassignee, foiuser, foicreator).ilike('%'+_keyword+'%'))
            else:
                if(requestby == 'IAO'):
                    filtercondition.append(FOIRestrictedMinistryRequest.isrestricted == True)
                else:
                    filtercondition.append(ministry_restricted_requests.isrestricted == True)

        selectedcolumns = [
            FOIMinistryRequest.axisrequestid.label('axisRequestId'),
            FOIRequestStatus.name.label('status'),
            notificationquery.c.notification["message"].astext.cast(String).label('notification'),     
            notificationquery.c.userid.label('to'),
            notificationquery.c.createdby.label('createdby'),
            notificationquery.c.created_at.label('createdat'),
            FOIMinistryRequest.assignedgroup.label('assignedGroup'),
            FOIMinistryRequest.assignedto.label('assignedTo'),
            FOIMinistryRequest.assignedministrygroup.label('assignedministrygroup'),
            FOIMinistryRequest.assignedministryperson.label('assignedministryperson'),
            iaoassignee.firstname.label('assignedToFirstName'),
            iaoassignee.lastname.label('assignedToLastName'),
            ministryassignee.firstname.label('assignedministrypersonFirstName'),
            ministryassignee.lastname.label('assignedministrypersonLastName'),
            assignedtoformatted,
            ministryassignedtoformatted,
            notificationquery.c.idnumber.label('id'),
            FOIRequest.foirawrequestid.label('rawrequestid'),
            FOIRequest.foirequestid.label('requestid'),
            FOIMinistryRequest.foiministryrequestid.label('ministryrequestid'),
            notificationquery.c.idnumber.label('idnumber'),
            foiuser.firstname.label('userFirstName'),
            foiuser.lastname.label('userLastName'),
            foicreator.firstname.label('creatorFirstName'),
            foicreator.lastname.label('creatorLastName'),
            NotificationType.name.label('notificationtype'),
            userformatted.label('userFormatted'),
            creatorformatted.label('creatorFormatted'),
            FOIMinistryRequest.description,
        ]

        basequery = _session.query(
                                *selectedcolumns
                            ).join(
                                subquery_ministry_maxversion,
                                and_(*joincondition_ministry)
                            ).join(
                                FOIRequest,
                                and_(FOIRequest.foirequestid == FOIMinistryRequest.foirequest_id, FOIRequest.version == FOIMinistryRequest.foirequestversion_id)
                            ).join(
                                FOIRequestStatus,
                                FOIRequestStatus.requeststatusid == FOIMinistryRequest.requeststatusid
                            ).join(
                                iaoassignee,
                                iaoassignee.username == FOIMinistryRequest.assignedto,
                                isouter=True
                            ).join(
                                ministryassignee,
                                ministryassignee.username == FOIMinistryRequest.assignedministryperson,
                                isouter=True
                            ).join(
                                FOIRestrictedMinistryRequest,
                                and_(
                                    FOIRestrictedMinistryRequest.ministryrequestid == FOIMinistryRequest.foiministryrequestid,
                                    FOIRestrictedMinistryRequest.type == 'iao',
                                    FOIRestrictedMinistryRequest.isactive == True),
                                isouter=True
                            ).join(
                                ministry_restricted_requests,
                                and_(
                                    ministry_restricted_requests.ministryrequestid == FOIMinistryRequest.foiministryrequestid,
                                    ministry_restricted_requests.type == 'ministry',
                                    ministry_restricted_requests.isactive == True),
                                isouter=True
                            ).join(
                                notificationquery,
                                and_(notificationquery.c.axisnumber == FOIMinistryRequest.axisrequestid),
                            ).join(
                                NotificationType,
                                NotificationType.notificationtypeid == notificationquery.c.notificationtypeid 
                            ).join(
                                foiuser, foiuser.preferred_username == notificationquery.c.userid, isouter=True  
                            ).join(
                                foicreator, foicreator.preferred_username == notificationquery.c.createdby, isouter=True  
                            ).filter(FOIMinistryRequest.requeststatusid != 3)
                            
        if(additionalfilter == 'watchingRequests'):
            #watchby
            activefilter = and_(FOIMinistryRequest.isactive == True, FOIRequestStatus.isactive == True)

            subquery_watchby = FOIRequestWatcher.getrequestidsbyuserid(userid)
            dbquery = basequery.join(subquery_watchby, subquery_watchby.c.ministryrequestid == FOIMinistryRequest.foiministryrequestid).filter(activefilter)
        elif(additionalfilter == 'myRequests'):
            #myrequest
            if(requestby == 'IAO'):
                dbquery = basequery.filter(or_(FOIMinistryRequest.assignedto == userid)).filter(ministryfilter)
            else:
                dbquery = basequery.filter(or_(FOIMinistryRequest.assignedministryperson == userid)).filter(ministryfilter)
        else:
            if(isiaorestrictedfilemanager == True or isministryrestrictedfilemanager == True):
                dbquery = basequery
            else:
                if(requestby == 'IAO'):
                    dbquery = basequery.filter(or_(or_(FOIRestrictedMinistryRequest.isrestricted == False, FOIRestrictedMinistryRequest.isrestricted == None), and_(FOIRestrictedMinistryRequest.isrestricted == True, FOIMinistryRequest.assignedto == userid))).filter(ministryfilter)
                else:
                    dbquery = basequery.filter(or_(or_(ministry_restricted_requests.isrestricted == False, ministry_restricted_requests.isrestricted == None), and_(ministry_restricted_requests.isrestricted == True, FOIMinistryRequest.assignedministryperson == userid))).filter(ministryfilter)
                
        if(keyword is None):
            return dbquery
        else:
            return dbquery.filter(or_(*filtercondition))

    @classmethod
    def getnotificationquery(cls, subquery_ministry_maxversion, joincondition_ministry, ministryfilter, additionalfilter, requestby, userid):      
        axisquery = db.session.query(
                        FOIMinistryRequest.axisrequestid             
                        ).join(
                         subquery_ministry_maxversion, and_(*joincondition_ministry)
                        ).filter(FOIMinistryRequest.requeststatusid != 3
                        ).filter(ministryfilter)
        
        query1 = db.session.query(
                                   FOIRequestNotification.idnumber.label('idnumber'),
                                   FOIRequestNotification.axisnumber.label('axisnumber'), 
                                   FOIRequestNotification.notification.label('notification'),
                                   FOIRequestNotificationUser.userid.label('userid'),
                                   FOIRequestNotificationUser.createdby.label('createdby'),
                                   FOIRequestNotificationUser.created_at.label('created_at'),
                                   FOIRequestNotification.notificationtypeid.label('notificationtypeid')
                                 ).join(
                                    FOIRequestNotificationUser,
                                    and_(FOIRequestNotification.notificationid == FOIRequestNotificationUser.notificationid), 
                                )
        query2 = db.session.query(
                                   FOIRawRequestNotification.idnumber.label('idnumber'),
                                   FOIRawRequestNotification.axisnumber.label('axisnumber'),
                                   FOIRawRequestNotification.notification.label('notification'),
                                   FOIRawRequestNotificationUser.userid.label('userid'),
                                   FOIRawRequestNotificationUser.createdby.label('createdby'),
                                   FOIRawRequestNotificationUser.created_at.label('created_at'),
                                   FOIRawRequestNotification.notificationtypeid.label('notificationtypeid')
                                 ).join(
                                    FOIRawRequestNotificationUser,
                                    and_(FOIRawRequestNotificationUser.notificationid == FOIRawRequestNotification.notificationid), 
                                )
        
        if additionalfilter == 'watchingRequests':
            axis_ids = FOIRequestNotificationUser.getaxisnumbersbywatcher(userid)    
            query1 = query1.filter(or_(FOIRequestNotification.axisnumber.in_(axis_ids),FOIRequestNotificationUser.userid == userid))
            query2 = query2.filter(or_(FOIRawRequestNotification.axisnumber.in_(axis_ids),FOIRawRequestNotificationUser.userid == userid))
        else:
            query1 = query1.filter(or_(FOIRequestNotification.axisnumber.in_(axisquery), FOIRequestNotificationUser.userid == userid))
            query2 = query2.filter(or_(FOIRawRequestNotification.axisnumber.in_(axisquery), FOIRawRequestNotificationUser.userid == userid))
        
        return query1.union(query2).subquery()          

    @classmethod
    def getgroupfilters(cls, groups):
        #ministry filter for group/team
        if groups is None:
            ministryfilter = FOIMinistryRequest.isactive == True
        else:
            groupfilter = []
            for group in groups:
                if (group == IAOTeamWithKeycloackGroup.flex.value or group in ProcessingTeamWithKeycloackGroup.list()):
                    groupfilter.append(
                        and_(
                            FOIMinistryRequest.assignedgroup == group
                        )
                    )
                elif (group == IAOTeamWithKeycloackGroup.intake.value):
                    groupfilter.append(
                        or_(
                            FOIMinistryRequest.assignedgroup == group,
                            and_(
                                FOIMinistryRequest.assignedgroup == IAOTeamWithKeycloackGroup.flex.value,
                                FOIMinistryRequest.requeststatusid.in_([1])
                            )
                        )
                    )
                else:
                    groupfilter.append(
                        or_(
                            FOIMinistryRequest.assignedgroup == group,
                            and_(
                                FOIMinistryRequest.assignedministrygroup == group,
                                FOIMinistryRequest.requeststatusid.in_([2,7,9,8,10,11,12,13,14])
                            )
                        )
                    )

            ministryfilter = and_(
                                    FOIMinistryRequest.isactive == True, FOIRequestStatus.isactive == True,
                                    or_(*groupfilter)
                                )
        
        return ministryfilter
    
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
    def getaxisnumbersbywatcher(cls, userid):
        watchers = []                
        try:
            sql = """ select fr.axisrequestid  from "FOIRequestWatchers" fw, 
                    ( select foiministryrequestid, axisrequestid, max(version) max_version from "FOIMinistryRequests" fr group by foiministryrequestid, axisrequestid
                    ) fr  where fw.watchedby = :userid and fw.ministryrequestid=fr.foiministryrequestid 
                    union
                    select fr.axisrequestid  from "FOIRawRequestWatchers" fw, ( 
                    select requestid, axisrequestid, max(version) max_version from "FOIRawRequests" fr group by requestid, axisrequestid
                    ) fr where fw.watchedby = :userid and fw.requestid=fr.requestid ;"""
            rs = db.session.execute(text(sql), {'userid': userid})        
            for row in rs:
                watchers.append(row["axisrequestid"])
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return watchers 
    
    @classmethod
    def getsorting(cls, sortingitems, sortingorders, iaoassignee, ministryassignee, foiuser, foicreator):
        #sorting
        sortingcondition = []
        if(len(sortingitems) > 0 and len(sortingorders) > 0 and len(sortingitems) == len(sortingorders)):
            for field in sortingitems:
                order = sortingorders.pop(0)
                sortingcondition.append(FOIRequestNotificationUser.getfieldforsorting(field, order, iaoassignee, ministryassignee, foiuser, foicreator))

        #default sorting
        if(len(sortingcondition) == 0):
            sortingcondition.append(FOIRequestNotificationUser.findfield('createdat', iaoassignee, ministryassignee, foiuser, foicreator).desc())

        #always sort by created_at last to prevent pagination collisions
        sortingcondition.append(asc('created_at'))
        
        return sortingcondition
    
    @classmethod
    def getfieldforsorting(cls, field, order, iaoassignee, ministryassignee, foiuser, foicreator):
        #get one field
        customizedfields = ['assignedToFormatted', 'ministryAssignedToFormatted', 'userFormatted','creatorFormatted', 'createdat', 'createdby', 'idNumber', 'notification']
        if(field in customizedfields):
            if(order == 'desc'):
                return nullslast(desc(field))
            else:
                return nullsfirst(asc(field))
        else:
            if(order == 'desc'):
                return nullslast(FOIMinistryRequest.findfield(field, iaoassignee, ministryassignee, foiuser, foicreator).desc())
            else:
                return nullsfirst(FOIMinistryRequest.findfield(field, iaoassignee, ministryassignee, foiuser, foicreator).asc())

    @classmethod
    def findfield(cls, x, iaoassignee, ministryassignee, foiuser, foicreator):
        #add more fields here if need sort/filter/search more columns

        return {
            'to': FOIRequestNotificationUser.userid,
            'createdby' : FOIRequestNotificationUser.createdby,
            'axisRequestId' : FOIMinistryRequest.axisrequestid,
            'assignedTo': FOIMinistryRequest.assignedto,
            'assignedministryperson': FOIMinistryRequest.assignedministryperson,
            'assignedToFirstName': iaoassignee.firstname,
            'assignedToLastName': iaoassignee.lastname,
            'assignedministrypersonFirstName': ministryassignee.firstname,
            'assignedministrypersonLastName': ministryassignee.lastname,
            'userFirstName':foiuser.firstname,
            'userLastName':foiuser.lastname,
            'creatorFirstName':foicreator.firstname,
            'creatorLastName':foicreator.lastname,
            'description': FOIMinistryRequest.description,
        }.get(x,  cast(FOIMinistryRequest.axisrequestid, String))
    
    # End of Dashboard functions
        
class FOIRequestNotificationUserSchema(ma.Schema):
    class Meta:
        fields = ('notificationid', 'userid','notificationusertypeid','created_at','createdby','updated_at','updatedby') 