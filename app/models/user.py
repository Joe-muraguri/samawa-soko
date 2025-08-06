from app.extensions import db
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
import datetime



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    verification_code = db.Column(db.String(6))
    code_expiry = db.Column(db.DateTime)
    is_verified = db.Column(db.Boolean, default=False)
    phone_number = db.Column(db.String(20))
    full_name = db.Column(db.String(100))
    address = db.Column(db.String(200))

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255), nullable=False, unique=True)
#     email = db.Column(db.String(255), nullable=False, unique=True)
#     password = db.Column(db.String(255), nullable=False, unique=True)
#     created_at = db.Column(db.DateTime, default = datetime.datetime.now())

#     def set_password(self, password):
#         self.password = generate_password_hash(password)
    
#     def check_password(self, password):
#         return check_password_hash(self.password, password)
    
#     def generate_access_token(self):
#         expires = datetime.timedelta(days=7)
#         return create_access_token(identity={"id":self.id},expires_delta=expires)
    
#     def __repr__(self):
#         return f'<User {self.email}>'