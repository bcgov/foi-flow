from .db import  db, ma
from .default_method_result import DefaultMethodResult


class RequestorType(db.Model):
    __tablename__ = 'RequestorTypes' 
    # Defining the columns
    requestortypeid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.String(255), unique=False, nullable=True)    
    isactive = db.Column(db.Boolean, unique=False, nullable=False)

    @classmethod
    def getrequestortypes(cls):
        requestortype_schema = RequestorTypeSchema(many=True)
        query = db.session.query(RequestorType).filter_by(isactive=True).all()
        return requestortype_schema.dump(query)

    @classmethod
    def getrequestortype(cls,type):
        programarea_schema = RequestorTypeSchema()
        query = db.session.query(RequestorType).filter_by(name=type).first()
        return programarea_schema.dump(query)

class RequestorTypeSchema(ma.Schema):
    class Meta:
        fields = ('requestortypeid', 'name', 'description','isactive')