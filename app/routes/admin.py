from flask import Blueprint, jsonify, render_template, request
from app.utils.utils import role_required
from flask_jwt_extended import jwt_required


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
    from app.models.product import Product
    products = Product.query.all()
    return render_template('admin/products_page.html', products=products), 200
