import os.path

from flask import Blueprint, render_template, url_for, flash, redirect, request, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from .custom_decorators import admin_required, landlord_required
from .. import forms, email_sender, db, models
from ..models import User, Property, PropertyFavourites, AccountRecovery
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse
import requests
import json

views = Blueprint('views', __name__)

app = None


def set_app(app1):
    global app
    app = app1


@views.route("/")
def landing_page():
    return render_template("homepage.html", user=current_user)


@views.route("/map", methods=['GET', 'POST'])
@login_required
def map_page():
    result_list, property_list = [], []
    form = forms.TargetLocationForm()
    dynamic_form = forms.DynamicForm()
    target = [1.369635, 103.803680]  # middle of sg coords
    if form.validate_on_submit():
        target_location = form.target_location.data
        url = "https://www.onemap.gov.sg/api/common/elastic/search?searchVal={}&returnGeom=N&getAddrDetails=Y&pageNum=1".format(
            target_location  # 639798
        )
        response = requests.request("GET", url)
        data = response.json()
        pages = data['totalNumPages']

        for item in data['results']:
            result_list.append((item['ADDRESS'], item['ADDRESS']))
        # print(result_list)

        for i in range(2, pages + 1):
            url = "https://www.onemap.gov.sg/api/common/elastic/search?searchVal={}&returnGeom=N&getAddrDetails=Y&pageNum={}".format(
                target_location,
                i
            )
            response = requests.request("GET", url)
            data = response.json()
            for item in data['results']:
                result_list.append((item['ADDRESS'], item['ADDRESS']))

        dynamic_form.address.choices = result_list

        return render_template("testpage_map.html", user=current_user, form=form, result_list=result_list,
                               dynamic_form=dynamic_form, property_list=property_list,
                               target=target)

    elif dynamic_form.validate_on_submit():
        target_location = dynamic_form.address.data
        url = "https://www.onemap.gov.sg/api/common/elastic/search?searchVal={}&returnGeom=Y&getAddrDetails=Y&pageNum=1".format(
            target_location
        )
        response = requests.request("GET", url)
        data = response.json()
        address_details = data['results'][0]
        # print(address_details)

        # query into db for properties
        property_list = Property.query(float(address_details['LATITUDE']), float(address_details['LONGITUDE']), [])
        # print(len(property_list))
        # print(property_list[0]['distance'])
        filtered = list(filter(lambda num: num['distance'] < 10,
                               property_list))  # right now its filtered to properties less than 10km from selected location
        # print(len(filtered))
        # print(filtered)
        return render_template("testpage_map.html", user=current_user, form=form, result_list=result_list,
                               dynamic_form=dynamic_form, property_list=filtered,
                               target=[float(address_details['LATITUDE']), float(address_details['LONGITUDE'])])

    return render_template("testpage_map.html", user=current_user, form=form, result_list=result_list,
                           dynamic_form=dynamic_form, property_list=property_list,
                           target=target)


@views.route("/map/<int:property_id>", methods=['GET', 'POST'])
@login_required
def map_page_info(property_id=None):
    return render_template("homepage.html", user=current_user, property_id=property_id)


@views.route("/admin")
@login_required
@admin_required
def admin_panel():
    return render_template("homepage.html", user=current_user)  # temp


@views.route('/forgetpassword', methods=['GET', 'POST'])
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
            return redirect(url_for("views.forget_password_request"))
    return render_template("forget_password.html", user=current_user, form=form)


@views.route('/forgetpassword/<uuid:reset_id>', methods=["GET", "POST"])
def forget_password(reset_id):
    account_recovery = AccountRecovery.query.filter_by(recovery_string=str(reset_id)).first()
    if not account_recovery:
        flash("No such password request exist", 'error')
        return redirect(url_for("views.forget_password_request"))
    elif ((datetime.now() - account_recovery.created_at).seconds / 60 < 15):  # link expired, more than 15 mins
        flash("Password reset link has expired", 'error')
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
@views.route('/settings/<string:setting_type>', methods=["GET", "POST"])
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

                    flash("Account Information Changed Successfully", 'success')
                    return redirect(url_for('views.account_settings'))
                else:
                    flash("Password entered is wrong", 'error')
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

                    flash("Your password is successfully updated.", 'success')
                    return redirect(url_for('views.account_settings'))
                else:
                    flash("Current Password is wrong", 'error')
                    return redirect(url_for('views.account_settings', setting_type='password'))
            return render_template("account_settings.html", user=current_user, setting_type=setting_type, form=form)
        else:
            return render_template("404.html", user=current_user)


APPROVAL_FORM_ALLOWED_EXTENSIONS = {"pdf"}
IMAGES_ALLOWED_EXTENSIONS = {"png"}


def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions


APPROVAL_FORM_FOLDER = 'website/storage/approval_documents'
IMAGE_FOLDER = 'website/storage/property_images'


@login_required
@landlord_required
@views.route("/registerproperty", methods=["GET", "POST"])
def register_property():
    form = forms.RegisterPropertyForm()

    if form.validate_on_submit():
        # check if the approval form is the correct type
        approval_form_filename = secure_filename(form.approval_form.name)  # get the file name from the form
        approval = request.files[approval_form_filename]  # get the filestorage object

        if approval.filename == "":  # empty file name, no file selected
            flash("No approval file selected", "error")
            return render_template("register_property.html", user=current_user, form=form)

        if not allowed_file(approval.filename, APPROVAL_FORM_ALLOWED_EXTENSIONS):  # check if file is pdf type
            flash("Invalid approval file type, only .pdf files are allowed", "error")
            return render_template("register_property.html", user=current_user, form=form)

        # do the same check for image
        image_filename = secure_filename(form.image.name)
        image = request.files[image_filename]

        if approval.filename == "":  # empty file name, no file selected
            flash("No image selected", "error")
            return render_template("register_property.html", user=current_user, form=form)

        if not allowed_file(image.filename, IMAGES_ALLOWED_EXTENSIONS):
            flash("Invalid image file type, only .png files are allowed", "error")
            return render_template("register_property.html", user=current_user, form=form)

        new_property = models.Property(rent_approval_date=form.rent_approval_date.data,
                                       town=form.town.data,
                                       block=form.block.data,
                                       street_name=form.street_name.data,
                                       flat_type=form.flat_type.data,
                                       monthly_rent=form.monthly_rent.data,
                                       postal=form.postal_code.data,
                                       latitude=0,  # placeholder value
                                       longitude=0,  # placeholder value
                                       building=form.building.data,
                                       number_of_bedrooms=form.num_bedrooms.data,
                                       floorsize=form.floor_size.data,
                                       price_per_square_metre=round(form.monthly_rent.data / form.floor_size.data, 6),
                                       year_built=form.year_built.data,
                                       floor_level=form.floor_level.data,
                                       furnishing=form.furnishing.data,
                                       lease_term=form.lease_term.data,
                                       negotiable_pricing=form.negotiable.data,
                                       user_id=current_user.user_id,
                                       is_approved=False,
                                       is_visible=True)
        db.session.add(new_property)
        db.session.commit()

        # save the approval form to the respective folder
        app.config["UPLOAD_FOLDER"] = APPROVAL_FORM_FOLDER
        approval_form_file_path = os.path.join(app.config["UPLOAD_FOLDER"], approval.filename)
        approval.save(approval_form_file_path)

        # save the image to the respective folder
        app.config["UPLOAD_FOLDER"] = IMAGE_FOLDER
        image_file_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
        image.save(image_file_path)

    # tentative return page
    flash("Placeholder success message", "success")
    return render_template("register_property.html", user=current_user, form=form)


@login_required
@views.route("/viewapproval")
def view_approval_document():
    # use the absolute path for now
    return send_from_directory(directory='C:/Users/Dreamcore/PycharmProjects/2006/main/website/storage/property_images',
                               path='image.png',
                               as_attachment=False)
