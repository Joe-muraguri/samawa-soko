from flask import  jsonify, request, render_template, flash, url_for
from datetime import datetime
from app.models.transactions import Transaction
from app.extensions import db
from flask import Blueprint
import requests
import base64
from app.config import Config
import os

def generate_access_token():
    consumer_key = os.getenv('CONSUMER_KEY')
    
    consumer_secret = os.getenv('CONSUMER_SECRET')

    if not consumer_key or not consumer_secret:
        raise ValueError("Missing CONSUMER_KEY or CONSUMER_SECRET in environment variables")


    #sandbox
    # url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    #live
    url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    try:
        
        encoded_credentials = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()

        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json"
        }

        # Send the request and parse the response
        response = requests.get(url, headers=headers).json()

        
        

        # Check for errors and return the access token
        if "access_token" in response:
            return response["access_token"]
        
        else:
            raise Exception("Failed to get access token: " + response["error_description"])
    except Exception as e:
        raise Exception("Failed to get access token: " + str(e)) 
    


