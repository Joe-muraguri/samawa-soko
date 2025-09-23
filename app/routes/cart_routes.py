from flask import Blueprint, redirect, url_for, jsonify, flash, request, render_template,session
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.cart import CartItem
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from app.models.product import Product
from app.extensions import db
from app.utils.cart_helpers import get_cart_data


cart_bp = Blueprint('cart', __name__)


@cart_bp.route('/<int:product_id>/add_cart', methods=['POST'])
# @jwt_required()
def add_to_cart(product_id):
    print("Add to cart called")
    cart = get_cart_data(session)
    # if not current_user.is_authenticated:
    #     return jsonify({
    #         "message":"Please login to continue",
    #         "login_url": url_for('login')
    #     }), 401 #unauthorized
    # user_id =1  #get_jwt_identity()
    data = request.get_json()
    print("Data received from database of the product to add to cart:", data)
    product_id = str(data.get('product_id'))
    quantity = int(data.get('quantity', 1))
    
    product = Product.query.get_or_404(product_id)
    if not product:
        return jsonify({"message":"Product not found"}), 404
    
    #Initialize cart in session if it doesn't exist
    if 'cart' not in session:
        session['cart'] = {}
    cart = session['cart']

    #Add/update the product in the cart
    if product_id in cart:
        cart[product_id]['quantity'] += quantity
    else:
        cart[product_id] = {
            'product_id': product.id,
            'product_name': product.name,
            'quantity': quantity,
            'price': product.price,
            'image_url': product.image_url if hasattr(product, 'image_url') else None
        }
    # save the cart back to the session
    session['cart'] = cart
    session.modified = True

    #Calculate the cart totals
    cart_total = sum(item['price'] * item['quantity'] for item in cart.values())
    cart_count = sum(item['quantity'] for item in cart.values())
    print("Cart after addition:", cart)
    print(f"{product.name} added to cart. Cart total: {cart_total}, Cart count: {cart_count}")
    return jsonify({
        "success": True,
        "cart_item":cart[product_id],
        "cart_total": cart_total,
        "cart_count": cart_count,
        "message": f"{product.name} added to cart successfully!",
    })

    # cart_item = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()      #user_id=current_user.id,

    # if cart_item:
    #     cart_item.quantity += quantity
    # else:
    #     cart_item = CartItem( product_id=product_id, quantity=quantity, user_id=user_id)
    #     db.session.add(cart_item)

    # db.session.commit()
    # flash("Product added to cart")

    # #calculate subtotal
    # subtotal = product.price * cart_item.quantity

    # return jsonify({
    #     "Cart_Item": {
    #         "product_id": cart_item.product_id,
    #         "product_name":product.name,
    #         "quantity":cart_item.quantity,
    #         "subtotal": subtotal
    #     }
    # })



    

    
@cart_bp.route('/', methods=['GET'])
# @jwt_required()
def view_cart():
    cart = session.get('cart', {})
    print(f"The cart that is being viewed: {cart}")
    subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
    cart_count = sum(item['quantity'] for item in cart.values())
    discount = 0.1 * subtotal if subtotal > 1000 else 0
    return render_template('cart.html', cart={
        "items": cart,
        "subtotal": subtotal,
        "cart_count": cart_count,
        "discount": discount,
        "total": subtotal - discount
    })


    # user_id = get_jwt_identity()
    # cart_items = CartItem.query.filter_by(user_id=user_id).all()
    # cart_items = CartItem.query.all()
    # if not cart_items:
    #     return jsonify({"message":"Cart is empty"}), 200
    

    # cart_data = []
    # for item in cart_items:
    #     product = item.product
    #     cart_data.append({
    #         'item_id':item.id,
    #         'product_id':product.id,
    #         'product_name':product.name,
    #         'quantity':item.quantity,
    #         'price':product.price,
    #         "total":product.price * item.quantity
    #     })
    # print("Cart data:", cart_data)

    # # return jsonify({"cart":cart_data}), 200
    # return render_template('cart.html', cart_data=cart_data)

    

    
@cart_bp.route('/update/<int:product_id>', methods=['POST'])
# @jwt_required()
def update_cart(product_id):
    # user_id = get_jwt_identity()
    # cart_item = CartItem.query.filter_by(id=cart_id, user_id=user_id).first()
    # if not cart_item:
    #     return jsonify({"message":"Cart item not found"}), 404
    
    data = request.get_json()

    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if not product_id or not quantity:
        return jsonify({"message":"Invalid data"}), 400
    
    cart = session.get('cart', {})

    if str(product_id) in cart:
        try:
            cart[str(product_id)]['quantity'] = int(quantity)
            session['cart'] = cart
            session.modified = True

            subtotal = sum(item['price'] * item['quantity'] for item in cart.values())
            total_items = sum(item['quantity'] for item in cart.values())
            discount = 0.1 * subtotal if subtotal > 1000 else 0
            total = subtotal - discount
            print(f"Cart after update: {cart}")
            print(f"Total after update: {total}, Cart count: {total_items}")
            flash(f"Cart updated successfully!", "success")

            return jsonify({'success': True, 'message': 'Cart updated successfully', 'cart': cart, 'totals':{
                'subtotal': subtotal,
                'discount': discount,
                'total': total,
                'cart_count': total_items
            }}), 200
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid quantity'}), 400
    return jsonify({'success': False, 'message': 'Product not found in cart'}), 404


    


@cart_bp.route('/<int:cart_id>', methods=['POST'])
# @jwt_required()
def remove_from_cart(cart_id):
    product_id = str(cart_id)
    print("Cart ID received:", cart_id)
    print("Product ID to delete:", product_id)
    print("Session Cart Keys:", list(session.get('cart', {}).keys()))
    if 'cart' in session and product_id in session['cart']:
        removed_item = session['cart'].pop(product_id)
        session.modified = True
        flash(f"{removed_item['product_name']} removed from cart successfully!", "success")
        return redirect(url_for('cart.view_cart'))  # Redirect back to cart page
    
    flash("Item not found in cart", "error")
    return redirect(url_for('cart.view_cart'))





    # user_id =get_jwt_identity()
    # cart_item = CartItem.query.filter_by(id=cart_id, user_id=user_id).first()
    # if not cart_item:
    #     return jsonify({"message" : "Cart item not found"}), 404
    
    # db.session.delete(cart_item)
    # db.session.commit()
    # return jsonify({"message":"Item removed from cart"}), 200


def clear_cart():
    if 'cart' in session:
        session.pop('cart', None)
        return jsonify({"message":"Cart cleared successfully"}), 200
    return jsonify({"message":"Cart is already empty"}), 200




