from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    userId = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))
    properties = db.relationship('Property')

class Property(db.Model):
    propertyId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey("user.userId"))