from flask import Blueprint, jsonify, request, render_template, flash, url_for, session, redirect
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.order import Order, OrderItem
from app.extensions import db

order_bp = Blueprint('order', __name__)

## VIEW USER ORDERS
@order_bp.route('/orders', methods=['GET'])
@jwt_required()
def get_orders():
    user_id = get_jwt_identity()
    orders = Order.query.filter_by(user_id=user_id).all()
    order_data = []
    for order in orders:
        order_items = OrderItem.query.filter_by(order_id=order.id).all()
        items = []
        for item in order_items:
            items.append({
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "price": item.price
            })
        order_data.append({
            "order_id": order.id,
            "total_price": order.total_price,
            "items": items
        })
    return jsonify(order_data), 200

# SINGLE ORDER
@order_bp.route('/order/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    user_id = get_jwt_identity()
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({"message":"Order not found"}), 404
   
    order_details = {
         "order_id": order.id,
        "total_price": order.total_price,
        "status": order.status,
        "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "items": [
            {
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "price": item.price
            } for item in order.order_items
        ]
   }
    return jsonify(order_details), 200

# update order status
@order_bp.route('/order/<int:order_id>', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user or not user.is_admin: #! check if user is admin
        return jsonify({"message":"Unauthorized"}), 401
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"message":"Order not found"}), 404
    data = request.get_json()
    new_status = data.get('status')

    if new_status not in ['Paid','pending', 'shipped', 'delivered']:
        return jsonify({"message":"Invalid status"}), 400
    order.status = new_status
    db.session.commit()
    return jsonify({"message":"Order status updated successfully"}), 200

@order_bp.route('/order_process', methods=['GET'])
def order_process():
    return render_template('order_process.html')

@order_bp.route('/create_order', methods=['POST'])
@jwt_required()
def create_order():
    user_id = get_jwt_identity()
    data = request.get_json()
    order_id = data.get('order_id')
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({"message":"Order not found"}), 404
    order.status = 'pending'
    db.session.commit()
    return jsonify({"message":"Order created successfully"}), 201


@order_bp.route('/order-status/<int:order_id>')
def wait_for_payment(order_id):
    order = Order.query.get(order_id)
    if order.status == 'paid':
        flash("Payment successful! Your order has been placed.")
        session['cart'] = []  # clear cart
        return redirect(url_for('success'))
    return render_template('waiting.html', order=order)
