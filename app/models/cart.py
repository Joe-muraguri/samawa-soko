from app.extensions import db
from datetime import datetime

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    added_at = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User', backref='cart_items', lazy=True)
    product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))