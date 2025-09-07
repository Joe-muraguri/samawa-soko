from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from werkzeug.utils import secure_filename
from app.config import S3_BUCKET, s3


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
                "ACL": "public-read",
                "ContentType": file.content_type
            }
        )
        return f"https://{S3_BUCKET}.s3.amazonaws.com/{folder}/{filename}"
    except Exception as e:
        print("S3 Upload Error:", e)
        return None
