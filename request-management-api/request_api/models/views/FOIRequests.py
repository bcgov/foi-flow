from .db import db, ma
from sqlalchemy.dialects.postgresql import insert, base

class FOIRequests(db.Model):
    # Name of the table in our database
    __tablename__ = 'v_FOIRequests'
    # Defining the columns
    foiministryrequestid = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer)
    foirequest_id = db.Column(db.Integer)
    rawrequestid = db.Column(db.Integer)
    axisrequestid = db.Column(db.String(500))
    requeststatusid = db.Column(db.Integer)
    status = db.Column(db.String(100))
    assignedto = db.Column(db.String(500))
    assignedgroup = db.Column(db.String(500))
    assignedministryperson = db.Column(db.String(500))
    assignedministrygroup = db.Column(db.String(500))
    assignedtoformatted = db.Column(db.Text)
    ministryassignedtoformatted = db.Column(db.String(500))
    description = db.Column(db.Text)
    
