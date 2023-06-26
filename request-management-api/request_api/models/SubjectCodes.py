from .db import  db, ma

class SubjectCode(db.Model):
    __tablename__ = 'SubjectCodes' 
    # Defining the columns
    subjectcodeid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(120), unique=False, nullable=False)
    description = db.Column(db.String(255), unique=False, nullable=True)    
    isaxissubjectcode = db.Column(db.Boolean, unique=False, nullable=False)
    isactive = db.Column(db.Boolean, unique=False, nullable=False)

    @classmethod
    def getsubjectcodes(cls):
        subjectcode_schema = SubjectCodeSchema(many=True)
        query = db.session.query(SubjectCode).filter_by(isactive=True).order_by(SubjectCode.name.asc()).all()
        return subjectcode_schema.dump(query)
    
    @classmethod
    def getsubjectcodebyname(cls,subjectcode):
        subjectcode_schema = SubjectCodeSchema()
        query = db.session.query(SubjectCode).filter_by(name=subjectcode).first()
        return subjectcode_schema.dump(query)
    
    @classmethod
    def getsubjectcodebyid(cls,subjectcodeid):
        subjectcode_schema = SubjectCodeSchema()
        query = db.session.query(SubjectCode).filter_by(subjectcodeid=subjectcodeid).first()
        return subjectcode_schema.dump(query)

class SubjectCodeSchema(ma.Schema):
    class Meta:
        fields = ('subjectcodeid', 'name', 'description','isaxissubjectcode', 'isactive')