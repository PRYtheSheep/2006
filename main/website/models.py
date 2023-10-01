from . import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))
    account_type = db.Column(db.String(150))
    properties_owned = db.relationship('Property')
    properties_favourited = db.relationship('PropertyFavourites')

    # override class used in flask_login
    def get_id(self):
        return (self.user_id)

class Property(db.Model):
    property_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))

class PropertyFavourites(db.Model):
    pf_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    property_id = db.Column(db.Integer, db.ForeignKey("property.property_id")) 

class AccountRecovery(db.Model):
    ar_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    recovery_string = db.Column(db.String(150), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    