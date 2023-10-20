from . import models
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import Form, StringField, IntegerField, PasswordField, validators, RadioField, \
    SelectField, ValidationError, FileField, \
    SubmitField, TextAreaField, DateField,FloatField


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', [validators.DataRequired()])
    last_name = StringField('Last Name', [validators.DataRequired()])
    email = StringField('Email Address', [validators.Email(),
                                          validators.DataRequired()])
    password = PasswordField('Password', [
        validators.Length(min=12, max=18),
        validators.DataRequired(),
        validators.EqualTo('confirm_password', message='Passwords must match.'),
        validators.Regexp("^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{12,18}$"
                          ,
                          message="The password must be 12-18 characters, contain at least one letter, one number and one special character.")
    ])
    confirm_password = PasswordField('Confirm Password', [validators.DataRequired()])
    register_as = SelectField('Register As', choices=[('tenant', 'Tenant'), ('landlord', 'Landlord')])
    # recaptcha = RecaptchaField()


class LoginForm(FlaskForm):
    email = StringField('Email Address', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])


class ForgetPasswordForm(FlaskForm):
    email = StringField('Enter your email address', [validators.DataRequired()])


class ChangeForgetPasswordForm(FlaskForm):
    password = PasswordField('Password', [
        validators.Length(min=12, max=18),
        validators.DataRequired(),
        validators.EqualTo('confirm_password', message='Passwords must match.'),
        validators.Regexp("^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{12,18}$"
                          ,
                          message="The password must be 12-18 characters, contain at least one letter, one number and one special character.")
    ])
    confirm_password = PasswordField('Confirm Password', [validators.DataRequired()])


class RegisterPropertyForm(FlaskForm):
    town = StringField('Town', [validators.DataRequired()])
    block = StringField('Block', [validators.DataRequired()])
    building = StringField('Building', [validators.DataRequired()])
    street_name = StringField('Street Name', [validators.DataRequired()])
    flat_type = SelectField('Flat Type', choices=[('2-Room', '2-Room'), ('3-Room', '3-Room'),
                                                  ('4-Room', '4-Room'), ('5-Room', '5-Room'),
                                                  ('Executive', 'Executive')])
    monthly_rent = IntegerField('Monthly Rent', [validators.NumberRange(min=0, max=10000)])
    postal_code = IntegerField('Postal Code', [validators.NumberRange(min=0, max=999999)])
    num_bedrooms = IntegerField('Number of bedrooms', [validators.NumberRange(min=1, max=6)])
    floor_size = IntegerField('Floor size in square metres', [validators.NumberRange(min=0, max=200)])
    year_built = IntegerField('Year Built', [validators.NumberRange(min=1950, max=2023)])
    furnishing = SelectField('Furnishing', choices=[('Not Furnished', 'Not Furnished'),
                                                                ('Partially Furnished', 'Partially Furnished'),
                                                                ('Fully Furnished', 'Fully Furnished')])
    floor_level = IntegerField('Floor Level', [validators.NumberRange(min=1, max=99)])
    rent_approval_date = DateField('List Date', format="%Y-%m-%d", validators=[validators.DataRequired()])
    lease_term = SelectField('Lease Term', choices=[('1 year', '1 year'), ('2 years', '2 years'),
                                                    ('3 years', '3 years'), ('Short Term', 'Short Term'),
                                                    ('Flexible', 'Flexible')])
    negotiable = SelectField('Negotiable Pricing', choices=[('No', 'No'), ('Yes', 'Yes')])
    image = FileField("Insert a photo of the property" ,[validators.DataRequired()])
    approval_form = FileField("Insert approval document", [validators.DataRequired()])


class AccountSettingsForm(FlaskForm):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', [validators.DataRequired()])
    new_password = PasswordField('New Password', [
    validators.Length(min=12, max=18),
    validators.DataRequired(),
    validators.EqualTo('confirm_new_password', message='Passwords must match.'),
    validators.Regexp("^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{12,18}$"
                        ,
                        message="The password must be 12-18 characters, contain at least one letter, one number and one special character.")
    ])
    confirm_new_password = PasswordField('Confirm New Password', [validators.DataRequired()])

class TargetLocationForm(FlaskForm):
    target_location = StringField("Target Location", [validators.DataRequired()])


class ManageApprovalForm(FlaskForm):
    property_id = IntegerField("Property ID", [validators.DataRequired()])
    selection = SelectField("Select an action to take", choices=[('Yes', "Yes"), ("No", "No"), ("View documents", "View documents")])

class DynamicForm(FlaskForm):
    address = SelectField('', choices=[], validate_choice=False)
    

class FiltersForm(FlaskForm):
    address = SelectField('', choices=[], validate_choice=False)
    monthly_rent = FloatField("Monthly rent max",[validators.DataRequired()])
    distance = FloatField("Distance",[validators.DataRequired()])
    num_of_bedrooms = IntegerField("Number of bedrooms",[validators.DataRequired()])
    floor_size = FloatField("Floor size",[validators.DataRequired()])
