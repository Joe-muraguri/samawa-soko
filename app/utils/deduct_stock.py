from app import db
from app.models.order import Order
from app.models.product import Product

def deduct_stock(order):
    if order.stock_deducted:
        return  # Prevent double deduction

    for item in order.items:
        product = Product.query.get(item.product_id)
        if product:
            product.stock = max(product.stock - item.quantity, 0)

    order.stock_deducted = True
    db.session.commit()
