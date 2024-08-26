from .db import db, ma

class OpenInformationExemptions(db.Model):
    __tablename__ = "OpenInformationExemptions"
    # Defining the columns
    oiexemptionid = db.Column(
        db.Integer, primary_key=True, autoincrement=True, nullable=False
    )
    name = db.Column(db.String, nullable=False)
    isactive = db.Column(db.Boolean, nullable=False)

    @classmethod
    def getallexemptions(cls):
        type_schema = OpenInfoExemptionSchema(many=True)
        query = db.session.query(OpenInformationExemptions).filter_by(isactive=True).all()
        return type_schema.dump(query)

class OpenInfoExemptionSchema(ma.Schema):
    class Meta:
        fields = ("oiexemptionid", "name", "isactive")