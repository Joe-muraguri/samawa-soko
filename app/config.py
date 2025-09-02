import os
from dotenv import load_dotenv

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
    
    
    