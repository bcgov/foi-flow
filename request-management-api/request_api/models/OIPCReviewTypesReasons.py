from .db import  db, ma
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy import text

class OIPCReviewTypesReasons(db.Model):
    __tablename__ = 'OIPCReviewTypesReasons' 
    # Defining the columns
    reviewtypereasonid = db.Column(db.Integer, primary_key=True,autoincrement=True)
    reviewtypeid = db.Column(db.Integer, ForeignKey('FOIReviewTypes'))
    relationship("FOIReviewTypes", backref=backref("FOIReviewTypes"), uselist=False)
    reasonid = db.Column(db.Integer, ForeignKey('FOIReasons'))
    relationship("FOIReasons", backref=backref("FOIReasons"), uselist=False)
    isactive = db.Column(db.Boolean, unique=False, nullable=False)

    @classmethod
    def getreviewtypeswithreasons(cls):
        type_schema = ReviewTypeReasonSchema(many=True)
        sql = '''
            SELECT types.reviewtypeid, reasons.reasonid, reasons.name as reason_name, types.name as type_name, typereason.isactive as reviewtypereason_isactive, reasons.isactive as reason_isactive, types.isactive as reviewtype_isactive FROM public."OIPCReviewTypesReasons" typereason
            JOIN public."OIPCReasons" reasons
            ON reasons.reasonid = typereason.reasonid
            JOIN public."OIPCReviewTypes" types
            ON types.reviewtypeid = typereason.reviewtypeid
            ORDER BY reviewtypereasonid ASC
            '''
        rs = db.session.execute(text(sql))
        reviewtypereasons = []
        for row in rs:
            reviewtypereasons.append({
                "reviewtypeid": row["reviewtypeid"], 
                "reasonid": row["reasonid"],
                "reason_name": row["reason_name"],
                "type_name": row["type_name"],
                "reviewtypereason_isactive": row["reviewtypereason_isactive"],
                "reviewtype_isactive": row["reviewtype_isactive"],
                "reason_isactive": row["reason_isactive"],
                })
        return reviewtypereasons

class ReviewTypeReasonSchema(ma.Schema):
    class Meta:
        fields = ('reviewtypereasonid', 'reviewtypeid', 'reasonid', 'isactive')