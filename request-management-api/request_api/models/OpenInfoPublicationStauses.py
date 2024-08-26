from .db import db, ma

class OpenInfoPublicationStatuses(db.Model):
    __tablename__ = "OpenInfoPublicationStatuses"
    # Defining the columns
    oipublicationstatusid = db.Column(
        db.Integer, primary_key=True, autoincrement=True, nullable=False
    )
    name = db.Column(db.String, nullable=False)
    isactive = db.Column(db.Boolean, nullable=False)

    @classmethod
    def getallpublicationstatuses(cls):
        type_schema = OpenInfoPublicationStatusSchema(many=True)
        query = db.session.query(OpenInfoPublicationStatuses).filter_by(isactive=True).all()
        return type_schema.dump(query)

class OpenInfoPublicationStatusSchema(ma.Schema):
    class Meta:
        fields = ("oipublicationstatusid", "name", "isactive")