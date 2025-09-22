from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename
from app.config import S3_BUCKET, s3
import os


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



