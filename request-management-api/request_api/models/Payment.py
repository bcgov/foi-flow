from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import ForeignKey

from .db import db, ma


class Payment(db.Model):
    __tablename__ = 'Payments'
    # Defining the columns
    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fee_code_id = db.Column(db.Integer, ForeignKey('FeeCodes.fee_code_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String, nullable=False)
    request_id = db.Column(db.Integer, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.now, nullable=False)
    completed_on = db.Column(db.DateTime, default=None, nullable=True)
    paybc_url = db.Column(db.String, nullable=True)
    response_url = db.Column(db.String, nullable=True)
    order_id = db.Column(db.String(50), nullable=True)
    transaction_number = db.Column(db.String(50), nullable=True)

    @classmethod
    def find_by_id(cls, identifier: int) -> Payment:
        """Return by id."""
        return cls.query.get(identifier)

    @classmethod
    def find_paid_transaction(cls, transaction_number: str) -> Payment:
        """Return by transaction_number."""
        a =  cls.query.filter_by(transaction_number=transaction_number, status='PAID').one_or_none()
        return a

    @classmethod
    def find_failed_transaction(cls, transaction_number: str) -> Payment:
        """Return by transaction_number."""
        a =  cls.query.filter(Payment.transaction_number == transaction_number, Payment.status != 'PAID').one_or_none()
        return a

    @staticmethod
    def commit():
        """Commit the session."""
        db.session.commit()

    def flush(self):
        """Save and flush."""
        db.session.add(self)
        db.session.flush()
        return self


class PaymentSchema(ma.Schema):
    class Meta:
        model = Payment
        exclude = []
