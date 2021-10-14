from .db import  db, ma
from .default_method_result import DefaultMethodResult
from datetime import datetime

class ProgramAreaDivisionStage(db.Model):
    __tablename__ = 'ProgramAreaDivisionStages' 
    # Defining the columns
    stageid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    divisionid = db.Column(db.Integer, unique=False, nullable=False)    
    name = db.Column(db.String(500), unique=False, nullable=False)    
    isactive = db.Column(db.Boolean, unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    createdby = db.Column(db.String(120), unique=False, default='System')
    
    @classmethod
    def getallprogramareadivisionstages(cls):
        divisionstage_schema = DivisionStageSchema(many=True)
        query = db.session.query(ProgramAreaDivisionStage).filter_by(isactive=True).all()
        return divisionstage_schema.dump(query)

    @classmethod
    def getprogramareadivisionstages(cls,divisionid):
        divisionstage_schema = DivisionStageSchema(many=True)
        query = db.session.query(ProgramAreaDivisionStage).filter_by(divisionid=divisionid).order_by(ProgramAreaDivisionStage.name.asc())
        return divisionstage_schema.dump(query)
    
 

class DivisionStageSchema(ma.Schema):
    class Meta:
        fields = ('stageid','divisionid', 'name','isactive')