from __future__ import annotations

from .db import db, ma


class RevenueAccount(db.Model):
    __tablename__ = 'RevenueAccounts'
    # Defining the columns
    revenue_account_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client = db.Column(db.String(3), nullable=True)
    responsibility_centre = db.Column(db.String(5), nullable=True)
    service_line = db.Column(db.String(5), nullable=True)
    stob = db.Column(db.String(4), nullable=True)
    project_code = db.Column(db.String(7), nullable=True)

    @classmethod
    def find_by_id(cls, identifier: int):
        """Return by id."""
        return cls.query.get(identifier)

class RevenueAccountSchema(ma.Schema):
    class Meta:
        model = RevenueAccount
