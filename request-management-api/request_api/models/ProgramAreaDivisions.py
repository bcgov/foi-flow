from .db import  db, ma
from .default_method_result import DefaultMethodResult
from sqlalchemy.orm import relationship,backref
from datetime import datetime
from sqlalchemy import text

class ProgramAreaDivision(db.Model):
    __tablename__ = 'ProgramAreaDivisions' 
    # Defining the columns
    divisionid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    programareaid = db.Column(db.Integer, db.ForeignKey('ProgramAreas.programareaid'))
    name = db.Column(db.String(500), unique=False, nullable=False)    
    isactive = db.Column(db.Boolean, unique=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    createdby = db.Column(db.String(120), unique=False, default='System')
    
    @classmethod
    def getallprogramareadivisons(cls):
        division_schema = ProgramAreaDivisionSchema(many=True)
        query = db.session.query(ProgramAreaDivision).filter_by(isactive=True).all()
        return division_schema.dump(query)

    @classmethod
    def getprogramareadivisions(cls,programareaid):
        division_schema = ProgramAreaDivisionSchema(many=True)
        query = db.session.query(ProgramAreaDivision).filter_by(programareaid=programareaid).order_by(ProgramAreaDivision.name.asc())
        return division_schema.dump(query)
    
    @classmethod
    def getdivisionstagesummary(cls, programareaid):
        sql ='select pad2.divisionid as divisionid, pad2.name as name, count(pads.divisionid) as rcount from "ProgramAreaDivisions" pad2  LEFT JOIN "ProgramAreaDivisionStages" pads on pads.divisionid   = pad2.divisionid where pad2.programareaid  = :programareaid group by pad2.divisionid'
        rs = db.session.execute(text(sql), {'programareaid': programareaid})
        divisionstagesummary = []
        for row in rs:
            divisionstagesummary.append({"divisionid": row["divisionid"], "name": row["name"], "count": row["rcount"]})
        return divisionstagesummary 
             

class ProgramAreaDivisionSchema(ma.Schema):
    class Meta:
        fields = ('divisionid','programareaid', 'name','isactive')