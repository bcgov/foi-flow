from .db import db, ma

class OpenInformationStatuses(db.Model):
    __tablename__ = "OpenInformationStatuses"
    # Defining the columns
    oistatusid = db.Column(
        db.Integer, primary_key=True, autoincrement=True, nullable=False
    )
    name = db.Column(db.String, nullable=False)
    isactive = db.Column(db.Boolean, nullable=False)

    @classmethod
    def getallstatuses(cls):
        type_schema = OpenInfoStatusSchema(many=True)
        query = db.session.query(OpenInformationStatuses).filter_by(isactive=True).all()
        return type_schema.dump(query)

class OpenInfoStatusSchema(ma.Schema):
    class Meta:
        fields = ("oistatusid", "name", "isactive")