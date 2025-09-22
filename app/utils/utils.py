from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename
from app.config import S3_BUCKET, s3
import os
from app.utils.pdf_generate import generate_pdf
import smtplib
from email.message import EmailMessage


def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            identity = get_jwt_identity()
            if not identity or identity.get('role') != required_role:
                return jsonify({"Error":"Unauthorized"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


def upload_file_to_s3(file, folder="products"):
    try:
        filename = secure_filename(file.filename)
        s3.upload_fileobj(
            file,
            S3_BUCKET,
            f"{folder}/{filename}",
            ExtraArgs={
                
                "ContentType": file.content_type
            }
        )
        return f"https://{S3_BUCKET}.s3.amazonaws.com/{folder}/{filename}"
    except Exception as e:
        print("S3 Upload Error:", e)
        return None


import requests
import json

API_URL = "https://sms.twachanga.co.ke/api/services/sendsms"


def send_sms(message, mobile):
    payload = {
        "apikey": os.getenv("SMS_API_KEY"),
        "partnerID": os.getenv("SMS_PARTNER_ID"),
        "message": message,
        "shortcode": os.getenv("SMS_SHORTCODE"),
        "mobile": mobile
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(API_URL, data=json.dumps(payload), headers=headers)
        print("Status Code:", response.status_code)

        
        try:
            print("Response:", response.json())
        except:
            print("Response:", response.text)

    except Exception as e:
        print("Error:", str(e))



def send_email_with_pdf(to_email, order_id, amount, phone, shipping_details, expected_time):
    # Generate PDF
    pdf_buffer = generate_pdf(order_id, amount, phone, shipping_details, expected_time)

    # Create email
    msg = EmailMessage()
    msg["Subject"] = "Your Order Receipt"
    msg["From"] = "joewarutere97@gmail.com"
    msg["To"] = to_email
    msg.set_content(
        f"Dear Customer,\n\nThank you for your payment.\nYour order {order_id} has been received.\n\nRegards,\nSAMAWATI"
    )

    # Attach PDF
    msg.add_attachment(
        pdf_buffer.read(),
        maintype="application",
        subtype="pdf",
        filename=f"receipt_{order_id}.pdf",
    )

    # Send email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login("joewarutere97@gmail.com", "kanjuriz")
        server.send_message(msg)
    print("Email sent successfully.")



