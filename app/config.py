import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite')
    SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'anothersecretkey')
    CORS_HEADERS = 'Content-Type'
    GOOGLE_OAUTH_CLIENT_ID = '298794906563-am32mqt1ut5rep8vh0vc6q7ta3nd6g4k.apps.googleusercontent.com'
    GOOGLE_OAUTH_CLIENT_SECRET = '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'