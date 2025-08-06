from flask import Blueprint, jsonify
from app.utils.utils import role_required
from flask_jwt_extended import jwt_required


admin_bp = Blueprint('admin', __name__)

@admin_bp.route('dashboard', methods=['GET'])
@jwt_required()
@role_required('admin')
def admin_dashboard():
    return jsonify({"message":"Welcome Admin"})