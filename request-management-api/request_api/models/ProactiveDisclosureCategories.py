from .db import  db, ma
from .default_method_result import DefaultMethodResult


class ProactiveDisclosureCategory(db.Model):
    __tablename__ = 'ProactiveDisclosureCategories' 
    # Defining the columns
    proactivedisclosurecategoryid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    description = db.Column(db.String(255), unique=False, nullable=True)    
    isactive = db.Column(db.Boolean, unique=False, nullable=False)

    @classmethod
    def getproactivedisclosurecategories(cls):
        proactivedisclosurecategory_schema = ProactiveDisclosureCategorySchema(many=True)
        query = db.session.query(ProactiveDisclosureCategory).filter_by(isactive=True).all()
        return proactivedisclosurecategory_schema.dump(query)

    @classmethod
    def getproactivedisclosurecategory(cls,pdcategory):
        proactivedisclosurecategory_schema = ProactiveDisclosureCategorySchema()
        query = db.session.query(ProactiveDisclosureCategory).filter_by(name=pdcategory).first()
        return proactivedisclosurecategory_schema.dump(query)
    
    
class ProactiveDisclosureCategorySchema(ma.Schema):
    class Meta:
        fields = ('proactivedisclosurecategoryid', 'name', 'description','isactive')