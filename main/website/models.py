from sqlalchemy import text

from . import db
from flask_login import UserMixin
from datetime import datetime
import math


class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))
    account_type = db.Column(db.String(150))
    properties_owned = db.relationship('Property')
    properties_favourited = db.relationship('PropertyFavourites')

    # override class used in flask_login
    def get_id(self):
        return (self.user_id)


class Property(db.Model):
    property_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    rent_approval_date = db.Column(db.DateTime)
    block = db.Column(db.String(6))
    street_name = db.Column(db.String(30))
    building = db.Column(db.String(30))
    postal = db.Column(db.Integer)
    town = db.Column(db.String(15))
    flat_type = db.Column(db.String(9))
    monthly_rent = db.Column(db.Integer)
    latitude = db.Column(db.Numeric(10, 6))
    longitude = db.Column(db.Numeric(10, 6))
    number_of_bedrooms = db.Column(db.Integer)
    floorsize = db.Column(db.Numeric(7, 2))
    price_per_square_metre = db.Column(db.Numeric(7, 2))
    year_built = db.Column(db.Integer)
    floor_level = db.Column(db.Integer)
    furnishing = db.Column(db.String(19))
    lease_term = db.Column(db.String(10))
    negotiable_pricing = db.Column(db.String(3))
    is_visible = db.Column(db.Boolean)
    is_approved = db.Column(db.Boolean)
    property_name = db.Column(db.String(150))  # new
    property_description = db.Column(db.String(150))  # new
    created_at = db.Column(db.DateTime) # new
    property_images = db.relationship('PropertyImages')
    gender = db.Column(db.String(6))

    @staticmethod
    def query_(
            inputlatitude,
            inputlongitude,
            leaseTerm: list,
            rentLowerBound=0,
            rentUpperBound=10000,
            pricePSMLowerBound=0,
            pricePSMUpperBound=200,
            numBedLowerBound=1,
            numBedUpperBound=5,
            yearLowerBound=1970,
            yearUpperBound=2030,
            floorLevelLowerBound=1,
            floorLevelUpperBound=20,
            listDate="2019-01-01",
            negotiable="no"):
        """""""""
        Queries the database by rent
        Returns a list of dictionaries corresponding to each property that falls with the given ranges
        """""""""
        column_names = Property.__table__.columns.keys()

        rentStatement = f"monthly_rent >= {rentLowerBound} AND monthly_rent <= {rentUpperBound} "
        pricePSMStatement = f"price_per_square_metre >= {pricePSMLowerBound} AND price_per_square_metre <= {pricePSMUpperBound} "
        numBedStatement = f"number_of_bedrooms >= {numBedLowerBound} AND number_of_bedrooms <= {numBedUpperBound} "
        yearStatement = f"year_built >= {yearLowerBound} AND year_built <= {yearUpperBound} "
        floorStatement = f"floor_level >= {floorLevelLowerBound} AND floor_level <= {floorLevelUpperBound} "
        is_approvedStatement = "is_approved = true"

        leaseStatement = []
        for lease in leaseTerm:
            lstatement = f"lease_term = '{lease}' "
            leaseStatement.append(lstatement)

        dateStatement = f"rent_approval_date > '{listDate}' "
        negotiableStatement = f"negotiable_pricing = '{negotiable}' "

        statement = f"SELECT * from property WHERE " + rentStatement + "AND " + pricePSMStatement + "AND " + numBedStatement + "AND " + yearStatement + "AND " + floorStatement + "AND " + dateStatement + "AND " + negotiableStatement + "AND " + is_approvedStatement + " AND "
        for lstatement in leaseStatement:
            statement = statement + lstatement + "OR "
        statement = statement[:len(statement) - 4]

        query = db.session.execute(text(statement)).fetchall()

        returnlist = []
        for row in query:
            dic = {}
            latitude1, longitude1 = 0, 0

            for i, name in enumerate(column_names):

                if name == "is_approved" and row[i] == 0:
                    continue  # property not yet approved, skip it

                dic.update({
                    name: row[i]
                })
                if name == "latitude":
                    latitude1 = float(row[i]) * (math.pi / 180)
                if name == "longitude":
                    longitude1 = float(row[i]) * (math.pi / 180)

            latitude2, longitude2 = inputlatitude * (math.pi / 180), inputlongitude * (math.pi / 180)
            distance = math.acos(
                math.sin(latitude1) * math.sin(latitude2) + math.cos(latitude1) * math.cos(latitude2) * math.cos(
                    longitude2 - longitude1)) * 6371
            dic.update({
                "distance": distance
            })

            returnlist.append(dic)
        return returnlist

    @staticmethod
    def approve_property(prop_id):
        statement = f"UPDATE property SET is_approved = TRUE WHERE property_id = {prop_id}"
        db.session.execute(text(statement))
        db.session.commit()

    @staticmethod
    def reject_property(prop_id):
        statement = f"DELETE FROM property WHERE property_id = {prop_id}"
        db.session.execute(text(statement))
        db.session.commit()

    @staticmethod
    def update_property(property_id,
                        monthly_rent=None,
                        num_bedrooms=None,
                        gender=None,
                        furnishing=None,
                        rent_approval_date=None,
                        lease_term=None,
                        negotiable=None):
        prop = Property.query.filter_by(property_id=property_id).first()

        # update the property data if data is provided in the argument
        if monthly_rent is not None:
            prop.monthly_rent = monthly_rent
            prop.price_per_square_metre = monthly_rent / prop.floorsize

        if num_bedrooms is not None:
            prop.number_of_bedrooms = num_bedrooms

        if gender is not None:
            prop.gender = gender

        if furnishing is not None:
            prop.furnishing = furnishing

        if rent_approval_date is not None:
            prop.rent_approval_date = rent_approval_date

        if lease_term is not None:
            prop.lease_term = lease_term

        if negotiable is not None:
            prop.negotiable_pricing = negotiable

        # set is_approved to false and commit it into the database
        prop.is_approved = False
        db.session.commit()

class PropertyFavourites(db.Model):
    pf_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    property_id = db.Column(db.Integer, db.ForeignKey("property.property_id"))

class PropertyImages(db.Model):
    pi_id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey("property.property_id"))
    image_url = db.Column(db.String(250))

    @staticmethod
    def reject_property_images(prop_id):
        statement = f"DELETE FROM property_images WHERE property_id = {prop_id}"
        db.session.execute(text(statement))
        db.session.commit()


class AccountRecovery(db.Model):
    ar_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    recovery_string = db.Column(db.String(150), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
