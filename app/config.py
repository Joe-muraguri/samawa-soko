import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite')
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'anothersecretkey')
    CORS_HEADERS = 'Content-Type'
    
    
    