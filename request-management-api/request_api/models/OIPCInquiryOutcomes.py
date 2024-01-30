from .db import  db, ma

class OIPCInquiryOutcomes(db.Model):
    __tablename__ = 'OIPCInquiryOutcomes' 
    # Defining the columns
    inquiryoutcomeid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), unique=False, nullable=False)  
    isactive = db.Column(db.Boolean, unique=False, nullable=False)

    @classmethod
    def getinquiryoutcomes(cls):
        type_schema = InquiryOutcomeSchema(many=True)
        query = db.session.query(OIPCInquiryOutcomes).filter_by(isactive=True).all()
        return type_schema.dump(query)


class InquiryOutcomeSchema(ma.Schema):
    class Meta:
        fields = ('inquiryoutcomeid', 'name','isactive')