from .db import  db, ma
from sqlalchemy import func

class FeeWaiverStatus(db.Model):
    __tablename__ = 'FeeWaiverStatuses'
    # Defining the columns
    waiverstatusid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(25), unique=False, nullable=False)
    description = db.Column(db.String(100), unique=False, nullable=False)
    isactive = db.Column(db.Boolean, unique=False, nullable=False)

    @classmethod
    def getallwaiverstatuses(cls):
        waiverstatus_schema = FeeWaiverStatusSchema(many=True)
        query = db.session.query(FeeWaiverStatus).filter_by(isactive=True).order_by(FeeWaiverStatus.waiverstatusid.asc()).all()
        return waiverstatus_schema.dump(query)

    @classmethod
    def getwaiverstatus(cls,waiverstatusid):
        waiverstatus_schema = FeeWaiverStatusSchema(many=False)
        query = db.session.query(FeeWaiverStatus).filter_by(waiverstatusid=waiverstatusid).first()
        return waiverstatus_schema.dump(query)

    @classmethod
    def getwaiverstatusid(cls,waiverstatus):
        waiverstatus_schema = FeeWaiverStatusSchema(many=False)
        query = db.session.query(FeeWaiverStatus).filter(func.lower(FeeWaiverStatus.name) == func.lower(waiverstatus)).first()
        return waiverstatus_schema.dump(query)

class FeeWaiverStatusSchema(ma.Schema):
    class Meta:
        fields = ('waiverstatusid','name','description','isactive')