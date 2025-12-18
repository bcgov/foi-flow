from .db import  db, ma
from .default_method_result import DefaultMethodResult


class ApplicantCategory(db.Model):
    __tablename__ = 'ApplicantCategories' 
    # Defining the columns
    applicantcategoryid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.String(255), unique=False, nullable=True)    
    isactive = db.Column(db.Boolean, unique=False, nullable=False)

    @classmethod
    def getapplicantcategories(cls):
        applicantcategory_schema = ApplicantCategorySchema(many=True)
        query = db.session.query(ApplicantCategory).filter_by(isactive=True).all()
        return applicantcategory_schema.dump(query)

    @classmethod
    def getapplicantcategory(cls,appltcategory):
        applicantcategory_schema = ApplicantCategorySchema()
        query = db.session.query(ApplicantCategory).filter_by(name=appltcategory).first()
        return applicantcategory_schema.dump(query)
    
    
class ApplicantCategorySchema(ma.Schema):
    class Meta:
        fields = ('applicantcategoryid', 'name', 'description','isactive')