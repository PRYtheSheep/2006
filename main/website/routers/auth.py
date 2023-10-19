from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import check_password_hash
from .. import models, forms, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user, login_remembered

from .. import forms, email_sender, db, models
from ..models import User, AccountRecovery
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse

auth = Blueprint('auth',__name__)

@auth.route("/login", methods=["GET","POST"])
def login_account():
    form = forms.LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = models.User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for("properties_views.map_page"))
            else:
                flash('Incorrect email or password', category='error')
        else:
            flash('Incorrect email or password', category='error')
        
    return render_template("loginpage.html", user=current_user, form=form)

@auth.route("/logout")
@login_required
def logout_account():
    logout_user()
    return redirect(url_for("auth.login_account"))

@auth.route("/register", methods=["GET","POST"])
def register_account():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        user = models.User.query.filter_by(email=email).first()
        if user:
            flash("Email: Email is already taken",category='error')
        else:
            password = generate_password_hash(form.password.data) #123456789aA$ , 123456789aA$$
            username = email.split("@")[0]
            account_type = form.register_as.data

            new_user = models.User(email=email, 
                                   password=password, 
                                   username=username, 
                                   account_type=account_type)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash("Registered Successfully", category='success')
            return redirect(url_for('auth.login_account'))
    return render_template("register.html", user=current_user, form=form)

@auth.route('/forgetpassword', methods=['GET', 'POST'])
def forget_password_request():
    form = forms.ForgetPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()

        if user:
            user_id = user.user_id
            account_recovery = AccountRecovery.query.filter_by(user_id=user_id).first()

            if account_recovery and ((
                                             datetime.now() - account_recovery.created_at).seconds / 60 < 5):  # user requested a reset in the last 5 minutes
                flash("You have requested a password reset in the last 5 minutes. Please try again later.", 'error')
            else:
                u = str(uuid.uuid4())
                # u = 218b7a1c-fa21-4e7b-9cfd-2d05e939ac28 # for testing purposes
                email_content = f"Password reset link: {request.url_root}/forgetpassword/{u}"
                email_sender.send_email(email, "Password Reset Request", email_content)

                if not account_recovery:  # first time resetting password
                    new_ar = AccountRecovery(user_id=user_id,
                                             recovery_string=u)
                    db.session.add(new_ar)
                else:
                    account_recovery.recovery_string = u
                    account_recovery.created_at = datetime.now()

                db.session.commit()

                flash("A password reset link has been sent to your email", 'success')

            return redirect(url_for("auth.login_account"))
        else:
            flash("There are no accounts with this email", 'error')
            return redirect(url_for("auth.forget_password_request"))
    return render_template("forget_password.html", user=current_user, form=form)


@auth.route('/forgetpassword/<uuid:reset_id>', methods=["GET", "POST"])
def forget_password(reset_id):
    account_recovery = AccountRecovery.query.filter_by(recovery_string=str(reset_id)).first()
    if not account_recovery:
        flash("No such password request exist", 'error')
        return redirect(url_for("auth.forget_password_request"))
    elif ((datetime.now() - account_recovery.created_at).seconds / 60 < 15):  # link expired, more than 15 mins
        flash("Password reset link has expired", 'error')
        return redirect(url_for("auth.forget_password_request"))
    else:
        form = forms.ChangeForgetPasswordForm()
        if form.validate_on_submit():
            user_id = account_recovery.user_id
            user = User.query.filter_by(user_id=user_id).first()

            password = generate_password_hash(form.password.data)
            user.password = password

            db.session.delete(account_recovery)

            db.session.commit()
            flash("Password changed successfully")
            return redirect(url_for("auth.login_account"))
    return render_template("forget_password_change.html", user=current_user, form=form, reset_id=reset_id)

