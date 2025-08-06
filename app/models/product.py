from app.extensions import db
from datetime import datetime

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<Product {self.name}>'

    # def to_dict(self):
    #     return {
    #         'id':self.id,
    #         'name':self.name,
    #         'description':self.description,
    #         'price':self.price,
    #         'stock':self.stock,
    #         'image_url':self.image_url,
    #         'created_at':self.created_at
    #     }