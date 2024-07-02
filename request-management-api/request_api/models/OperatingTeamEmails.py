
from .db import  db, ma
from sqlalchemy import text
import logging
from datetime import datetime

class OperatingTeamEmail(db.Model):
    __tablename__ = 'OperatingTeamEmails' 
    # Defining the columns
    emailid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    email_address = db.Column(db.String(255), nullable=False, unique=False)
    isactive = db.Column(db.Boolean, unique=False, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=True)
    #ForeignKey References
    teamid = db.Column(db.Integer, db.ForeignKey('OperatingTeams.teamid'))

    @classmethod
    def getalloperatingteamemails(cls):
        emails = []
        try:
            sql = """
                SELECT email_address, emailid, op.name FROM public."OperatingTeamEmails" em
                    JOIN public."OperatingTeams" op
                    ON em.teamid = op.teamid
                WHERE em.isactive = true
                ORDER BY emailid ASC
            """
            rs = db.session.execute(text(sql))
            for row in rs:
                emails.append({"email":row["email_address"], "name":row["name"]})
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return emails

    @classmethod
    def getoperatingteamemail(cls, operatingteamname):
        try:
            sql = """
                SELECT email_address FROM public."OperatingTeamEmails" em
                    JOIN public."OperatingTeams" op
                    ON em.teamid = op.teamid
                WHERE em.isactive = true and op.name = :operatingteamname
                ORDER BY emailid ASC
            """
            rs = db.session.execute(text(sql), {'operatingteamname': operatingteamname})
            for row in rs:
                email = row["email_address"]
        except Exception as ex:
            logging.error(ex)
            raise ex
        finally:
            db.session.close()
        return email

class OperatingTeamEmailSchema(ma.Schema):
    class Meta:
        fields = ('emailid', 'email_address', 'isactive','created_at','updated_at', 'teamid')