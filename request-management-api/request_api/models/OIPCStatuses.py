from .db import  db, ma

class OIPCStatuses(db.Model):
    __tablename__ = 'OIPCStatuses' 
    # Defining the columns
    statusid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), unique=False, nullable=False)  
    isactive = db.Column(db.Boolean, unique=False, nullable=False)

    @classmethod
    def getstatuses(cls):
        type_schema = StatusSchema(many=True)
        query = db.session.query(OIPCStatuses).filter_by(isactive=True).all()
        return type_schema.dump(query)


class StatusSchema(ma.Schema):
    class Meta:
        fields = ('statusid', 'name','isactive')