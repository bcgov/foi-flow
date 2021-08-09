from .db import  db, ma
from .default_method_result import DefaultMethodResult


class ContactType(db.Model):
    __tablename__ = 'ContactTypes' 
    # Defining the columns
    contacttypeid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.String(255), unique=False, nullable=True)    
    isactive = db.Column(db.Boolean, unique=False, nullable=False)

    @classmethod
    def getcontacttypes(cls):
        contacttype_schema = ContactTypeSchema(many=True)
        query = db.session.query(ContactType).filter_by(isactive=True).all()
        return contacttype_schema.dump(query)


class ContactTypeSchema(ma.Schema):
    class Meta:
        fields = ('contacttypeid', 'name', 'description','isactive')