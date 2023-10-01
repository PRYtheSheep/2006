from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, current_user

db = SQLAlchemy()
DB_NAME = "mydb"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://root:password@localhost/{DB_NAME}"
    db.init_app(app)

    from .routers.auth import auth
    from .routers.views import views

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from . import models

    with app.app_context():
        db.create_all()
        print(len(models.Property.query(leaseTerm=["1 year", "2 years", "3 years", "short term", "flexible"])))

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login_account'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(int(user_id))
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html", user=current_user)

    return app