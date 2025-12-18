from .db import  db, ma
from .default_method_result import DefaultMethodResult


class ReceivedMode(db.Model):
    __tablename__ = 'ReceivedModes' 
    # Defining the columns
    receivedmodeid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.String(255), unique=False, nullable=True)    
    isactive = db.Column(db.Boolean, unique=False, nullable=False)

    @classmethod
    def getreceivedmodes(cls):
        receivedmode_schema = ReceivedModeSchema(many=True)
        query = db.session.query(ReceivedMode).filter_by(isactive=True).all()
        return receivedmode_schema.dump(query)
    
    @classmethod
    def getreceivedmode(cls,receivedmode):
        deliverymode_schema = ReceivedModeSchema()
        query = db.session.query(ReceivedMode).filter_by(name=receivedmode).first()
        return deliverymode_schema.dump(query)

class ReceivedModeSchema(ma.Schema):
    class Meta:
        fields = ('receivedmodeid', 'name', 'description','isactive')