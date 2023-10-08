from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import check_password_hash
from .. import models, forms, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user, login_remembered

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
                return redirect(url_for("views.map_page"))
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
            flash("Email is already taken",category='error')
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