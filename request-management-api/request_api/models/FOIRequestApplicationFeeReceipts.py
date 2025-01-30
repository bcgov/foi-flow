from datetime import datetime
from .default_method_result import DefaultMethodResult
from sqlalchemy.sql.schema import ForeignKey
from .db import db, ma
from .FOIRequestApplicationFees import FOIRequestApplicationFee

class FOIRequestApplicationFeeReceipt(db.Model):
    __tablename__ = 'FOIRequestApplicationFeeReceipts'

    # Defining the columns
    receiptid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    applicationfeeid = db.Column(db.Integer, ForeignKey('FOIRequestApplicationFees.applicationfeeid'))
    applicationfeeid_version = db.Column(db.Integer, ForeignKey('FOIRequestApplicationFees.version'))
    receiptfilename = db.Column(db.String(500), unique=False, nullable=True)
    receiptfilepath = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    isactive = db.Column(db.Boolean)

    @classmethod
    def getapplicationfeereceipts(cls, applicationfeeid)->DefaultMethodResult:   
        applicationfee_schema = FOIRequestApplicationFeeReceiptSchema(many=True)
        query = db.session.query(FOIRequestApplicationFeeReceipt).filter_by(applicationfeeid=applicationfeeid).order_by(FOIRequestApplicationFeeReceipt.applicationfeeid.desc()).all()
        return applicationfee_schema.dump(query)

    @classmethod
    def saveapplicationfeereceipt(cls, applicationfeereceipt)->DefaultMethodResult:
        applicationfee = db.session.query(FOIRequestApplicationFee).filter_by(applicationfeeid=applicationfeereceipt.applicationfeeid).order_by(FOIRequestApplicationFee.version.desc()).first()
        applicationfeereceipt.applicationfeeid_version = applicationfee.version
        db.session.add(applicationfeereceipt)
        db.session.commit()
        return DefaultMethodResult(True,'Application Fee Receipt added for  application fee : '+ str(applicationfeereceipt.applicationfeeid))   

    @classmethod
    def deactivateapplicationfeereceipt(cls, applicationfeereceiptid, userid)->DefaultMethodResult:
        db.session.query(FOIRequestApplicationFeeReceipt).filter_by(receiptid=applicationfeereceiptid).update({"isactive": False, "updated_at": datetime.now(),"updatedby": userid}, synchronize_session=False)
        db.session.commit()
        return DefaultMethodResult(True,'Application Fee Receipt has been removed for receipt with the id '+ str(applicationfeereceiptid))   

class FOIRequestApplicationFeeReceiptSchema(ma.Schema):
    class Meta:
        fields = ('receiptid', 'applicationfeeid', 'receiptfilename', 'receiptfilepath', 'created_at', 'createdby', 'updated_at', 'updatedby', 'isactive') 