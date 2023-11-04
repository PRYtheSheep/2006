from datetime import datetime

from wtforms.widgets import TextArea

from . import models
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import HiddenField, IntegerRangeField, StringField, IntegerField, PasswordField, SubmitField, validators, \
    SelectField, FileField, \
    DateField, FloatField, MultipleFileField,SelectMultipleField


"""
Forms for registration/login/password reset
"""
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
    password = PasswordField('New Password', [
        validators.Length(min=12, max=18),
        validators.DataRequired(),
        validators.EqualTo('confirm_password', message='Passwords must match.'),
        validators.Regexp("^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{12,18}$"
                          ,
                          message="The password must be 12-18 characters, contain at least one letter, one number and one special character.")
    ])
    confirm_password = PasswordField('Confirm New Password', [validators.DataRequired()])


"""
Forms for account settings
"""
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


"""
Forms for property management
"""
class RegisterPropertyForm(FlaskForm):
    property_name = StringField('Property Name', widget=TextArea(), validators=[validators.data_required()])
    postal_code = IntegerField('Postal Code', [validators.NumberRange(min=0, max=999999)])
    town = StringField('Town', [validators.DataRequired()])
    # block = StringField('Block', [validators.DataRequired()]) # don't need block
    # building = StringField('Building', [validators.DataRequired()]) # don't need building
    # street_name = StringField('Street Name', [validators.DataRequired()]) # don't need street name
    flat_type = SelectField('Flat Type', choices=[('2-Room', '2-Room'), ('3-Room', '3-Room'),
                                                  ('4-Room', '4-Room'), ('5-Room', '5-Room'),
                                                  ('Executive', 'Executive')])
    monthly_rent = IntegerField('Monthly Rent', [validators.NumberRange(min=0, max=10000)])
    num_bedrooms = IntegerField('Number of bedrooms', [validators.NumberRange(min=1, max=6)])
    gender = SelectField('Gender', choices=[('mixed', 'mixed'), ('male', 'male'), ('female', 'female')])
    floor_size = IntegerField('Floor size in square metres', [validators.NumberRange(min=0, max=200)])
    year_built = DateField('Built Date', format="%Y-%m-%d", validators=[validators.DataRequired()])
    furnishing = SelectField('Furnishing', choices=[('Not Furnished', 'Not Furnished'),
                                                                ('Partially Furnished', 'Partially Furnished'),
                                                                ('Fully Furnished', 'Fully Furnished')])
    floor_level = IntegerField('Floor Level', [validators.NumberRange(min=1, max=99)])
    #rent_approval_date = DateField('List Date', format="%Y-%m-%d", validators=[validators.DataRequired()])
    lease_term = SelectField('Lease Term', choices=[('1 year', '1 year'), ('2 years', '2 years'),
                                                    ('3 years', '3 years'), ('Short Term', 'Short Term'),
                                                    ('Flexible', 'Flexible')])
    negotiable = SelectField('Negotiable Pricing', choices=[('No', 'No'), ('Yes', 'Yes')])
    property_description = StringField('Property Description', widget=TextArea(), validators=[validators.data_required()])
    image = MultipleFileField("Insert up to 5 photos of the property" ,[validators.DataRequired()])
    approval_form = FileField("Insert approval document", [validators.DataRequired()])


class ManageApprovalForm(FlaskForm):
    property_id = IntegerField("Property ID", [validators.DataRequired()])
    selection = SelectField("Select an action to take", choices=[('Yes', "Yes"), ("No", "No"), ("View documents", "View documents")])

class AdminPropertyViewForm(FlaskForm):
    user_id = StringField("User ID", render_kw={'disabled': True})
    full_name = StringField("Landlord Full Name", render_kw={'disabled': True})
    email = StringField("Email", render_kw={'disabled': True})
    property_id = StringField("Property ID", render_kw={'disabled': True})
    property_name = StringField("Property Name", render_kw={'disabled': True})
    property_description = StringField("Property Description", render_kw={'disabled': True})
    block = StringField("Block", render_kw={'disabled': True})
    street_name = StringField("Street Name", render_kw={'disabled': True})
    building = StringField("Building", render_kw={'disabled': True})
    postal_code = StringField("Postal Code", render_kw={'disabled': True})
    town = StringField("Town", render_kw={'disabled': True})
    flat_type = StringField("Flat Type", render_kw={'disabled': True})
    monthly_rent = StringField("Monthly Rent", render_kw={'disabled': True})
    num_bedrooms = StringField("Number of Bedrooms", render_kw={'disabled': True})
    floor_size = StringField("Floor Size", render_kw={'disabled': True})
    ppsm = StringField("Price Per Square Metre", render_kw={'disabled': True})
    year_built = StringField("Year Built", render_kw={'disabled': True})
    furnishing = StringField("Furnishing", render_kw={'disabled': True})
    floor_level = StringField("Floor Level", render_kw={'disabled': True})
    lease_term = StringField("Lease Term", render_kw={'disabled': True})
    negotiable = StringField("Negotiable", render_kw={'disabled': True})
    created_at = StringField("Created At", render_kw={'disabled': True})
    approve_field = SubmitField("Approve Property")
    reject_field = SubmitField("Reject Property")
    reject_reason = StringField("Reason For Rejection (if applicable)", widget=TextArea())

class EditProperty(FlaskForm):
    property_name = StringField('Property Name', widget=TextArea())
    monthly_rent = IntegerField('Monthly Rent', [validators.NumberRange(min=0, max=10000)])
    num_bedrooms = IntegerField('Number of bedrooms', [validators.NumberRange(min=1, max=6)])
    gender = SelectField('Gender', choices=[('mixed', 'mixed'), ('male', 'male'), ('female', 'female')])
    furnishing = SelectField('Furnishing', choices=[('not furnished', 'not furnished'),
                                                    ('partially furnished', 'partially furnished'),
                                                    ('fully furnished', 'fully furnished')])
    lease_term = SelectField('Lease Term', choices=[('1 year', '1 year'), ('2 years', '2 years'),
                                                    ('3 years', '3 years'), ('Short Term', 'Short Term'),
                                                    ('Flexible', 'Flexible')])
    negotiable = SelectField('Negotiable Pricing', choices=[('no', 'no'), ('yes', 'yes')])
    property_description = StringField('Property Description', widget=TextArea())
    image = MultipleFileField("Insert up to 5 photos of the property")
    approval_form = FileField("Insert approval document", [validators.DataRequired()])

"""
Forms for map view
"""

class TargetLocationForm(FlaskForm):
    target_location = StringField("Target Location", [validators.DataRequired()])
    submit_target_location_form = SubmitField("Search")

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