from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import insert as upsert
import os
from flask_login import LoginManager, current_user
from .secret_key import refresh_one_map_token
from werkzeug.security import generate_password_hash

db = SQLAlchemy()
DB_NAME = "mydb"

def create_app():
    app = Flask(__name__)

    # app configs
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    app.config['SECRET_KEY'] = 'secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://root:96173880@localhost/{DB_NAME}"
    app.config['ONE_MAP_TOKEN'] = refresh_one_map_token()
    app.config["IMAGE_UPLOAD_FOLDER"] = APP_ROOT+'\\\\storage\\\\property_images'
    app.config["APPROVAL_DOCUMENT_UPLOAD_FOLDER"] = APP_ROOT+'\\\\storage\\\\approval_documents'

    # init db
    db.init_app(app)
    from . import models
    with app.app_context():
        db.create_all()
        # update and insert default users, see function below
        upsert_users(1, "johndoe@landlord.com", "johndoe", "landlord", "John", "Doe") 
        upsert_users(2, "admin@admin.com", "admin", "admin", "Admin", "User") 
        upsert_users(3, "jackdoe@tenant.com", "jackdoe", "tenant", "Jack", "Doe")

    # init login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login_account'
    login_manager.init_app(app)
    login_manager.login_message = 'Please login to access this page.'

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html", user=current_user)

    return app

def register(app):
    from .routers.auth import auth
    from .routers.views import views
    from .routers.account_views import account_views
    from .routers.properties_views import properties_views
    from .routers.admin_views import admin

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(account_views, url_prefix="/")
    app.register_blueprint(properties_views, url_prefix="/")
    app.register_blueprint(admin, url_prefix="/admin")

    return app

def upsert_users(user_id, email, username, account_type, first_name, last_name):
    from .models import User
    upsert_stmt = upsert(User).values(
        user_id=user_id,
        email=email,
        password=generate_password_hash("123456789aA$"),
        username=username,
        account_type=account_type,
        first_name=first_name,
        last_name=last_name
    )

    on_duplicate_stmt = upsert_stmt.on_duplicate_key_update(
        email=upsert_stmt.inserted.email,
        password=upsert_stmt.inserted.password,
        username=upsert_stmt.inserted.username,
        account_type=upsert_stmt.inserted.account_type,
        first_name=upsert_stmt.inserted.first_name,
        last_name=upsert_stmt.inserted.last_name
    )

    db.session.execute(on_duplicate_stmt)
    db.session.commit()

    