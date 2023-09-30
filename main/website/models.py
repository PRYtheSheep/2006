from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    userId = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))
    properties_owned = db.relationship('Property')
    properties_favourited = db.relationship('PropertyFavourites')

    # override class used in flask_login
    def get_id(self):
        return (self.userId)

class Property(db.Model):
    propertyId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey("user.userId"))

class PropertyFavourites(db.Model):
    pfId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey("user.userId"))
    propertyId = db.Column(db.Integer, db.ForeignKey("property.propertyId")) 
