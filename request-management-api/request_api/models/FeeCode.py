from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import ForeignKey

from .db import db, ma


class FeeCode(db.Model):
    __tablename__ = 'FeeCodes'
    # Defining the columns
    fee_code_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(10), nullable=False)
    description = db.Column(db.String(100), unique=False, nullable=True)
    start_date = db.Column(db.Date, default=date.today(), nullable=False)
    end_date = db.Column(db.Date, default=None, nullable=True)
    fee = db.Column(db.Float, nullable=False)
    revenue_account_id = db.Column(db.Integer, ForeignKey('RevenueAccounts.revenue_account_id'), nullable=False)

    @classmethod
    def get_fee(cls, code: str,
                valid_date: date
                ) -> FeeCode:
        """Given a code and date, return the active fee code."""
        if not valid_date:
            valid_date = date.today()

        query = cls.query.filter_by(code=code). \
            filter(FeeCode.start_date <= valid_date). \
            filter((FeeCode.end_date.is_(None)) | (FeeCode.end_date >= valid_date))

        return query.one_or_none()

    @classmethod
    def find_by_id(cls, identifier: int) -> FeeCode:
        """Return by id."""
        return cls.query.get(identifier)


class FeeCodeSchema(ma.Schema):
    class Meta:
        model = FeeCode
        exclude = []
