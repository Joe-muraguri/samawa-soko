from app.extensions import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Keep existing integer ID
    uuid = db.Column(UUID(as_uuid=True), unique=True, default=uuid.uuid4)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Pending')  #! Shipped||Delivered||Paid||pending
    created_at = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User', backref='orders', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    order = db.relationship('Order', backref='order_items', lazy=True)
    product = db.relationship('Product', backref='order_items', lazy=True)