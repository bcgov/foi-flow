from .db import  db, ma
from .default_method_result import DefaultMethodResult


class PersonalInformationAttribute(db.Model):
    __tablename__ = 'PersonalInformationAttributes' 
    # Defining the columns
    attributeid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.String(255), unique=False, nullable=True)    
    isactive = db.Column(db.Boolean, unique=False, nullable=False)

    @classmethod
    def getpersonalattributes(cls):
        requestortype_schema = PersonalInformationAttributesSchema(many=True)
        query = db.session.query(PersonalInformationAttribute).filter_by(isactive=True).all()
        return requestortype_schema.dump(query)

    @classmethod
    def getpersonalattribute(cls,attribname):
        deliverymode_schema = PersonalInformationAttributesSchema()
        query = db.session.query(PersonalInformationAttribute).filter_by(name=attribname).first()
        return deliverymode_schema.dump(query)

class PersonalInformationAttributesSchema(ma.Schema):
    class Meta:
        fields = ('attributeid', 'name', 'description','isactive')