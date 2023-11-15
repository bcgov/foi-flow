from .db import  db, ma

class OIPCOutcomes(db.Model):
    __tablename__ = 'OIPCOutcomes' 
    # Defining the columns
    outcomeid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), unique=False, nullable=False)  
    isactive = db.Column(db.Boolean, unique=False, nullable=False)

    @classmethod
    def getoutcomes(cls):
        type_schema = OutcomeSchema(many=True)
        query = db.session.query(OIPCOutcomes).filter_by(isactive=True).all()
        return type_schema.dump(query)


class OutcomeSchema(ma.Schema):
    class Meta:
        fields = ('outcomeid', 'name','isactive')