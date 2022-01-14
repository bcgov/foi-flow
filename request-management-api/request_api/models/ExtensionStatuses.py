from .db import  db, ma

class ExtensionStatus(db.Model):
    __tablename__ = 'ExtensionStatuses' 
    # Defining the columns
    extensionstatusid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(25), unique=False, nullable=False)
    description = db.Column(db.String(100), unique=False, nullable=False)    
    isactive = db.Column(db.Boolean, unique=False, nullable=False)    
    
    @classmethod
    def getallextensionstatuses(cls):
        extensionstatus_schema = ExtensionStatusSchema(many=True)
        query = db.session.query(ExtensionStatus).filter_by(isactive=True).order_by(ExtensionStatus.extensionstatusid.asc()).all()
        return extensionstatus_schema.dump(query)

    @classmethod
    def getextensionstatus(cls,extensionstatusid):
        extensionstatus_schema = ExtensionStatusSchema(many=True)
        query = db.session.query(ExtensionStatus).filter_by(extensionstatusid=extensionstatusid).first()
        return extensionstatus_schema.dump(query)
    
             

class ExtensionStatusSchema(ma.Schema):
    class Meta:
        fields = ('extensionstatusid','name','description','isactive')