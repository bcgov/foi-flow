from .db import db, ma
from sqlalchemy.dialects.postgresql import insert, base

class FOINotifications(db.Model):
    # Name of the table in our database
    __tablename__ = 'v_FOINotifications'
    # Defining the columns
    id = db.Column(db.String(100), primary_key=True)
    idnumber = db.Column(db.String(100))
    axisnumber = db.Column(db.String(100))
    notification = db.Column(db.Text)
    notificationtypeid = db.Column(db.Integer)
    userid = db.Column(db.String(500))
    createdby = db.Column(db.String(500))
    created_at = db.Column(db.DateTime)
    userformatted = db.Column(db.Text)
    creatorformatted = db.Column(db.Text)
    notificationtype = db.Column(db.String(500))
    
