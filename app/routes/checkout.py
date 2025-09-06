from flask import Blueprint, jsonify, request, render_template, flash, url_for, session, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.order import Order, OrderItem
from app.models.cart import CartItem
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from app.models.product import Product
from app.extensions import db
from flask_login import current_user
from app.routes.mpesa_payment import pay_with_mpesa
import uuid
from datetime import datetime, timedelta
from app.utils.mpesa import generate_access_token
import os
import base64
import requests

checkout_bp = Blueprint('checkout', __name__)

def lipa_na_mpesa(phone_number,order_id):
    token = generate_access_token()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    shortCode = os.getenv('SHORT_CODE')  #sandbox -174379
    passkey = os.getenv('PASSKEY')
    stk_password = base64.b64encode((shortCode + passkey + timestamp).encode('utf-8')).decode('utf-8')



    #choose one depending on you development environment
    #sandbox
    # url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    #!live
    url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }

    requestBody = {
        "BusinessShortCode": shortCode,
        "Password": stk_password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline", #till "CustomerBuyGoodsOnline"
        "Amount": 1,
        "PartyA": phone_number,
        "PartyB": os.getenv('SHORT_CODE'),
        "PhoneNumber": phone_number,
        "CallBackURL": "https://samawa.co.ke/callback",
        "AccountReference": str(order_id),
        "TransactionDesc": "Payment for order"
    }

    try:
        response = requests.post(url, json=requestBody, headers=headers)
        print(response.json())
        return response.json()
    except Exception as e:
        print('Error:', str(e))


@checkout_bp.route('/checkout', methods=['GET'])
# @jwt_required()
def checkout():
    cart = session.get('cart', {})
    print("Current cart contents at checkout:", cart)
    if not cart:
        flash("Your cart is empty", "warning")
        return redirect(url_for('cart.view_cart'))
    
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render_template('checkout.html', cart_total=total, cart=cart)

@checkout_bp.route('/initiate-payment', methods=['POST'])

def initiate_payment():
    try:
        data = request.get_json()
        phone = data.get('phone')
        if phone.startswith('07'):
            phone = '254' + phone[1:]
        print("Phone number to use is:", phone)
        
        
        if not phone:
            return jsonify({
                'success': False,
                'message': 'Phone number is required'
            }), 400

        cart = session.get('cart', {})
        if not cart:
            return jsonify({
                'success': False,
                'message': 'Your cart is empty'
            }), 400

        total = sum(item['price'] * item['quantity'] for item in cart.values())
        print("Total amount to be paid:", total)
        print("Cart contents:", cart)
        # order_id = uuid.uuid4()

        # Create order record
        new_order = Order(
            
            user_id=None,
            total=total,
            status='pending',
            
        )
        db.session.add(new_order)
        db.session.commit()

        print("New order created with ID:", new_order.id)

        # Use the UUID field for payment reference
        payment_reference = new_order.uuid
        print("Payment reference (UUID):", payment_reference)

        # Initiate M-Pesa payment
        result = lipa_na_mpesa(phone, new_order.id)
        
        if result.get('ResponseCode') == '0':
            print("M-Pesa payment initiated successfully:", result)
            # For testing purposes, we can simulate the callback immediately
            payment_callback()  # Simulate callback for testing purposes

            # Store pending order in session
            session['pending_order'] = {
                'order_id': new_order.id,
                'phone': phone,
                'amount': total,
                'created_at': datetime.utcnow().isoformat()
            }
            
            return jsonify({
                'success': True,
                'order_id': new_order.id,
                'message': 'Payment initiated. Check your phone.'
            })
        else:
            new_order.status = 'failed'
            db.session.commit()
            return jsonify({
                'success': False,
                'message': result.get('ResponseDescription', 'Payment initiation failed')
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@checkout_bp.route('/check-payment/<order_id>', methods=['GET'])

def check_payment(order_id):
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'payment_status': 'not_found'}), 404
        print("Checking payment status for order ID:", order_id)
        print("Order status before check:", order.status)
        if order.status == 'completed':
            return jsonify({
                'payment_status': 'completed',
                'delivery_date': (datetime.utcnow() + timedelta(days=3)).strftime('%Y-%m-%d')
            })
        elif order.status == 'failed':
            return jsonify({'payment_status': 'failed'})
        else:
            return jsonify({'payment_status': 'pending'})

    except Exception as e:
        return jsonify({
            'payment_status': 'error',
            'message': str(e)
        }), 500

@checkout_bp.route('/callback', methods=['POST'])
def payment_callback():
    try:
        callback_data = request.json
        print("Callback data received:", callback_data)
        result_code = callback_data['Body']['stkCallback']['ResultCode']
        
        if result_code == 0:
            # Extract payment details
            metadata = callback_data['Body']['stkCallback']['CallbackMetadata']['Item']
            amount = next(item['Value'] for item in metadata if item['Name'] == 'Amount')
            phone = next(item['Value'] for item in metadata if item['Name'] == 'PhoneNumber')
            receipt = next(item['Value'] for item in metadata if item['Name'] == 'MpesaReceiptNumber')
            order_id = next(item['Value'] for item in metadata if item['Name'] == 'MerchantRequestID')

            print(f"Payment successful: Amount={amount}, Phone={phone}, Receipt={receipt}, Order ID={order_id}")

            # Update order status
            order = Order.query.get(order_id)
            if order:
                order.status = 'completed'
                order.payment_receipt = receipt
                db.session.commit()
                print(f"Order {order_id} marked as completed.")
                
                
                # Clear cart
                if 'cart' in session:
                    session.pop('cart')
                
                return jsonify({'status': 'success'}), 200
        
        return jsonify({'status': 'failed'}), 400

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500