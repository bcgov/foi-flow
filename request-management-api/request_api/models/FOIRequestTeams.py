from .db import  db, ma
from .default_method_result import DefaultMethodResult
from sqlalchemy.orm import relationship,backref
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy import text
import logging
class FOIRequestTeam(db.Model):
    __tablename__ = 'FOIRequestTeams' 
    # Defining the columns
    requestteamid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    requesttype = db.Column(db.String(100), unique=False, nullable=True)
    requeststatusid = db.Column(db.Integer,ForeignKey('FOIRequestStatuses.requeststatusid'))
    teamid = db.Column(db.Integer,ForeignKey('OperatingTeams.teamid'))
    programareaid = db.Column(db.Integer,ForeignKey('ProgramAreas.programareaid'))
    isactive = db.Column(db.Boolean, unique=False, nullable=False)

    @classmethod
    def getrequestteams(cls):
        programarea_schema = FOIRequestTeamSchema(many=True)
        query = db.session.query(FOIRequestTeam).filter_by(isactive=True).all()
        return programarea_schema.dump(query)
    
    @classmethod
    def getteamsbystatusandprogramarea(cls, requesttype, status, bcgovcode):  
        teams = []
        try:              
            sql = """select ot."name" as name, ot."type" as type from "FOIRequestTeams" ft inner join "FOIRequestStatuses" fs2 on ft.requeststatusid = fs2.requeststatusid 
                    inner join "OperatingTeams" ot on ft.teamid = ot.teamid 
                    left join "ProgramAreas" pa on ft.programareaid = pa.programareaid 
                    where ft.isactive = true and lower(ft.requesttype) = :requesttype 
                    and replace(lower(fs2."name"),' ','') = :status
                    and (lower(pa.bcgovcode) = :bcgovcode or ft.programareaid  is null)"""
            rs = db.session.execute(text(sql), {'requesttype': requesttype, 'status': status,'bcgovcode':bcgovcode})
        
            for row in rs:
                teams.append({"name":row["name"], "type":row["type"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return teams
    
    @classmethod
    def getprocessingteamsbytype(cls, requesttype):    
        teams = []
        try:            
            sql = """select ot."name" as team, pa."name" as ministry, pa.bcgovcode, pa.iaocode from "FOIRequestTeams" ft 
                    inner join  "OperatingTeams" ot on ft.teamid = ot.teamid
                    inner join "ProgramAreas" pa on ft.programareaid = pa.programareaid 
                    where lower(ft.requesttype) = :requesttype and ft.programareaid is not null
                    and ot."type" = 'iao'
                    and ft.requeststatusid = 8"""
            rs = db.session.execute(text(sql), {'requesttype': requesttype})
            for row in rs:
                teams.append({"team":row["team"], "ministry":row["ministry"], "bcgovcode":row["bcgovcode"], "iaocode":row["iaocode"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return teams
    
    @classmethod
    def getdefaultprocessingteamforpersonal(cls, bcgovcode):   
        defaultteam = None
        try: 
            sql = """select ot."name" as name from "FOIRequestTeams" ft inner join "FOIRequestStatuses" fs2 on ft.requeststatusid = fs2.requeststatusid 
                    inner join "OperatingTeams" ot on ft.teamid = ot.teamid 
                    left join "ProgramAreas" pa on ft.programareaid = pa.programareaid 
                    where ft.isactive = true and lower(ft.requesttype) = 'personal' 
                    and replace(lower(fs2."name"),' ','') = 'open'
                    and ot."name" <> 'Intake Team'
                    and (lower(pa.bcgovcode) = :bcgovcode or ft.programareaid  is null)"""
            rs = db.session.execute(text(sql), {'bcgovcode':bcgovcode.lower()})
            for row in rs:
                defaultteam = row["name"]
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return defaultteam
    
class FOIRequestTeamSchema(ma.Schema):
    class Meta:
        fields = ('requestteamid', 'requesttype', 'requeststatusid','teamid','programareaid','isactive')