from datetime import datetime
from app.extensions import db
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    mpesa_code = db.Column(db.String(255), unique=True, nullable=False)
    status = db.Column(db.String(255), nullable=False, default="pending")
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f"Transaction('{self.phone}', '{self.amount}', '{self.mpesa_code}', '{self.status}')"
