from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from datetime import datetime as datetime2, timezone
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.sql.expression import distinct
from sqlalchemy import text
from sqlalchemy.sql.sqltypes import DateTime, String, Date
from sqlalchemy.orm import relationship, backref, aliased
from sqlalchemy import insert, and_, or_, text, func, literal, cast, asc, desc, case, nullsfirst, nullslast, TIMESTAMP, extract
from .FOIAssignees import FOIAssignee
from .FOIRequestNotificationUsers import FOIRequestNotificationUser
from .FOIUsers import FOIUser
from .FOIRawRequestNotificationUsers import FOIRawRequestNotificationUser


class FOIRequestNotificationDashboard:   
   
    @classmethod
    def getiaoeventpagination(cls, groups, page, size, sortingitems, sortingorders, filterfields, keyword, additionalfilter, userid, isiaorestrictedfilemanager, isministryrestrictedfilemanager=False):
        #ministry requests
        iaoassignee = aliased(FOIAssignee)
        ministryassignee = aliased(FOIAssignee)
        foiuser = aliased(FOIUser)
        foicreator = aliased(FOIUser)

        subquery_ministry_queue = FOIRequestNotificationUser.geteventsubquery(groups, filterfields, keyword, additionalfilter, userid, iaoassignee, ministryassignee, foiuser, foicreator, 'IAO', isiaorestrictedfilemanager, isministryrestrictedfilemanager)

        #sorting
        sortingcondition = FOIRawRequestNotificationUser.getsorting(sortingitems, sortingorders)
        #if "Intake Team" in groups or groups is None:                
        subquery_rawrequest_queue = FOIRawRequestNotificationUser.getrequestssubquery(groups, foiuser, foicreator, filterfields, keyword, additionalfilter, userid, isiaorestrictedfilemanager)
        query_full_queue = subquery_rawrequest_queue.union(subquery_ministry_queue)
        return query_full_queue.order_by(*sortingcondition).paginate(page=page, per_page=size)
        #else:
        #    return subquery_ministry_queue.order_by(*sortingcondition).paginate(page=page, per_page=size)

    @classmethod
    def getministryeventpagination(cls, group, page, size, sortingitems, sortingorders, filterfields, keyword, additionalfilter, userid,isiaorestrictedfilemanager, isministryrestrictedfilemanager):
        iaoassignee = aliased(FOIAssignee)
        ministryassignee = aliased(FOIAssignee)
        foiuser = aliased(FOIUser)
        foicreator = aliased(FOIUser)

        requestby = 'Ministry'

        subquery = FOIRequestNotificationUser.geteventsubquery(group, filterfields, keyword, additionalfilter, userid, iaoassignee, ministryassignee, foiuser, foicreator, requestby, isiaorestrictedfilemanager, isministryrestrictedfilemanager)
        sortingcondition = FOIRequestNotificationUser.getsorting(sortingitems, sortingorders, iaoassignee, ministryassignee, foiuser, foicreator)

        return subquery.order_by(*sortingcondition).paginate(page=page, per_page=size)
      