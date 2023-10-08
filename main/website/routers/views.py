from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_required, current_user
from .custom_decorators import admin_required, landlord_required
from .. import forms, email_sender, db
from ..models import User, Property, PropertyFavourites, AccountRecovery
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash,  check_password_hash
from urllib.parse import urlparse 
import requests
import json

views = Blueprint('views',__name__)

@views.route("/")
def landing_page():
    return render_template("homepage.html", user=current_user)

@views.route("/map", methods=['GET','POST'])
@login_required
def map_page():
    result_list, property_list = [], []
    form = forms.TargetLocationForm()
    dynamic_form = forms.DynamicForm()
    if form.validate_on_submit():
        target_location = form.target_location.data
        url = "https://www.onemap.gov.sg/api/common/elastic/search?searchVal={}&returnGeom=N&getAddrDetails=Y&pageNum=1".format(
            target_location #639798 
        )
        response = requests.request("GET", url)
        data = response.json()
        pages = data['totalNumPages']

        for item in data['results']:
            result_list.append((item['ADDRESS'],item['ADDRESS']))
        #print(result_list)

        for i in range(2,pages+1):
            url = "https://www.onemap.gov.sg/api/common/elastic/search?searchVal={}&returnGeom=N&getAddrDetails=Y&pageNum={}".format(
                target_location,
                i
            )
            response = requests.request("GET", url)
            data = response.json()
            for item in data['results']:
                result_list.append((item['ADDRESS'],item['ADDRESS']))

        dynamic_form.address.choices = result_list
        
        return render_template("testpage_map.html", user=current_user, form=form, result_list=result_list, dynamic_form=dynamic_form)
    
    elif dynamic_form.validate_on_submit():
        target_location = dynamic_form.address.data
        url = "https://www.onemap.gov.sg/api/common/elastic/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1".format(
            target_location
        )
        response = requests.request("GET", url)
        data = response.json()
        address_details = data['results'][0]
        #print(address_details)

        # query into db for properties
        property_list = Property.query(float(address_details['LATITUDE']), float(address_details['LONGITUDE']), []) 
        print(len(property_list))
        #print(property_list[0]['distance'])
        filtered = json.dumps(list(filter(lambda num: num['distance']<10, property_list)),indent=2,default=str)
        print(len(filtered))
        return render_template("testpage_map.html", user=current_user, form=form, result_list=result_list, dynamic_form=dynamic_form, property_list=filtered, target = [float(address_details['LATITUDE']), float(address_details['LONGITUDE'])])
    
    return render_template("testpage_map.html", user=current_user, form=form, result_list=result_list, dynamic_form=dynamic_form)

    
    
@views.route("/map/<int:property_id>", methods=['GET','POST'])
@login_required
def map_page_info(property_id=None):
    return render_template("homepage.html", user=current_user, property_id=property_id)



@views.route("/admin")
@login_required
@admin_required
def admin_panel():
    return render_template("homepage.html", user=current_user) # temp

@views.route('/forgetpassword', methods=['GET','POST'])
def forget_password_request():
    form = forms.ForgetPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()

        if user:
            user_id = user.user_id
            account_recovery = AccountRecovery.query.filter_by(user_id=user_id).first()

            if account_recovery and ((datetime.now()-account_recovery.created_at).seconds/60<5): # user requested a reset in the last 5 minutes
                flash("You have requested a password reset in the last 5 minutes. Please try again later.",'error')
            else:
                u = str(uuid.uuid4())
                #u = 218b7a1c-fa21-4e7b-9cfd-2d05e939ac28 # for testing purposes
                email_content = f"Password reset link: {request.url_root}/forgetpassword/{u}"
                email_sender.send_email(email, "Password Reset Request", email_content)

                if not account_recovery: # first time resetting password
                    new_ar = AccountRecovery(user_id=user_id,
                                             recovery_string=u)
                    db.session.add(new_ar)
                else:
                    account_recovery.recovery_string = u
                    account_recovery.created_at = datetime.now()
                    
                db.session.commit()

                flash("A password reset link has been sent to your email",'success')
            
            return redirect(url_for("auth.login_account"))
        else:
            flash("There are no accounts with this email",'error')
            return redirect(url_for("views.forget_password_request"))
    return render_template("forget_password.html", user=current_user, form=form)

@views.route('/forgetpassword/<uuid:reset_id>', methods=["GET","POST"])
def forget_password(reset_id):
    account_recovery = AccountRecovery.query.filter_by(recovery_string=str(reset_id)).first()
    if not account_recovery:
        flash("No such password request exist",'error')
        return redirect(url_for("views.forget_password_request"))
    elif ((datetime.now()-account_recovery.created_at).seconds/60<15): # link expired, more than 15 mins
            flash("Password reset link has expired",'error')
            return redirect(url_for("views.forget_password_request"))
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

@views.route('/settings')
@views.route('/settings/<string:setting_type>', methods=["GET","POST"])
@login_required
def account_settings(setting_type=None):
    if not setting_type:
        return render_template("account_settings.html", user=current_user, setting_type=setting_type)
    else:
        if setting_type == 'account':
            form = forms.AccountSettingsForm()
            if form.validate_on_submit():
                if check_password_hash(current_user.password, form.password.data):
                    user = User.query.filter_by(user_id=current_user.user_id).first()
                    user.username = form.username.data

                    db.session.commit()
                    current_user.username = form.username.data     
                                  
                    flash("Account Information Changed Successfully",'success')
                    return redirect(url_for('views.account_settings'))
                else:
                    flash("Password entered is wrong",'error')
                    return redirect(url_for('views.account_settings', setting_type='account'))
            return render_template("account_settings.html", user=current_user, setting_type=setting_type, form=form) 
        elif setting_type == 'password':
            form = forms.ChangePasswordForm()
            if form.validate_on_submit():
                if check_password_hash(current_user.password, form.current_password.data):
                    user = User.query.filter_by(user_id=current_user.user_id).first()
                    new_password = generate_password_hash(form.new_password.data)
                    user.password = new_password

                    db.session.commit()
                    current_user.password = new_password

                    flash("Your password is successfully updated.",'success')
                    return redirect(url_for('views.account_settings'))
                else:
                    flash("Current Password is wrong",'error')
                    return redirect(url_for('views.account_settings', setting_type='password'))
            return render_template("account_settings.html", user=current_user, setting_type=setting_type, form=form)
        else:
            return render_template("404.html", user=current_user)
        