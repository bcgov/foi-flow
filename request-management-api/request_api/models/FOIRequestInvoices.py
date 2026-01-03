from flask.app import Flask
from sqlalchemy.sql.schema import ForeignKey, ForeignKeyConstraint
from .db import  db, ma
from sqlalchemy.orm import relationship, backref, aliased
from sqlalchemy import or_, and_, text, func, literal, cast, case, nullslast, nullsfirst, desc, asc
from sqlalchemy.sql.sqltypes import Date, Integer, String
from request_api.models.default_method_result import DefaultMethodResult
from sqlalchemy import text
import logging

class FOIRequestInvoices(db.Model):
    __tablename__ = "FOIRequestInvoices"
    # Defining the columns
    invoiceid = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    foirequestcfrfee_id = db.Column(db.Integer, ForeignKey('FOIRequestCFRFees.cfrfeeid'), nullable=False)
    foirequestcfrfeeversion_id = db.Column(db.Integer, ForeignKey('FOIRequestCFRFees.version'), nullable=False)
    documentpath = db.Column(db.Text, nullable=False)
    filename = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.String(120), nullable=False)
    applicant_name = db.Column(db.String(120), nullable=False)
    applicant_address = db.Column(db.String(200), nullable=False)

    @classmethod
    def get_invoice_by_cfrfeeid(cls, foicfrfeeid):
        return db.session.query(FOIRequestInvoices).filter(FOIRequestInvoices.foirequestcfrfee_id == foicfrfeeid).order_by(FOIRequestInvoices.invoiceid.desc()).first()

    @classmethod
    def getcurrentinvoiceid(cls):
        return db.session.query(FOIRequestInvoices).order_by(FOIRequestInvoices.invoiceid.desc()).first()

    @classmethod
    def save_invoice(cls, invoice, userid):
        try:
            new_invoice = FOIRequestInvoices(
                foirequestcfrfee_id=invoice["foirequestcfrfee_id"],
                foirequestcfrfeeversion_id=invoice["foicfrefeeversion_id"],
                documentpath=invoice["documentpath"],
                filename=invoice["filename"],
                applicant_name=invoice["applicant_name"],
                applicant_address=invoice["applicant_address"],
                created_at=invoice["created_at"].isoformat(),
                created_by=userid
            )
            db.session.add(new_invoice)
            db.session.commit()
            documentpath = new_invoice.documentpath
            return DefaultMethodResult(True, "FOIRequestInvoice entry created", documentpath)
        except Exception as exception:
            logging.error(f"Error: {exception}")
            return DefaultMethodResult(False, "FOIRequestInvoice entry unable to be created")
        finally:
            db.session.close()

    class FOIRequestInvoiceSchema(ma.Schema):
        class Meta:
            fields=('invoiceid', 'documentpath', 'foirequestcfrfee_id', 'foirequestcfrfeeversion_id', 'filename', 'applicant_name', 'applicant_address', 'created_at', 'created_by')