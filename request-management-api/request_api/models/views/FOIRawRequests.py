from .db import db, ma
from sqlalchemy.dialects.postgresql import insert, base

class FOIRawRequests(db.Model):
    # Name of the table in our database
    __tablename__ = 'v_FOIRawRequests'
    # Defining the columns
    rawrequestid = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer)
    axisrequestid = db.Column(db.String(500))
    foirequest_id = db.Column(db.Integer)
    ministryrequestid = db.Column(db.Integer)    
    status = db.Column(db.String(100))
    assignedto = db.Column(db.String(500))
    assignedgroup = db.Column(db.String(500))
    assignedministryperson = db.Column(db.String(500))
    assignedministrygroup = db.Column(db.String(500))
    assignedtoformatted = db.Column(db.Text)
    ministryassignedtoformatted = db.Column(db.String(500))
    description = db.Column(db.Text)
    isiaorestricted = db.Column(db.Boolean)
    crtid = db.Column(db.Text)
    
