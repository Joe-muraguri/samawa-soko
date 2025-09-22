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
from twilio.rest import Client
from app.utils.utils import send_sms, send_email_with_pdf


checkout_bp = Blueprint('checkout', __name__)

CUSTOMER_EMAIL = ""

def lipa_na_mpesa(phone_number):
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
        "CallBackURL": "https://samawa.co.ke/api/checkout/callback",
        "AccountReference": "Online payment",
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
        CUSTOMER_EMAIL = data.get('email')
        print("Customer email is:", CUSTOMER_EMAIL)
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

        # Create order record
        new_order = Order(
            user_id=None,
            total=total,
            status='pending',
        )
        db.session.add(new_order)
        db.session.flush()  # Flush to get the ID without committing

        # Create order items
        for product_id, item_data in cart.items():
            product = Product.query.get(product_id)
            if product:
                order_item = OrderItem(
                    order_id=new_order.id,
                    product_id=product_id,
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
                db.session.add(order_item)

        db.session.commit()
        print("New order created with ID:", new_order.id)

        # Initiate M-Pesa payment
        result = lipa_na_mpesa(phone)

        checkout_id = result.get('CheckoutRequestID')
        print("CheckoutRequestID received:", checkout_id)
        
        if checkout_id:
            new_order.checkout_request_id = checkout_id
            db.session.commit()
        
        if result.get('ResponseCode') == '0':
            print("M-Pesa payment initiated successfully:", result)
            
            return jsonify({
                'success': True,
                'order_id': new_order.id,
                'checkout_request_id': checkout_id,
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
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@checkout_bp.route('/callback', methods=['POST'])
def payment_callback():
    try:
        callback_data = request.get_json()
        print("Raw callback data received:", callback_data)
        
        if not callback_data or 'Body' not in callback_data:
            print("Invalid callback data structure")
            return jsonify({'status': 'failed', 'message': 'Invalid callback data'}), 400
        
        stk_callback = callback_data['Body'].get('stkCallback', {})
        result_code = stk_callback.get('ResultCode')
        checkout_request_id = stk_callback.get('CheckoutRequestID')
        
        print("Callback Result code:", result_code)
        print("Callback CheckoutRequestID fr:", checkout_request_id)

        if not checkout_request_id:
            print("No CheckoutRequestID in callback")
            return jsonify({'status': 'failed', 'message': 'No CheckoutRequestID'}), 400

        # Find order by checkout_request_id
        order = Order.query.filter_by(checkout_request_id=checkout_request_id).first()
        if not order:
            print(f"No order found for CheckoutRequestID: {checkout_request_id}")
            return jsonify({'status': 'failed', 'message': 'Order not found'}), 404

        if result_code == 0:
            print("Payment successful, processing details...")
            
            # Extract payment details safely
            metadata = stk_callback.get('CallbackMetadata', {}).get('Item', [])
            payment_data = {}
            
            for item in metadata:
                if 'Name' in item and 'Value' in item:
                    payment_data[item['Name']] = item['Value']
            
            print("Payment data extracted:", payment_data)
            
            if 'Amount' in payment_data:
                order.total = payment_data['Amount']
            # Update order with payment details
            order.total = payment_data.get('Amount')
            order.status = 'completed'
            order.MpesaReceipt = payment_data.get('MpesaReceiptNumber')
            
            sms_message = f"Your payment of KES {order.total} was successful. Receipt: {order.MpesaReceipt}. Thank you for shopping with us!"
            print("SMS message to be sent:", sms_message)
            
            
            db.session.commit()
            print(f"Order {order.id} marked as completed with receipt {order.MpesaReceipt}")

            for item in metadata:
                if item.get('Name') == 'PhoneNumber':
                    phone_number = item.get('Value')
                    
            send_sms(sms_message,phone_number)
            # Example after payment success
            send_email_with_pdf(
                to_email=CUSTOMER_EMAIL,
                order_id=order.id,
                amount=order.total,
                phone=phone_number,
                shipping_details="Nairobi, Kenya",
                expected_time="3-5 business days"
            )

            
            # Clear cart from session
            if 'cart' in session:
                del session['cart']
                session.modified = True
            
            return jsonify({'status': 'success'}), 200
        else:
            # Payment failed
            order.status = 'failed'
            db.session.commit()
            print(f"Order {order.id} marked as failed. Result code: {result_code}")
            return jsonify({'status': 'failed', 'message': 'Payment failed'}), 400

    except Exception as e:
        print("Error processing payment callback:", str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@checkout_bp.route('/check-payment/<order_id>', methods=['GET'])
def check_payment(order_id):
    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'status': 'not_found'}), 404
        print("Checking payment status for order ID:", order_id)
        print("Order status before check:", order.status)
        if order.status == 'completed':
            return jsonify({
                'status': 'completed',
                'delivery_date': (datetime.utcnow() + timedelta(days=3)).strftime('%Y-%m-%d')
            })
        elif order.status == 'failed':
            return jsonify({'status': 'failed'})
        else:
            return jsonify({'status': 'pending'})

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500
    
