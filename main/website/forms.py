from . import models
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import Form, StringField, PasswordField, validators, RadioField, \
    SelectField, ValidationError, FileField, \
    SubmitField, TextAreaField

class RegistrationForm(FlaskForm):
    email = StringField('Email Address', [validators.Email(),
                                           validators.DataRequired()])
    password = PasswordField('Password', [
        validators.Length(min=12, max=18),
        validators.DataRequired(),
        validators.EqualTo('confirm_password', message='Passwords must match.'),
        validators.Regexp("^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{12,18}$"
                          , message="The password must be 12-18 characters, contain at least one letter, one number and one special character.")
    ])
    confirm_password = PasswordField('Confirm Password', [validators.DataRequired()])
    register_as = SelectField('Register Account As', choices=[('tenant', 'Tenant'), ('landlord', 'Landlord')])
    #recaptcha = RecaptchaField()

class LoginForm(FlaskForm):
    email = StringField('Email Address', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])


