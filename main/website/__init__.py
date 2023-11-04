from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager, current_user
from .secret_key import refresh_one_map_token

db = SQLAlchemy()
DB_NAME = "mydb"

def create_app():
    app = Flask(__name__)

    # app configs
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    app.config['SECRET_KEY'] = 'secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://root:PRYtheSheep1!@localhost/{DB_NAME}"
    app.config['ONE_MAP_TOKEN'] = refresh_one_map_token()
    app.config["IMAGE_UPLOAD_FOLDER"] = APP_ROOT+'\\\\storage\\\\property_images'
    app.config["APPROVAL_DOCUMENT_UPLOAD_FOLDER"] = APP_ROOT+'\\\\storage\\\\approval_documents'

    # init db
    db.init_app(app)
    from . import models
    with app.app_context():
        db.create_all()

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