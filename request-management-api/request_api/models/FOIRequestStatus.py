from .db import  db, ma
from .default_method_result import DefaultMethodResult


class FOIRequestStatus(db.Model):
    __tablename__ = 'FOIRequestStatuses' 
    # Defining the columns
    requeststatusid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.String(255), unique=False, nullable=True)    
    isactive = db.Column(db.Boolean, unique=False, nullable=False)

    @classmethod
    def getrequeststatuses(cls):
        requeststatus_schema = RequestStatusSchema(many=True)
        query = db.session.query(FOIRequestStatus).filter_by(isactive=True).all()
        return requeststatus_schema.dump(query)

    @classmethod
    def getrequeststatusid(cls,status):
        requeststatus_schema = RequestStatusSchema()
        query = db.session.query(FOIRequestStatus).filter_by(name=status).first()
        return requeststatus_schema.dump(query)

    @classmethod
    def getrequeststatusname(cls,statusid):
        requeststatus_schema = RequestStatusSchema()
        query = db.session.query(FOIRequestStatus).filter_by(requeststatusid=statusid, isactive=True).first()
        return requeststatus_schema.dump(query)

class RequestStatusSchema(ma.Schema):
    class Meta:
        fields = ('requeststatusid', 'name', 'description','isactive')