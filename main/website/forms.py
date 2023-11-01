from datetime import datetime
from . import models
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import HiddenField, IntegerRangeField, StringField, IntegerField, PasswordField, SubmitField, validators, \
    SelectField, FileField, \
    DateField, FloatField, MultipleFileField,SelectMultipleField


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
    gender = SelectField('Gender', choices=[('mixed', 'mixed'), ('male', 'male'), ('female', 'female')])
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
    submit_target_location_form = SubmitField("Search")


class ManageApprovalForm(FlaskForm):
    property_id = IntegerField("Property ID", [validators.DataRequired()])
    selection = SelectField("Select an action to take", choices=[('Yes', "Yes"), ("No", "No"), ("View documents", "View documents")])

class FiltersForm(FlaskForm):
    target_location = HiddenField("Target Location")
    distance_min = FloatField("Distance (km)",default=0, validators=[validators.NumberRange(min=0)])
    distance_max = FloatField("Maximum Distance",default=5, validators=[validators.NumberRange(min=0)])
    monthly_rent_min = FloatField("Monthly Rent ($/per month)",default=0, validators=[validators.NumberRange(min=0)])
    monthly_rent_max = FloatField("Maximum Monthly Rent",default=10000, validators=[validators.NumberRange(min=0)])
    num_of_bedrooms_min = IntegerField("Number of bedrooms",default=1, validators=[validators.NumberRange(min=1)])
    num_of_bedrooms_max = IntegerField("Maximum Number of bedrooms",default=5, validators=[validators.NumberRange(min=1)])
    floor_size_min = FloatField("Floor size",default=0, validators=[validators.NumberRange(min=0)])
    floor_size_max = FloatField("Maximum Floor size",default=1000, validators=[validators.NumberRange(min=0)])
    ppsm_min = FloatField("Price Per Square Meter",default=0, validators=[validators.NumberRange(min=0)])
    ppsm_max = FloatField("Maximum Price Per Square Meter",default=200, validators=[validators.NumberRange(min=0)])
    year_built_min = DateField("Built Year",format='%Y-%d-%m',default=datetime(1970,1,1))
    year_built_max = DateField("Maximum Built Year",format='%Y-%d-%m',default=datetime(2030,1,1))
    floor_level_min = IntegerField("Floor Level",default=1, validators=[validators.NumberRange(min=1)])
    floor_level_max = IntegerField("Maximum Floor Level",default=20, validators=[validators.NumberRange(min=1)])
    approval_date_min = DateField("Approval Date",format='%Y-%d-%m',default=datetime(1970,1,1))
    approval_date_max = DateField("Maximum Approval Date",format='%Y-%d-%m',default=datetime(2030,1,1))
    furnish_status = SelectMultipleField('Furnish Status', choices=[
        ('fully furnished','Fully Furnished'), 
        ('not furnished','Not Furnished'), 
        ('partially furnished','Partially Furnished')], 
        default=['fully furnished','not furnished','partially furnished'])
    lease_term = SelectMultipleField('Lease Term', choices=[
        ('1 year','1 year'),
        ('2 years','2 years'), 
        ('3 years','3 years'), 
        ('short term','Short Term'), 
        ('flexible','Flexible')],
        default=['1 year','2 years','3 years','short term','flexible'])
    negotiable = SelectMultipleField('Negotiable', choices=[
        ('yes','Yes'),
        ('no','No')],
        default=['yes','no'])
    flat_type = SelectMultipleField('Flat Type', choices = [
        ('EXECUTIVE','EXECUTIVE'), 
        ('5-ROOM','5-ROOM'),
        ('4-ROOM','4-ROOM'), 
        ('3-ROOM','3-ROOM'), 
        ('2-ROOM','2-ROOM')],
        default=['EXECUTIVE','5-ROOM','4-ROOM','3-ROOM','2-ROOM'])
    gender = SelectMultipleField('Gender', choices=[
        ('female','Female'), 
        ('male','Male'),
        ('mixed','Mixed')],
        default=['female','male','mixed'])
    submit_filters_form = SubmitField("Apply Filters")


class SelectPropertyToEdit(FlaskForm):
    prop_id = IntegerField("Property ID", [validators.DataRequired()])


class EditProperty(FlaskForm):
    monthly_rent = IntegerField('Monthly Rent', [validators.NumberRange(min=0, max=10000)])
    num_bedrooms = IntegerField('Number of bedrooms', [validators.NumberRange(min=1, max=6)])
    gender = SelectField('Gender', choices=[('mixed', 'mixed'), ('male', 'male'), ('female', 'female')])
    furnishing = SelectField('Furnishing', choices=[('Not Furnished', 'Not Furnished'),
                                                    ('Partially Furnished', 'Partially Furnished'),
                                                    ('Fully Furnished', 'Fully Furnished')])
    rent_approval_date = DateField('List Date', format="%Y-%m-%d")
    lease_term = SelectField('Lease Term', choices=[('1 year', '1 year'), ('2 years', '2 years'),
                                                    ('3 years', '3 years'), ('Short Term', 'Short Term'),
                                                    ('Flexible', 'Flexible')])
    negotiable = SelectField('Negotiable Pricing', choices=[('No', 'No'), ('Yes', 'Yes')])
    image = MultipleFileField("Insert up to 5 photos of the property")
    approval_form = FileField("Insert approval document", [validators.DataRequired()])