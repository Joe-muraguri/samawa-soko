from flask import Blueprint, request, jsonify, render_template, redirect, url_for, abort, flash,session
from app import db
from datetime import datetime, timedelta
import secrets
import smtplib
from email.message import EmailMessage
from app.models.user import User
from werkzeug.security import check_password_hash,generate_password_hash
from flask_jwt_extended import create_access_token
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

import os

auth_bp = Blueprint('auth', __name__)
google_bp = make_google_blueprint(
    client_id= os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    redirect_to= 'auth.google_callback'
)

@auth_bp.route('/register', methods=['POST'])
def register():
    #chech if the user is already authenticated first
    # if current_user.is_authenticated:
    #     return jsonify({
    #         "message":"You're already logged in",
    #         "redirect": url_for('home')
    #     }), 200
    

    #get the data from the incoming JSOn request from the user
    data = request.get_json()

    #validate required fields
    if not data or not data.get("name") or not data.get("email") or not data.get("password"):
        return jsonify({"Message":"Name, Email and Password are required"}), 400
    
    #check if the user already exist
    user = User.query.filter_by(email=data["email"]).first()

    if user:
        return jsonify({
            "message":f"User with email {data['email']} already exists!",
            "login_url":url_for("auth.login")
        }), 409 #conflict in this case the email exist
    
    #Create the user
    new_user = User(
        name=data["name"],
        email=data["email"],
        password =generate_password_hash(data["password"], method="pbkdf2:sha256", salt_length=8),
        

    )

    #add the user to the database
    db.session.add(new_user)
    db.session.commit()

    #Flash a message to show a successful registration
    return jsonify({
        "message":"Thanks for registering. You can now login.",
        "login_url": url_for('auth.login')
    }), 201




#Gmail login
@auth_bp.route('/google_login', methods=['GET', 'POST'])
def google_login():
    if request.method == 'POST':
        email = request.form.get("email")
        print("Your email is", email)

        #check if user exist or create new user
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, name=email.split('@')[0])
            db.session.add(user)

            #Generate verification code
            verification_code = secrets.token_hex(3).upper()[:6]
            user.verification_code = verification_code
            user.code_expiry = datetime.utcnow() + timedelta(minutes=15)
            user.is_verified = False
            db.session.commit()

            #send verification code to user email
            send_verification_email(email, verification_code)

            #store email in session for verification
            session['verify_email'] = email
            return jsonify({'success': True, 'message': 'Verification code sent to your email.'})
    return render_template('login.html')
    
def send_verification_email(email, verification_code):
    msg = EmailMessage()
    msg['Subject'] = 'Your Verification Code'
    msg['From'] = os.getenv("MAIL_USERNAME")
    msg['To'] = email
    msg.set_content(f'Your verification code is {verification_code}\n\nThis code is valid for 15 minutes.')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(os.getenv("MAIL_USERNAME"), os.getenv("MAIL_PASSWORD"))
        smtp.send_message(msg)
    
#Verify login
@auth_bp.route('/verify_login', methods=['POST'])
def verify_login():

    data = request.get_json()
    code = data.get("code")
    email = session.get('verify_email')

    if not email:
        flash("Session expired. Please login again.", "error")
        return redirect(url_for('auth.google_login'))
    
    user = User.query.filter_by(email=email).first()
    if not user or user.verification_code != code:
        flash("Invalid verification code", "error")
        return redirect(url_for('auth.verify_login'))
    if user.code_expiry < datetime.utcnow():
        flash("Verification code expired. Please request a new one.", "error")
        return redirect(url_for('auth.google_login'))
    user.is_verified = True
    db.session.commit()
    session.pop('verify_email', None)  # Clear the session variable

    login_user(user)  # Log the user in after verification
    return jsonify({"success": True, "message": "Verification successful. Redirecting..."})
    # If the request method is GET, render the verification page
    # return render_template('verify_login.html')

@auth_bp.route('/verify_login_page', methods=['GET'])
def verify_login_page():
    # Only GET here — just shows the form
    return render_template('verify_login.html')


# @auth_bp.route('/login', methods=['POST'])
# def login():
#     #check if the user is already authenticated
#     # if current_user.is_authenticated:
#     #     return jsonify({"Message":"Already authenticated", "redirect" :url_for('home')}), 200
    
#     #get the data from the request incoming into the server
#     data = request.get_json()

#     email = data.get("email")
#     password = data.get("password")

#     user = User.query.filter_by(email=email).first()

#     #validate the required fileds

#     if not data or not data.get("email") or not data.get("password"):
#         return jsonify({"Message":"Email and Password are required"}), 400
    
    

#     #query the user from the database

    

#     if not user or not user.check_password(password):
#         return jsonify({
#             "message":f"Invalid email or password",
#             "register_url": url_for("register")
#         }),404

#     access_token = user.generate_access_token()
#     return jsonify({
#         "access_token": access_token,
#         "user": {
#             "id": user.id,
#             "email": user.email
#         }
#     }), 200
    
    #check password hash
    # if check_password_hash(user.password, password):
    #     login_user(user)
    #     return jsonify({
    #         "message":"Login successful",
    #         "redirect": url_for('home')
    #     }), 200
    # else:
    #     return jsonify({
    #         "message":"Email or password is incorrect"
    #     }), 401




@auth_bp.route('/logout')
# @login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# @auth_bp.route('/google')
# def google_login():
#     if not google.authorized:
#         return redirect(url_for('google.login'))
#     resp = google.get("/oauth2/v2/userinfo")
#     user_info = resp.json()
#     email = user_info["email"]
#     user = User.query.filter_by(email=email).first()
#     if not user:
#         user = User(email=email, name=user_info["name"])
#         db.session.add(user)
#         db.session.commit()

#     access_token = create_access_token(identity=user.id)
#     return jsonify({"access_token":access_token, "user": {"id": user.id, "email": user.email}}), 200
