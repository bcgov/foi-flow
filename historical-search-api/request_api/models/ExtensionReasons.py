from .db import  db, ma

class ExtensionReason(db.Model):
    __tablename__ = 'ExtensionReasons' 
    # Defining the columns
    extensionreasonid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    reason = db.Column(db.String(100), unique=False, nullable=False)
    extensiontype = db.Column(db.String(25), unique=False, nullable=False)
    defaultextendedduedays = db.Column(db.Integer, unique=False, nullable=True)
    isactive = db.Column(db.Boolean, unique=False, nullable=False)    
    
    @classmethod
    def getallextensionreasons(cls):
        extensionreason_schema = ExtensionReasonSchema(many=True)
        query = db.session.query(ExtensionReason).filter_by(isactive=True).order_by(ExtensionReason.extensionreasonid.asc()).all()
        return extensionreason_schema.dump(query)

    @classmethod
    def getextensionreasonbyid(cls,extensionreasonid):
        extensionreason_schema = ExtensionReasonSchema()
        query = db.session.query(ExtensionReason).filter_by(extensionreasonid=extensionreasonid).first()
        return extensionreason_schema.dump(query)
    
             

class ExtensionReasonSchema(ma.Schema):
    class Meta:
        fields = ('extensionreasonid','reason','extensiontype','isactive', 'defaultextendedduedays')