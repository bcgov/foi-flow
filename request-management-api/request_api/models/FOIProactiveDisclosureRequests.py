from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship, backref, aliased
from sqlalchemy import or_, and_, text, func, literal, cast, case, nullslast, nullsfirst, desc, asc
from sqlalchemy.sql.sqltypes import String
from sqlalchemy.sql.sqltypes import Date, Integer
from request_api.models.default_method_result import DefaultMethodResult
from sqlalchemy import text
from datetime import datetime as datetime2
import logging

class FOIProactiveDisclosureRequests(db.Model):
    __tablename__ = "FOIProactiveDisclosureRequests"
    # Defining the columns
    proactivedisclosureid = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    #version = db.Column(db.Integer, primary_key=True, nullable=False)
    foiministryrequest_id = db.Column(db.Integer, ForeignKey('FOIMinistryRequests.foiministryrequestid'), nullable=False)
    foiministryrequestversion_id = db.Column(db.Integer, ForeignKey('FOIMinistryRequests.version'), nullable=False)
    proactivedisclosurecategoryid = db.Column(db.Integer,ForeignKey('ProactiveDisclosureCategories.proactivedisclosurecategoryid')) 
    proactivedisclosurecategory =  relationship("ProactiveDisclosureCategory",backref=backref("ProactiveDisclosureCategories"),uselist=False)
    reportperiod = db.Column(db.String, nullable=True)
    publicationdate = db.Column(db.DateTime, nullable=True)
    #receiveddate = db.Column(db.DateTime, nullable=True)
    #isactive = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), nullable=False)
    updatedby = db.Column(db.String(120), nullable=True)


    @classmethod
    def getproactiverequestbyministryrequestid(cls,ministryrequestid, ministryversion):
        request_schema = FOIProactiveDisclosureRequestSchema()
        query = db.session.query(FOIProactiveDisclosureRequests).filter_by(foiministryrequest_id=ministryrequestid , foiministryrequestversion_id = ministryversion).order_by(FOIProactiveDisclosureRequests.foiministryrequestversion_id.desc()).first()
        return request_schema.dump(query) 

    def getcurrentfoiproactiverequest(cls, foiminstryrequestid)->DefaultMethodResult:
        try:
            foiopeninforequest_schema = FOIProactiveDisclosureRequestSchema()
            query = db.session.query(FOIProactiveDisclosureRequests).filter_by(foiministryrequest_id=foiminstryrequestid).order_by(FOIProactiveDisclosureRequests.version.desc()).first()
            return foiopeninforequest_schema.dump(query)
        except Exception as exception:
            logging.error(f"Error: {exception}")
                
    # def createopeninfo(cls, foiopeninforequest, userid)->DefaultMethodResult:
    #     try:
    #         createddate = datetime2.now().isoformat()
    #         new_foiopeninforequest = FOIProactiveDisclosureRequests(
    #             version=1,
    #             foiministryrequest_id=foiopeninforequest["foiministryrequest_id"],
    #             foiministryrequestversion_id=foiopeninforequest["foiministryrequestversion_id"],
    #             proactivedisclosurecategoryid = foiopeninforequest["proactivedisclosurecategoryid"],
    #             reportperiod = foiopeninforequest["reportperiod"],
    #             #publicationdate = foiopeninforequest["publicationdate"],
    #             publicationdate=foiopeninforequest.get("publicationdate"),
    #             receiveddate=foiopeninforequest.get("receiveddate"),
    #             copyrightsevered=foiopeninforequest.get("copyrightsevered"),
    #             created_at=createddate,
    #             createdby=userid,
    #         )
    #         db.session.add(new_foiopeninforequest)
    #         db.session.commit()      
    #         return DefaultMethodResult(True, "FOIOpenInfo request created", new_foiopeninforequest.foiopeninforequestid)
    #     except Exception as exception:
    #         logging.error(f"Error: {exception}")
    #         return DefaultMethodResult(False, "FOIOpenInfo request unable to be created")    


class FOIProactiveDisclosureRequestSchema(ma.Schema):
    class Meta:
        fields = (
            'proactivedisclosureid', 'foiministryrequest_id', 'foiministryrequestversion_id', 'proactivedisclosurecategoryid', 
            'proactivedisclosurecategory.proactivedisclosurecategoryid','proactivedisclosurecategory.name','reportperiod',
            'publicationdate', 'created_at', 'updated_at', 'createdby', 'updatedby',
        )