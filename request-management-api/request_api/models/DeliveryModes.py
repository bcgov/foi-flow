from .db import  db, ma
from .default_method_result import DefaultMethodResult


class DeliveryMode(db.Model):
    __tablename__ = 'DeliveryModes' 
    # Defining the columns
    deliverymodeid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.String(255), unique=False, nullable=True)    
    isactive = db.Column(db.Boolean, unique=False, nullable=False)

    @classmethod
    def getdeliverymodes(cls):
        deliverymode_schema = DeliveryModeSchema(many=True)
        query = db.session.query(DeliveryMode).filter_by(isactive=True).all()
        return deliverymode_schema.dump(query)

    @classmethod
    def getdeliverymode(cls,deliverymode):
        deliverymode_schema = DeliveryModeSchema()
        query = db.session.query(DeliveryMode).filter_by(name=deliverymode).first()
        return deliverymode_schema.dump(query)

class DeliveryModeSchema(ma.Schema):
    class Meta:
        fields = ('deliverymodeid', 'name', 'description','isactive')