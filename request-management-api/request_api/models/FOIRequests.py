from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey
from .db import  db, ma
from datetime import datetime
from sqlalchemy.orm import relationship,backref
from .default_method_result import DefaultMethodResult


class FOIRequest(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOIRequests' 
    # Defining the columns
    foirequestid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    version = db.Column(db.Integer, primary_key=True,nullable=False)
    requesttype = db.Column(db.String(15), unique=False, nullable=False)
    receiveddate = db.Column(db.DateTime, default=datetime.now().isoformat())
    isactive = db.Column(db.Boolean, unique=False, nullable=False,default=True)

    initialdescription = db.Column(db.String(500), unique=False, nullable=True)
    initialrecordsearchfromdate = db.Column(db.DateTime, nullable=True)
    initialrecordsearchtodate = db.Column(db.DateTime, nullable=True)
                
    created_at = db.Column(db.DateTime, default=datetime.now().isoformat())
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    #ForeignKey References
    
    deliverymodeid = db.Column(db.Integer,ForeignKey('DeliveryModes.deliverymodeid'))
    deliverymode =  relationship("DeliveryMode",backref=backref("DeliveryModes"),uselist=False)
    
    receivedmodeid = db.Column(db.Integer,ForeignKey('ReceivedModes.receivedmodeid'))
    receivedmode =  relationship("ReceivedMode",backref=backref("ReceivedModes"),uselist=False)

    foirawrequestid = db.Column(db.Integer,unique=False, nullable=True)
    

    @classmethod
    def getrequest(cls,requestid):
        request_schema = FOIRequestsSchema(many=True)
        query = db.session.query(FOIRequest).filter_by(foirequestid=requestid).order_by(FOIRequest.version.desc()).first()
        return request_schema.dump(query)

class FOIRequestsSchema(ma.Schema):
    class Meta:
        fields = ('foirequestid','version','requesttype','receiveddate','initialdescription','initialrecordSearchFromDate','initialrecordsearchtodate','receivedmode.receivedmodeid','deliverymode.deliverymodeid')
    