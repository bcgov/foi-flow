from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from datetime import datetime
from .default_method_result import DefaultMethodResult

class FOICorrespondenceEmailRawRequest(db.Model):
    # Name of the table in our database
    __tablename__ = 'FOICorrespondenceEmailsRawRequests'
    __table_args__ = (
        ForeignKeyConstraint(
            ["foirawrequest_id", "foirawrequestversion_id"], ["FOIRawRequests.requestid", "FOIRawRequests.version"]
        ),
    )
        
    # Defining the columns
    correspondenceemailid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    email = db.Column(db.Text, unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    createdby = db.Column(db.String(120), unique=False, nullable=False)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    
    #ForeignKey References       
    foirawrequest_id =db.Column(db.Integer, db.ForeignKey('FOIRawRequests.requestid'))
    foirawrequestversion_id=db.Column(db.Integer, db.ForeignKey('FOIRawRequests.version'))

    
    @classmethod
    def getcorrespondenceemails(cls,rawrequestid):
        email_schema = FOICorrepondenceEmailRawRequestSchema(many=True)
        query = db.session.query(FOICorrespondenceEmailRawRequest.email).filter(FOICorrespondenceEmailRawRequest.foirawrequest_id == rawrequestid).order_by(FOICorrespondenceEmailRawRequest.email.desc()).all()
        return email_schema.dump(query)
    
    @classmethod
    def savecorrespondenceemail(cls,correpondenceemail)->DefaultMethodResult: 
        
        try:
            db.session.add(correpondenceemail)
            db.session.commit()
            return DefaultMethodResult(True,'correspondence email added')
        except Exception:
            return DefaultMethodResult(False,'unable to save correspondence email')
        finally:
            db.session.close()
   
class FOICorrepondenceEmailRawRequestSchema(ma.Schema):
    class Meta:
        fields = ('correspondenceemailid','email','created_at','createdby')
    