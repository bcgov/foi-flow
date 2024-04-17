from .db import  db, ma
from datetime import datetime as datetime2
from .default_method_result import DefaultMethodResult
from sqlalchemy.orm import relationship,backref
from datetime import datetime
from sqlalchemy import text,or_

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
    specifictopersonalrequests = db.Column(db.Boolean, unique=False, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    createdby = db.Column(db.String(120), unique=False, default='system')
    updated_at = db.Column(db.DateTime, nullable=True)
    updatedby = db.Column(db.String(120), unique=False, nullable=True)
    type = db.Column(db.String(25), unique=False, nullable=True)
    
    @classmethod
    def getallprogramareadivisons(cls):
        division_schema = ProgramAreaDivisionSchema(many=True)
        query = db.session.query(ProgramAreaDivision).filter_by(isactive=True,issection=False).all()
        return division_schema.dump(query)
    
    @classmethod
    def getallprogramareadivisonsandsections(cls):
        division_schema = ProgramAreaDivisionSchema(many=True)
        query = db.session.query(ProgramAreaDivision).filter_by(isactive=True).all()
        return division_schema.dump(query)

    @classmethod
    def getprogramareadivisions(cls,programareaid):
        division_schema = ProgramAreaDivisionSchema(many=True)        
        query = db.session.query(ProgramAreaDivision).filter(ProgramAreaDivision.programareaid == programareaid, ProgramAreaDivision.isactive == True, ProgramAreaDivision.issection == False,or_(ProgramAreaDivision.specifictopersonalrequests == None,ProgramAreaDivision.specifictopersonalrequests == False))
        return division_schema.dump(query)

    @classmethod
    def getallprogramareatags(cls,programareaid):
        division_schema = ProgramAreaDivisionSchema(many=True)        
        query = db.session.query(ProgramAreaDivision).filter(ProgramAreaDivision.programareaid == programareaid, ProgramAreaDivision.isactive == True)
        return division_schema.dump(query)
    
    @classmethod
    def getpersonalspecificprogramareadivisions(cls,programareaid):
        division_schema = ProgramAreaDivisionSchema(many=True)
        query = db.session.query(ProgramAreaDivision).filter_by(programareaid=programareaid, isactive=True,issection=False,specifictopersonalrequests=True).order_by(ProgramAreaDivision.name.asc())
        return division_schema.dump(query)
    
    @classmethod
    def getpersonalrequestsprogramareasections(cls,programareaid):
        division_schema = ProgramAreaDivisionSchema(many=True)
        query = db.session.query(ProgramAreaDivision).filter_by(programareaid=programareaid, isactive=True,issection=True,specifictopersonalrequests=True).order_by(ProgramAreaDivision.name.asc())
        return division_schema.dump(query)
    
    @classmethod
    def getpersonalrequestsdivisionsandsections(cls,programareaid):
        division_schema = ProgramAreaDivisionSchema(many=True)
        query = db.session.query(ProgramAreaDivision).filter_by(programareaid=programareaid, isactive=True,specifictopersonalrequests=True).order_by(ProgramAreaDivision.name.asc())
        return division_schema.dump(query)
    
    @classmethod
    def getpersonalrequestsprogramareapeople(cls,programareaid):
        division_schema = ProgramAreaDivisionSchema(many=True)
        query = db.session.query(ProgramAreaDivision).filter_by(programareaid=programareaid,isactive=True,type='person',specifictopersonalrequests=True).order_by(ProgramAreaDivision.sortorder.asc(), ProgramAreaDivision.name.asc())
        return division_schema.dump(query)
    
    @classmethod
    def getpersonalrequestsprogramareavolumes(cls,programareaid):
        division_schema = ProgramAreaDivisionSchema(many=True)
        query = db.session.query(ProgramAreaDivision).filter_by(programareaid=programareaid,isactive=True,type='volume',specifictopersonalrequests=True).order_by(ProgramAreaDivision.sortorder.asc(), ProgramAreaDivision.name.asc())
        return division_schema.dump(query)
    
    @classmethod
    def getpersonalrequestsprogramareafiletypes(cls,programareaid):
        division_schema = ProgramAreaDivisionSchema(many=True)
        query = db.session.query(ProgramAreaDivision).filter_by(programareaid=programareaid,isactive=True,type='filetype',specifictopersonalrequests=True).order_by(ProgramAreaDivision.sortorder.asc(), ProgramAreaDivision.name.asc())
        return division_schema.dump(query)
    
    @classmethod
    def createprogramareadivision(cls, programareadivision)->DefaultMethodResult:
        created_at = datetime2.now().isoformat()
        newprogramareadivision = ProgramAreaDivision(
            programareaid=programareadivision["programareaid"], 
            name=programareadivision["name"], 
            isactive=True, 
            created_at=created_at, 
            issection=programareadivision["issection"],
            parentid=programareadivision["parentid"],
            specifictopersonalrequests=programareadivision["specifictopersonalrequests"]
            )
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
        # Below code ensures that sort order DB column does not contain 0 which has no impact on the sortorder
        sortorder = programareadivision["sortorder"] if programareadivision["sortorder"] != 0 else None
        if(division.count() > 0) :             
            division.update({ProgramAreaDivision.programareaid:programareadivision["programareaid"], ProgramAreaDivision.name:programareadivision["name"], 
                             ProgramAreaDivision.isactive:True, ProgramAreaDivision.sortorder:sortorder,
                             ProgramAreaDivision.issection:programareadivision["issection"], ProgramAreaDivision.parentid:programareadivision["parentid"],
                             ProgramAreaDivision.specifictopersonalrequests:programareadivision["specifictopersonalrequests"], ProgramAreaDivision.updatedby:userid, 
                             ProgramAreaDivision.updated_at:datetime2.now()}, synchronize_session = False)
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
    
    @classmethod
    def getchilddivisions(cls, divisonid):   
        division_schema = ProgramAreaDivisionSchema(many=True)
        query = db.session.query(ProgramAreaDivision).filter_by(parentid=divisonid, issection=True, isactive=True).all()
        return division_schema.dump(query)

class ProgramAreaDivisionSchema(ma.Schema):
    class Meta:
        fields = ('divisionid','programareaid','name','isactive','sortorder','issection','parentid','specifictopersonalrequests','type')