from flask import Flask, session, render_template, jsonify, request, flash, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from datetime import timedelta
from app.extensions import jwt, db, migrate,cors,mail
from app.models.user import User
import os
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required





def create_app():
    app = Flask(__name__,
                static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'),
        static_url_path='/static'
        )
    app.config.from_object(Config)   #loads the configurations from the Config.py

    # In your Flask app configuration
    app.config['SECRET_KEY'] = 'warutere'
    app.config['SESSION_TYPE'] = 'filesystem'  # Or 'redis' for production
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))

    login_manager.login_view = 'auth.google_login'  # still needed for HTML routes

# ✅ This prevents 302 redirect for APIs and gives JSON instead
    @login_manager.unauthorized_handler
    def unauthorized_callback():
        if request.is_json or request.path.startswith('/api/'):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        return redirect(url_for('auth.google_login'))

    @app.context_processor
    def inject_cart_count():
        cart = session.get('cart', {})
        total_quantity = sum(item['quantity'] for item in cart.values())
        return dict(cart_count=total_quantity)

    
    
    # app.secret_key = os.urandom(24)

    #initialize the extensions with the app
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    mail.init_app(app)

    #import and register blueprints
    from app.routes.auth_routes import auth_bp, google_bp
    from app.routes.admin import admin_bp
    from app.routes.product_routes import product_bp
    from app.routes.cart_routes import cart_bp
    from app.routes.checkout import checkout_bp
    from app.routes.order_routes import order_bp
    from app.routes.mpesa_payment import payment_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(google_bp, url_prefix='/api/login')
    app.register_blueprint(product_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(order_bp, url_prefix='/api/orders')
    app.register_blueprint(payment_bp, url_prefix='/api/payment')   

    
    return app


