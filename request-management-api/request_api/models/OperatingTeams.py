from .db import  db, ma
from .default_method_result import DefaultMethodResult


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
        allteams = db.session.query(OperatingTeam).filter_by(isactive=True).all()
        for team in allteams:
            teams.append(team.name)
        return teams

class OperatingTeamSchema(ma.Schema):
    class Meta:
        fields = ('teamid', 'name', 'description','type','isactive')