from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path

db = SQLAlchemy()
DB_NAME = "ars"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://root:password@localhost/{DB_NAME}"
    db.init_app(app)

    from .routers.auth import auth
    from .routers.views import views

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    # app.config['RECAPTCHA_USE_SSL'] = False
    # app.config['RECAPTCHA_PUBLIC_KEY'] = '6Lf8rlooAAAAAFz3veH2jeohzUa1tcmKdF0-pMAE'
    # app.config['RECAPTCHA_PRIVATE_KEY'] = '6Lf8rlooAAAAABt5dyhmw3EzrRtRTq6J0qARS4Dl'
    # app.config['RECAPTCHA_OPTIONS'] = {'theme': 'white'}

    #from . import models

    with app.app_context():
        db.create_all()

    return app