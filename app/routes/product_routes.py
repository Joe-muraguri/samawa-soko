from flask import Blueprint, request, jsonify, render_template, url_for, flash,redirect
from flask_jwt_extended import jwt_required
from app.utils.utils import role_required
from app import db
from app.models.product import Product
import os
from werkzeug.utils import secure_filename
import uuid
from app.config import S3_BUCKET, s3





product_bp = Blueprint('product', __name__)

@product_bp.route('/', methods=['GET'])
def get_products():
    products = Product.query.all()
    return render_template('index.html', products=products) 
    #! return jsonify([{"id":p.id, "name":p.name, "description":p.description, "price":p.price} for p in products]), 200  API end point

@product_bp.route('/<int:id>', methods=['GET'])
def get_product(id):
    product = Product.query.get_or_404(id)
    if not product:
        return jsonify({"message":"Product not found"}), 404
    return render_template('product_details.html', product=product)  # Render a template with the product details
     #! return jsonify({"id":product.id, "name": product.name,"price":product.price, "description": product.description}), 200 API end point



ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@product_bp.route('/create_product', methods=['GET','POST'])
# @jwt_required()
# @role_required('admin')
def create_product():
    if request.method == 'POST':
        name = request.form.get("name")
        description = request.form.get("description")
        price = request.form.get("price")
        stock = request.form.get("stock", 0)
        file = request.files.get("image_url")

        print("Form data:", request.form)
        print("Files:", request.files)

        # Validate image file
        if not file or not allowed_file(file.filename):
            return jsonify({"Error": "Invalid image file"}), 400

        # Generate a unique file name
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"

        try:
            # Upload to S3
            s3.upload_fileobj(
                file,
                S3_BUCKET,
                f"products/{unique_filename}",
                ExtraArgs={
                    "ACL": "public-read",
                    "ContentType": file.content_type
                }
            )

            # Get public image URL from S3
            image_url = f"https://{S3_BUCKET}.s3.amazonaws.com/products/{unique_filename}"

        except Exception as e:
            print("S3 Upload Error:", e)
            return jsonify({"Error": "Failed to upload image"}), 500

        # Validate required fields
        if not name or not price or not description:
            return jsonify({"message": "Missing required fields"}), 400

        # Save product to database
        product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            image_url=image_url
        )

        db.session.add(product)
        db.session.commit()

        # Handle AJAX request or normal form submission
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"message": "Product created successfully"}), 200
        else:
            flash("Product created successfully", "success")
            return redirect(url_for('product_bp.create_product'))

    return render_template('create_product.html')
    #! return jsonify({"message":"Product added successfully"}), 201  For API end point

@product_bp.route('/<int:id>/edit', methods=['GET'])
def api_get_product(id):
    product = Product.query.get_or_404(id)
    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock,
        'image_url': product.image_url,  # or wherever your image is
        
    })

def serialize_product(product):
    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "description": product.description,
        "image_url": product.image_url,
        # add all relevant fields here
    }


@product_bp.route('/<int:product_id>/edit', methods=["GET","PUT"])
# @jwt_required()
# @role_required('admin')
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    print("product", product)
    if not product:
        return jsonify({"message":"Product not found"})
    
    

    product.name = request.form.get('name', product.name)
    product.description = request.form.get('description', product.description)
    product.price = request.form.get('price', product.price)
    product.stock = request.form.get('stock', product.stock)
    product.image_url = request.files.get('image_url', product.image_url)

    db.session.commit()

    return jsonify({"message":"Product updated successfully", "product":serialize_product(product)}), 200


@product_bp.route('/<int:product_id>/delete', methods=['DELETE'])
# @jwt_required()
# @role_required('admin')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    try:
        # Delete associated image if exists
        if product.image_url:
            image_path = os.path.join('UPLOAD_FOLDER', product.image_url)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(product)
        db.session.commit()
        
        # Return JSON response for API calls
        return jsonify({
            'status': 'success',
            'message': 'Product deleted successfully',
            'redirect': url_for('product.get_products')
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting product {product_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

