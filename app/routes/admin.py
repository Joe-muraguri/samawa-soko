from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from app import db
from app.utils.utils import role_required
from flask_jwt_extended import jwt_required
from app.models.product import Product
from app.models.order import Order


admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard', methods=['GET'])
# @jwt_required()
# @role_required('admin')
def admin_dashboard():
    return render_template('admin/dashboard.html'), 200

@admin_bp.route('/products', methods=['GET'])
# @jwt_required()   
# @role_required('admin')
def admin_products():
    
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "")

    query = Product.query

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    products = query.order_by(Product.id.desc()).paginate(
        page=page,
        per_page=10,
        error_out=False
    )
    return render_template('admin/products_page.html', products=products,search=search), 200


@admin_bp.route("/orders")
def admin_orders():
    page = request.args.get("page", 1, type=int)
    search = request.args.get("q", "")
    status_filter = request.args.get("status", "")

    query = Order.query

    if search:
        query = query.filter(Order.user_name.ilike(f"%{search}%"))

    if status_filter:
        query = query.filter(Order.status == status_filter)

    orders = Order.query.order_by(Order.created_at.desc()).paginate(
        page=page,
        per_page=10,
        error_out=False
    )

    return render_template("admin/orders.html", orders=orders, search=search, status_filter=status_filter)


@admin_bp.route("/orders/<int:order_id>")
def view_order(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template("admin/order_detail.html", order=order)



@admin_bp.route("/orders/<int:order_id>/status", methods=["POST"])
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = request.form.get("status")
    db.session.commit()
    return redirect(url_for("admin.view_order", order_id=order.id))
