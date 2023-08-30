from .db import  db, ma
from datetime import datetime as datetime2
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
    sortorder = db.Column(db.Integer, unique=False, nullable=True)
    issection = db.Column(db.Boolean, unique=False, nullable=True)
    parentid = db.Column(db.Integer, unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    createdby = db.Column(db.String(120), unique=False, default='system')
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    
    @classmethod
    def getallprogramareadivisons(cls):
        division_schema = ProgramAreaDivisionSchema(many=True)
        query = db.session.query(ProgramAreaDivision).filter_by(isactive=True,issection=False).all()
        return division_schema.dump(query)

    @classmethod
    def getprogramareadivisions(cls,programareaid):
        division_schema = ProgramAreaDivisionSchema(many=True)
        query = db.session.query(ProgramAreaDivision).filter_by(programareaid=programareaid, isactive=True,issection=False).order_by(ProgramAreaDivision.name.asc())
        return division_schema.dump(query)
    
    @classmethod
    def createprogramareadivision(cls, programareadivision)->DefaultMethodResult:
        created_at = datetime2.now().isoformat()
        newprogramareadivision = ProgramAreaDivision(programareaid=programareadivision["programareaid"], name=programareadivision["name"], isactive=True, created_at=created_at)
        db.session.add(newprogramareadivision)
        db.session.commit()      
        return DefaultMethodResult(True,'Division added successfully',newprogramareadivision.divisionid)

    @classmethod
    def disableprogramareadivision(cls, divisionid, userid):   
        dbquery = db.session.query(ProgramAreaDivision)
        division = dbquery.filter_by(divisionid=divisionid)
        if(division.count() > 0) :             
            division.update({ProgramAreaDivision.isactive:False,ProgramAreaDivision.updatedby:userid, ProgramAreaDivision.updated_at:datetime2.now()}, synchronize_session = False)
            db.session.commit()
            return DefaultMethodResult(True,'Division disabled successfully',divisionid)
        else:
            return DefaultMethodResult(True,'No Division found',divisionid)  
    
    @classmethod
    def updateprogramareadivision(cls, divisionid, programareadivision, userid):   
        dbquery = db.session.query(ProgramAreaDivision)
        division = dbquery.filter_by(divisionid=divisionid, isactive=True)
        if(division.count() > 0) :             
            division.update({ProgramAreaDivision.programareaid:programareadivision["programareaid"], ProgramAreaDivision.name:programareadivision["name"], 
                             ProgramAreaDivision.isactive:True, ProgramAreaDivision.sortorder:programareadivision["sortorder"],
                             ProgramAreaDivision.updatedby:userid, ProgramAreaDivision.updated_at:datetime2.now()}, synchronize_session = False)
            db.session.commit()
            return DefaultMethodResult(True,'Division updated successfully',divisionid)
        else:
            return DefaultMethodResult(True,'No Division found',divisionid)  
        
    @classmethod
    def getdivisionbynameandprogramarea(cls, programareadivision):   
        division_schema = ProgramAreaDivisionSchema(many=True)
        dbquery = db.session.query(ProgramAreaDivision)
        division = dbquery.filter_by(programareaid=programareadivision["programareaid"], isactive=True, name=programareadivision["name"])
        return division_schema.dump(division)
    
             

class ProgramAreaDivisionSchema(ma.Schema):
    class Meta:
        fields = ('divisionid','programareaid', 'name','isactive','sortorder','issection','parentid')