from .db import  db, ma
from .default_method_result import DefaultMethodResult


class ProgramArea(db.Model):
    __tablename__ = 'ProgramAreas' 
    # Defining the columns
    programareaid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(255), unique=False, nullable=False)    
    iaocode = db.Column(db.String(30), unique=False, nullable=True)
    bcgovcode = db.Column(db.String(30), unique=False, nullable=True)
    type = db.Column(db.String(100), unique=False, nullable=True)
    isactive = db.Column(db.Boolean, unique=False, nullable=False)

    @classmethod
    def getprogramareas(cls):
        programarea_schema = ProgramAreaSchema(many=True)
        query = db.session.query(ProgramArea).filter_by(isactive=True).all()
        return programarea_schema.dump(query)

    @classmethod
    def getprogramarea(cls,pgname):
        programarea_schema = ProgramAreaSchema()
        query = db.session.query(ProgramArea).filter_by(name=pgname).first()
        return programarea_schema.dump(query)

class ProgramAreaSchema(ma.Schema):
    class Meta:
        fields = ('programareaid', 'name', 'iaocode','bcgovcode','type','isactive')