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

auth = Blueprint('auth',__name__)

@auth.route("/login", methods=["GET","POST"])
def login_account():
    form = forms.LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for("properties_views.map_page"))
            else:
                flash('Incorrect email or password', category='error')
        else:
            flash('Incorrect email or password', category='error')
        
    return render_template("login_page.html", user=current_user, form=form)

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
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email: Email is already taken",category='error')
        else:
            password = generate_password_hash(form.password.data) #123456789aA$ , 123456789aA$$

            new_user = User(email=email, 
                                   password=password, 
                                   username=email.split("@")[0], 
                                   account_type=form.register_as.data,
                                   first_name=form.first_name.data,
                                   last_name=form.last_name.data)
            
            User.register_account(new_user)

            flash(f"Registered as a {str(form.register_as.data).title()} Successfully", category='success')
            return redirect(url_for('auth.login_account'))
        
    return render_template("register_account_page.html", user=current_user, form=form)

@auth.route('/forgetpassword', methods=['GET', 'POST'])
def forget_password_request():
    form = forms.ForgetPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()

        if user:
            flash_msg = AccountRecovery.create_and_send_account_recovery(user, request.url_root)

            flash(flash_msg[0], flash_msg[1])

            return redirect(url_for("auth.login_account"))
        else:
            flash("There are no accounts with this email", 'error')
            return redirect(url_for("auth.forget_password_request"))
        
    return render_template("forget_password_request_page.html", user=current_user, form=form)


@auth.route('/forgetpassword/<uuid:reset_id>', methods=["GET", "POST"])
def forget_password(reset_id):
    form = forms.ChangeForgetPasswordForm()

    valid_request = AccountRecovery.check_valid_recovery_string(str(reset_id))

    if not valid_request[0]:
        flash(valid_request[1], valid_request[2])
        return redirect(url_for("auth.forget_password_request"))
    else:
        if form.validate_on_submit():
            account_recovery = valid_request[1]
            user_id = account_recovery.user_id
            user = User.query.filter_by(user_id=user_id).first()

            password = generate_password_hash(form.password.data)
            user.password = password

            db.session.delete(account_recovery)

            db.session.commit()
            flash("Password changed successfully")
            return redirect(url_for("auth.login_account"))
    return render_template("forget_password_change_page.html", user=current_user, form=form, reset_id=reset_id)

@auth.route('/page404')
def page404():
    return render_template("404.html", user=current_user)