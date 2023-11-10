from flask import request
from sqlalchemy import text, select

from . import db, email_sender
from flask_login import UserMixin
from datetime import datetime
import math
import uuid
from werkzeug.security import generate_password_hash


class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    password = db.Column(db.String(150))
    username = db.Column(db.String(150))
    account_type = db.Column(db.String(150))
    properties_owned = db.relationship('Property', backref='user', lazy=True)
    properties_favourited = db.relationship('PropertyFavourites')
    notifications = db.relationship('Notifications')
    
    # override class used in flask_login
    def get_id(self):
        return (self.user_id)

    @staticmethod
    def register_account(user_obj: object):
        """registers a new user into the database
        
        Keyword arguments:
        user_obj -- the user object to be registered
        Return: void
        """
        
        db.session.add(user_obj)
        db.session.commit()


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
    year_built = db.Column(db.Date)
    floor_level = db.Column(db.Integer)
    furnishing = db.Column(db.String(19))
    lease_term = db.Column(db.String(10))
    negotiable_pricing = db.Column(db.String(3))
    is_approved = db.Column(db.Boolean, default=False)
    is_pending_deletion = db.Column(db.Boolean, default=False)
    property_name = db.Column(db.String(150))
    property_description = db.Column(db.String(150))
    created_at = db.Column(db.DateTime, default=datetime.now())
    gender = db.Column(db.String(6))
    approval_document_url = db.Column(db.String(150))
    property_images = db.relationship('PropertyImages')
    
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
    def query_and_filter_v2(
            input_latitude,
            input_longitude,
            min_distance = 0,
            max_distance = 5,
            min_rent = 0,
            max_rent = 10000,
            min_bedrooms = 1,
            max_bedrooms = 5,
            min_floor_size = 0,
            max_floor_size = 1000,
            min_ppsm = 0,
            max_ppsm = 200,
            min_year_built = datetime(1970,1,1),
            max_year_built = datetime(2030,1,1),
            min_floor_level = 1,
            max_floor_level = 20,
            furnish_status = ['fully furnished', 'partially furnished', 'not furnished'],
            lease_term = ['1 year','2 years','3 years','short term','flexible'],
            min_approval_date = datetime(1970,1,1),
            max_approval_date = datetime(2030,1,1),
            is_negotiable = ['no', 'yes'],
            flat_type = ['5-ROOM', '4-ROOM', '3-ROOM', '2-ROOM', 'EXECUTIVE'],
            gender = ['male','female','mixed'],
            is_approved = True
            ):

        """ returns a list of properties that satisfy the given criteria
        
        Keyword arguments:
        input_latitude -- target latitude
        input_longitude -- target longitude
        min_distance -- minimum distance from target location
        max_distance -- maximum distance from target location
        min_rent -- minimum monthly rent
        max_rent -- maximum monthly rent
        min_bedrooms -- minimum number of bedrooms
        max_bedrooms -- maximum number of bedrooms
        min_floor_size -- minimum floor size
        max_floor_size -- maximum floor size
        min_ppsm -- minimum price per square metre
        max_ppsm -- maximum price per square metre
        min_year_built -- minimum year built
        max_year_built -- maximum year built
        min_floor_level -- minimum floor level
        max_floor_level -- maximum floor level
        furnish_status -- list of furnish status
        lease_term -- list of lease term
        min_approval_date -- minimum approval date
        max_approval_date -- maximum approval date
        is_negotiable -- list of negotiable pricing
        flat_type -- list of flat type
        is_approved -- is the property approved

        Return: list of properties
        """
        
        stmt = select('*').select_from(Property)\
            .where(Property.monthly_rent >= min_rent, 
                    Property.monthly_rent <= max_rent,
                    Property.number_of_bedrooms >= min_bedrooms,
                    Property.number_of_bedrooms <= max_bedrooms,
                    Property.floorsize >= min_floor_size,
                    Property.floorsize <= max_floor_size,
                    Property.price_per_square_metre >= min_ppsm,
                    Property.price_per_square_metre <= max_ppsm,
                    Property.year_built >= min_year_built,
                    Property.year_built <= max_year_built,
                    Property.floor_level >= min_floor_level,
                    Property.floor_level <= max_floor_level,
                    Property.furnishing.in_(furnish_status),
                    Property.lease_term.in_(lease_term),
                    Property.rent_approval_date >= min_approval_date,
                    Property.rent_approval_date <= max_approval_date,
                    Property.negotiable_pricing.in_(is_negotiable),
                    Property.flat_type.in_(flat_type),
                    Property.gender.in_(gender),
                    Property.is_approved == is_approved)
        
        results = db.session.execute(stmt).mappings().all()
    
        result_list = [ dict(row) for row in results ]
        filtered_list = []
        
        for result in result_list:
            within_distance = Property.distance_from_property(input_latitude, input_longitude, min_distance, max_distance, result)
            if within_distance:
                first_image = PropertyImages.query.filter_by(property_id=result['property_id']).first()
                result['image_url'] = first_image.image_url
                result['latitude'] = float(result['latitude'])
                result['longitude'] = float(result['longitude'])
                result['price_per_square_metre'] = float(result['price_per_square_metre'])
                result['floorsize'] = float(result['floorsize'])
                result['rent_approval_date'] = result['rent_approval_date'].strftime("%Y-%m-%d")
                result['created_at'] = result['created_at'].strftime("%Y-%m-%d")
                result['year_built'] = result['year_built'].strftime("%Y-%m-%d")
                filtered_list.append(result)

        return filtered_list

    @staticmethod
    def approve_property(prop_id):
        statement = f"UPDATE property SET is_approved = TRUE WHERE property_id = {prop_id}"
        db.session.execute(text(statement))
        db.session.commit()

    @staticmethod
    def reject_property(prop_id):
        approval_document = Property.query.filter_by(property_id=prop_id).first().approval_document_url
        statement = f"DELETE FROM property WHERE property_id = {prop_id}"
        db.session.execute(text(statement))
        db.session.commit()
        return approval_document

    @staticmethod
    def update_property(property_id,
                        monthly_rent=None,
                        num_bedrooms=None,
                        gender=None,
                        furnishing=None,
                        rent_approval_date=None,
                        lease_term=None,
                        negotiable=None,
                        property_name=None,
                        property_description=None):
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

        if property_name is not None:
            prop.property_name = property_name

        if property_description is not None:
            prop.property_description = property_description

        # set is_approved to false and commit it into the database
        prop.is_approved = False
        db.session.commit()

    @staticmethod
    def distance_from_property(inputlatitude, inputlongitude, min_distance, max_distance, property):
        """returns true or false depending on whether the property is within the distance range
        
        Keyword arguments:
        inputlatitude -- target latitude
        inputlongitude -- target longitude
        min_distance -- minimum distance from target location
        max_distance -- maximum distance from target location
        property -- property object

        Return: boolean
        """
        
        latitude1, longitude1 = float(property['latitude']) * (math.pi / 180), float(property['longitude']) * (math.pi / 180)
        latitude2, longitude2 = inputlatitude * (math.pi / 180), inputlongitude * (math.pi / 180)
        distance = math.acos(
            math.sin(latitude1) * math.sin(latitude2) + 
            math.cos(latitude1) * math.cos(latitude2) * math.cos(longitude2 - longitude1)) * 6371
        
        if distance >= min_distance and distance <= max_distance:
            return True
        else:
            return False

    
class PropertyFavourites(db.Model):
    pf_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    property_id = db.Column(db.Integer, db.ForeignKey("property.property_id"))


class PropertyImages(db.Model):
    pi_id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey("property.property_id"))
    image_url = db.Column(db.String(50))

    @staticmethod
    def reject_property_images(prop_id):
        current_image = PropertyImages.query.filter_by(property_id=prop_id).all()
        image_list = []
        for image in current_image:
            image_list.append(image.image_url)

        statement = f"DELETE FROM property_images WHERE property_id = {prop_id}"
        db.session.execute(text(statement))
        db.session.commit()
        return image_list


class AccountRecovery(db.Model):
    ar_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    recovery_string = db.Column(db.String(150), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.now())

    @staticmethod
    def create_and_send_account_recovery(user_obj: User, request_url_root: str):
        """creates a new account recovery object and sends an email to the user
        
        Keyword arguments:
        user_obj -- user object to be sent the email
        request_url_root -- url root of the request
        Return: flash message to be displayed
        """
        account_recovery = AccountRecovery.query.filter_by(user_id=user_obj.user_id).first()

        if account_recovery and ((datetime.now() - account_recovery.created_at).seconds / 60 < 5):  # user requested a reset in the last 5 minutes
            return ("You have requested a password reset in the last 5 minutes. Please try again later.", 'error')
        else:
            u = str(uuid.uuid4())
            # u = 218b7a1c-fa21-4e7b-9cfd-2d05e939ac28 # for testing purposes

            if not account_recovery:  # first time resetting password
                new_ar = AccountRecovery(user_id=user_obj.user_id,
                                            recovery_string=u)
                db.session.add(new_ar)
            else:
                account_recovery.recovery_string = u
                account_recovery.created_at = datetime.now()

            db.session.commit()
            email_content = f"Password reset link: {request_url_root}/forgetpassword/{u}"
            email_sender.send_email(user_obj.email, "Password Reset Request", email_content)

            return ("A password reset link has been sent to your email", 'success')

    @staticmethod
    def check_valid_recovery_string(reset_id: str):
        """checks if the recovery string is valid
        
        Keyword arguments:
        recovery_string -- recovery string to be checked
        Return: false: flash message to be displayed
                true: account recovery object
        """
        account_recovery = AccountRecovery.query.filter_by(recovery_string=reset_id).first()

        if not account_recovery:
            return (False, "No such password request exist", 'error')
        elif ((datetime.now() - account_recovery.created_at).seconds / 60 > 15):  # link expired, more than 15 mins
            return (False, "Password reset link has expired", 'error')
        else:
            return (True, account_recovery)

class Notifications(db.Model):
    notif_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id"))
    title = db.Column(db.String(150))
    message = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.now())
    is_read = db.Column(db.Boolean, default=False)

    @staticmethod
    def new_notification(user_id: str, title: str, message: str):
        new_notif = Notifications(
            user_id=user_id,
            title=title,
            message=message,
        )
        db.session.add(new_notif)
        db.session.commit()