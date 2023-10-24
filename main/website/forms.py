from . import models
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import Form, StringField, IntegerField, PasswordField, validators, RadioField, \
    SelectField, ValidationError, FileField, \
    SubmitField, TextAreaField, DateField, FloatField, MultipleFileField


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
    postal_code = IntegerField('Postal Code', [validators.NumberRange(min=0, max=999999)])
    town = StringField('Town', [validators.DataRequired()])
    # block = StringField('Block', [validators.DataRequired()]) # don't need block
    # building = StringField('Building', [validators.DataRequired()]) # don't need building
    # street_name = StringField('Street Name', [validators.DataRequired()]) # don't need streetname
    flat_type = SelectField('Flat Type', choices=[('2-Room', '2-Room'), ('3-Room', '3-Room'),
                                                  ('4-Room', '4-Room'), ('5-Room', '5-Room'),
                                                  ('Executive', 'Executive')])
    monthly_rent = IntegerField('Monthly Rent', [validators.NumberRange(min=0, max=10000)])
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
    image = MultipleFileField("Insert up to 5 photos of the property" ,[validators.DataRequired()])
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
    address = StringField('')
    distance_min = FloatField("Minimum Distance",[validators.DataRequired()])
    distance_max = FloatField("Maximum Distance",[validators.DataRequired()])
    monthly_rent_max = FloatField("Maximum Monthly Rent",[validators.DataRequired()])
    num_of_bedrooms_min = IntegerField("Minimum Number of bedrooms",[validators.DataRequired()])
    num_of_bedrooms_max = IntegerField("Maximum Number of bedrooms",[validators.DataRequired()])
    floor_size_min = FloatField("Minimum Floor size",[validators.DataRequired()])
    floor_size_max = FloatField("Maximum Floor size",[validators.DataRequired()])
    ppsm_min = FloatField("Minimum Price Per Square Meter",[validators.DataRequired()])
    ppsm_max = FloatField("Maximum Price Per Square Meter",[validators.DataRequired()])
    year_built_min = FloatField("Minimum Built Year",[validators.DataRequired()])
    year_built_max = FloatField("Maximum Built Year",[validators.DataRequired()])
    floor_level_min = FloatField("Minimum Floor Level",[validators.DataRequired()])
    floor_level_max = FloatField("Maximum Floor Level",[validators.DataRequired()])
    furnish_status = SelectField('Furnish Status', choices=['fully furnished', 'not furnished', 'partially furnished'], validate_choice=False)
    lease_term = SelectField('Lease Term', choices=['1 year','2 years', '3 years', 'short term', 'flexible'], validate_choice=False)
    negotiable = SelectField('Negotiable', choices=['yes','no'], validate_choice=False)
    flat_type = SelectField('Flat Type', choices = ['5-ROOM', '4-ROOM', '3-ROOM', 'EXECUTIVE', '2-ROOM'],validate_choice = False)

class EditProperty(FlaskForm):
    Prop_id = IntegerField("Property ID", [validators.DataRequired()])
    image = MultipleFileField("Upload new photos, all previous uploaded photos will be deleted")
