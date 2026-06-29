from datetime import datetime
from .default_method_result import DefaultMethodResult
from .db import db, ma

class FOIRequestApplicationFee(db.Model):
    __tablename__ = 'FOIRequestApplicationFees'
    # Defining the columns
    applicationfeeid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    version =db.Column(db.Integer,primary_key=True,nullable=False)
    rawrequestid = db.Column(db.Integer, nullable=False)
    ministryrequestid = db.Column(db.Integer, nullable=True)
    applicationfeestatus = db.Column(db.String(50), nullable=True)
    amountpaid = db.Column(db.Float, nullable=True)
    paymentsource = db.Column(db.String(50), nullable=True)
    paymentdate = db.Column(db.DateTime, nullable=True)
    orderid = db.Column(db.String(50), nullable=True)
    transactionnumber = db.Column(db.String(50), nullable=True)
    refundamount = db.Column(db.Float, nullable=True)
    refunddate = db.Column(db.DateTime, nullable=True)
    reasonforrefund = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    createdby = db.Column(db.String(120), unique=False, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)

    @classmethod
    def getapplicationfee(cls, rawrequestid, ministryrequestid=None)->DefaultMethodResult:
        applicationfee_schema = FOIRequestApplicationFeeSchema(many=False)
        if ministryrequestid:
            query = db.session.query(FOIRequestApplicationFee).filter_by(ministryrequestid=ministryrequestid).order_by(FOIRequestApplicationFee.applicationfeeid.desc(), FOIRequestApplicationFee.version.desc()).first()
        elif rawrequestid:
            query = db.session.query(FOIRequestApplicationFee).filter_by(rawrequestid=rawrequestid, ministryrequestid=None).order_by(FOIRequestApplicationFee.applicationfeeid.desc(), FOIRequestApplicationFee.version.desc()).first()
        else:
            return None
        return applicationfee_schema.dump(query)

    @classmethod    
    def saveapplicationfee(cls, applicationfee, userid)->DefaultMethodResult:
        applicationfee.created_at = datetime.now().isoformat()
        applicationfee.createdby = userid 
        db.session.add(applicationfee)
        db.session.commit()
        if applicationfee.ministryrequestid:
            request_identifier = applicationfee.ministryrequestid
            request_type = "Ministry Request"
        else:
            request_identifier = applicationfee.rawrequestid
            request_type = "Raw Request"
        return DefaultMethodResult(True,'Application Fee added for ' + request_type + ' : '+ str(request_identifier), applicationfee.applicationfeeid)

    @classmethod
    def applicationfeestatushaschanged(cls, rawrequestid, ministryrequestid=None):
        applicationfee_schema = FOIRequestApplicationFeeSchema(many=True)
        if ministryrequestid:
            query = db.session.query(FOIRequestApplicationFee).filter_by(ministryrequestid=ministryrequestid).order_by(FOIRequestApplicationFee.applicationfeeid.desc(), FOIRequestApplicationFee.version.desc()).all()
        elif rawrequestid:
            query = db.session.query(FOIRequestApplicationFee).filter_by(rawrequestid=rawrequestid, ministryrequestid=None).order_by(FOIRequestApplicationFee.applicationfeeid.desc(), FOIRequestApplicationFee.version.desc()).all()
        else:
            return False

        result = applicationfee_schema.dump(query)
        if len(result) >= 2 and result[0]['applicationfeestatus'] != result[1]['applicationfeestatus']:
            return True
        elif len(result) == 1 and result[0]['applicationfeestatus'] != 'init':
            return True
        else:
            return False

    @classmethod
    def applicationfeerefundamountupdated(cls, rawrequestid, ministryrequestid=None):
        applicationfee_schema = FOIRequestApplicationFeeSchema(many=True)
        if ministryrequestid:
            query = db.session.query(FOIRequestApplicationFee).filter_by(ministryrequestid=ministryrequestid).order_by(FOIRequestApplicationFee.applicationfeeid.desc(), FOIRequestApplicationFee.version.desc()).all()
        elif rawrequestid:
            query = db.session.query(FOIRequestApplicationFee).filter_by(rawrequestid=rawrequestid, ministryrequestid=None).order_by(FOIRequestApplicationFee.applicationfeeid.desc(), FOIRequestApplicationFee.version.desc()).all()
        else:
            return False

        result = applicationfee_schema.dump(query)
        if len(result) >= 2 and result[0]['refundamount'] != result[1]['refundamount']:
            return True
        elif len(result) == 1 and result[0]['refundamount'] != 0 and result[0]['refundamount'] is not None:
            return True
        else:
            return False

class FOIRequestApplicationFeeSchema(ma.Schema):
    class Meta:
        fields = ('applicationfeeid', 'version', 'rawrequestid', 'ministryrequestid', 'applicationfeestatus', 'amountpaid', 'paymentsource', 'paymentdate', 'orderid', 'transactionnumber', 'refundamount', 'refunddate', 'reasonforrefund', 'receipts', 'created_at', 'createdby', 'updated_at', 'updatedby')