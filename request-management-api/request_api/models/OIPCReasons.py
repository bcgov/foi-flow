
from .db import  db, ma

class OIPCReasons(db.Model):
    __tablename__ = 'OIPCReasons' 
    # Defining the columns
    reasonid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), unique=False, nullable=False)  
    isactive = db.Column(db.Boolean, unique=False, nullable=False)

    @classmethod
    def getreasons(cls):
        type_schema = ReasonSchema(many=True)
        query = db.session.query(OIPCReasons).filter_by(isactive=True).all()
        return type_schema.dump(query)


class ReasonSchema(ma.Schema):
    class Meta:
        fields = ('reasonid', 'name','isactive')