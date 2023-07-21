from .db import  db, ma
from .default_method_result import DefaultMethodResult
from sqlalchemy import text
import logging
class OperatingTeam(db.Model):
    __tablename__ = 'OperatingTeams' 
    # Defining the columns
    teamid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(255), unique=False, nullable=False)    
    description = db.Column(db.String(500), unique=False, nullable=True)
    type = db.Column(db.String(100), unique=False, nullable=True)
    isactive = db.Column(db.Boolean, unique=False, nullable=False)

    @classmethod
    def getalloperatingteams(cls):
        teams = []
        try:
            sql = """select name, type from "OperatingTeams" ot where ot.isactive = true"""
            rs = db.session.execute(text(sql))
            for row in rs:
                teams.append({"name":row["name"], "type":row["type"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return teams
    
    @classmethod
    def getteam(cls, team):    
        try:            
            sql = """select type, name from "OperatingTeams" ot 
                    where replace(lower(name),' ','') = replace(:team,' ','')"""
            rs = db.session.execute(text(sql), {'team': team})
            for row in rs:
                return {'type': row["type"], 'name': row['name']}
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return None
    

class OperatingTeamSchema(ma.Schema):
    class Meta:
        fields = ('teamid', 'name', 'description','type','isactive')