from functools import wraps
from flask import jsonify, render_template
from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename
from app.config import S3_BUCKET, s3
import os
from app.utils.pdf_generate import generate_pdf
import smtplib
from email.message import EmailMessage
import resend
import logging
from threading import Thread
import pdfkit


resend.api_key = os.getenv("RESEND_API_KEY")


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
        server.login("joewarutere97@gmail.com", "cazn nzlv btdu guph")
        server.send_message(msg)
    print("Email sent successfully.")

def generate_order_pdf(order_id, amount, phone, shipping_details):
    """Generate PDF receipt - customize as needed"""
    html = render_template(
        'emails/order_receipt.html',  # create this template
        order_id=order_id,
        amount=amount,
        phone=phone,
        shipping_details=shipping_details
    )
    try:
        pdf = pdfkit.from_string(html, False)
        return pdf
    except Exception as e:
        logging.error(f"PDF generation failed: {e}")
        return None

def send_email_with_resend(
    to_email: str,
    order_id: int,
    amount: float,
    phone: str,
    shipping_details: str,
    expected_time: str = "3-5 business days"
):
    """
    Send order confirmation email with PDF receipt using Resend
    """
    if not to_email or not to_email.strip():
        logging.warning(f"Order {order_id}: No email provided, skipping send")
        return False

    to_email = to_email.strip()

    try:
        # Generate PDF receipt
        pdf_content = generate_order_pdf(order_id, amount, phone, shipping_details)

        # Email HTML body
        html_body = render_template(
            'emails/order_confirmation.html',
            order_id=order_id,
            amount=amount,
            phone=phone,
            shipping_details=shipping_details,
            expected_time=expected_time
        )

        params = {
            "from": "Samawa Soko <orders@samawa.co.ke>",  # Must be verified domain or use onresend.com for testing
            "to": [to_email],
            "subject": f"Order Confirmed #{order_id} - Thank You!",
            "html": html_body,
        }

        # Attach PDF if generated
        if pdf_content:
            params["attachments"] = [
                {
                    "filename": f"receipt_order_{order_id}.pdf",
                    "content": pdf_content,
                    "content_type": "application/pdf"
                }
            ]

        response = resend.Emails.send(params)
        logging.info(f"Order {order_id}: Email sent via Resend to {to_email} - ID: {response.get('id')}")
        return True

    except Exception as e:
        logging.error(f"Order {order_id}: Failed to send email via Resend: {str(e)}")
        return False


def send_confirmation_email_async(order_id, amount, phone, shipping_details, customer_email):
    if not customer_email or not customer_email.strip():
        logging.warning(f"Order {order_id}: No email to send confirmation")
        return

    def _send():
        send_email_with_resend(
            to_email=customer_email,
            order_id=order_id,
            amount=amount,
            phone=phone,
            shipping_details=shipping_details
        )

    thread = Thread(target=_send)
    thread.daemon = True
    thread.start()
