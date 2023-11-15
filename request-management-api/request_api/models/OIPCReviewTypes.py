from .db import  db, ma

class OIPCReviewTypes(db.Model):
    __tablename__ = 'OIPCReviewTypes' 
    # Defining the columns
    reviewtypeid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), unique=False, nullable=False)  
    isactive = db.Column(db.Boolean, unique=False, nullable=False)

    @classmethod
    def getreviewtypes(cls):
        type_schema = ReviewTypeSchema(many=True)
        query = db.session.query(OIPCReviewTypes).filter_by(isactive=True).all()
        return type_schema.dump(query)


class ReviewTypeSchema(ma.Schema):
    class Meta:
        fields = ('reviewtypeid', 'name','isactive')