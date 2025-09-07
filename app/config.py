import os
from dotenv import load_dotenv
import boto3

load_dotenv()

class Config:

    # 🚀 RENDER PRODUCTION DATABASE (Uncomment for deployment)
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://', 1)
    
    
    # SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/uza_db'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL','postgresql://postgres:postgres@localhost:5432/uza_db')
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'anothersecretkey')
    CORS_HEADERS = 'Content-Type'

  

    S3_BUCKET = os.getenv("AWS_S3_BUCKET_NAME")
    S3_REGION = os.getenv("AWS_REGION")
    S3_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
    S3_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

    s3 = boto3.client(
        "s3",
        region_name=S3_REGION,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY
    )
    
    
    