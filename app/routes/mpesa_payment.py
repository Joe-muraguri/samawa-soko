from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import requests
import base64
import datetime
from app.models.order import Order
from app.extensions import db

from app.config import Config
import os
from app.utils.mpesa import generate_access_token
from datetime import datetime


payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/pay/mpesa', methods=['POST'])
# @jwt_required
def pay_with_mpesa(phone_number,amount, order_id):
    # user_id = get_jwt_identity()
    data = request.get_json()
    order_id = data.get('order_id')
    phone_number = data.get('phone_number')

    order = Order.query.filter_by(id=order_id).first()
    if not order:
        return jsonify({"message":"Order not found"}), 404
    
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
        "Amount": order.total_price,
        "PartyA": phone_number,
        "PartyB": os.getenv('SHORT_CODE'),
        "PhoneNumber": phone_number,
        "CallBackURL": "https://samawa.co.ke/callback",
        "AccountReference": str(order.id),
        "TransactionDesc": "Payment for order"
    }
    
    try:
        response = requests.post(url, json=requestBody, headers=headers)
        print(response.json())
        return response.json()
    except Exception as e:
        print('Error:', str(e))


@payment_bp.route('/callback', methods=['POST'])
def mpesa_callback():
    try:
        callback_data = request.json
        print(callback_data)
        result_code = callback_data['Body']['stkCallback']['ResultCode']

        
        

        if result_code == 0:
            callback_metadata = callback_data['Body']['stkCallback']['CallbackMetadata']
            amount = None
            phone_number = None
            for item in callback_metadata['Item']:
                if item['Name'] == 'Amount':
                    amount = item['Value']
                    print(f"Paid Amaount is : {amount}")
                elif item['Name'] == 'PhoneNumber':
                    phone_number = item['Value']
                    print(f"Phone number is : {phone_number}")
                elif item['Name'] == 'MpesaReceiptNumber':
                    mpesa_code = item['Value']
                    print(f"Mpesa code is : {mpesa_code}")
                elif item['Name'] == 'MerchantRequestID':
                    order_id = item['Value']
                    

            #Saving the data in the database
            
            order = Order.query.get(order_id)
            if order:
                order.status = 'Paid'
                db.session.commit()
                return jsonify({"status":"success", "message":"Order has been paid", "transaction_id":mpesa_code})
        return jsonify({"status":"failed", "message":"Order not found"})
    except Exception as e:
        print('Error:', str(e))
        return jsonify({"status":"failed", "message":"An error occurred"}), 500
