from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import check_password_hash
from .. import models
from .. import forms
from .. import db
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth',__name__)

@auth.route("/login", methods=["GET","POST"])
def loginWebsite():
    form = forms.LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = models.User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash("Logged in successfully", category='success')
                # 
            else:
                flash('Incorrect email or password', category='error')
        else:
            flash('Incorrect email or password', category='error')
        
    return render_template("loginpage.html")

@auth.route("/logout", methods=["POST"])
def logoutAccount():
    return "<p>logout</p>"

@auth.route("/register", methods=["GET","POST"])
def registration():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        user = models.User.query.filter_by(email=email).first()
        if user:
            flash("Email is already taken",category='error')
        else:
            password = generate_password_hash(form.password.data)
            new_user = models.User(email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('auth.loginWebsite'))
    return render_template("register.html", form=form)

