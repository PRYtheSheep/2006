import os.path
import webbrowser

import flask
from flask import Blueprint, render_template, url_for, flash, redirect, request, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from .custom_decorators import admin_required, landlord_required
from .properties_views import property_image_url
from .. import forms, db, models
from ..models import User, Property, PropertyFavourites, PropertyImages
from datetime import datetime
import requests

views = Blueprint('views', __name__)

app = None


def set_app(app1):
    global app
    app = app1


@views.route("/")
def landing_page():
    return render_template("homepage.html", user=current_user)


@views.route("/admin")
@login_required
@admin_required
def admin_panel():
    return render_template("homepage.html", user=current_user)  # temp

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

        # do the same check for image(multiple images can be uploaded)
        for i, image in enumerate(form.image.data):
            if i > 5:
                flash("Max of 5 images are allowed", "error")
                return render_template("register_property.html", user=current_user, form=form)

            if not allowed_file(secure_filename(image.filename), IMAGES_ALLOWED_EXTENSIONS):  # check if file is png type
                flash("Invalid image file type, only .png files are allowed", "error")
                return render_template("register_property.html", user=current_user, form=form)

        postal_code = form.postal_code.data
        url = f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={postal_code}&returnGeom=Y&getAddrDetails=Y&pageNum=1"
        response = requests.request("GET", url)
        response = response.json()
        result_dict = response["results"][0]
        property_latitude = result_dict['LATITUDE']
        property_longitude = result_dict['LONGITUDE']
        property_streetname = result_dict['ROAD_NAME']
        property_building = result_dict['BUILDING'] if result_dict['BUILDING'] != 'NIL' else result_dict['BLK_NO']
        property_block = result_dict['BLK_NO']

        new_property = models.Property(user_id=current_user.user_id,
                                       rent_approval_date=form.rent_approval_date.data,
                                       town=form.town.data,
                                       block=property_block,
                                       street_name=property_streetname,
                                       flat_type=form.flat_type.data,
                                       monthly_rent=form.monthly_rent.data,
                                       postal=form.postal_code.data,
                                       latitude=property_latitude,
                                       longitude=property_longitude,
                                       building=property_building,
                                       number_of_bedrooms=form.num_bedrooms.data,
                                       floorsize=form.floor_size.data,
                                       price_per_square_metre=round(form.monthly_rent.data / form.floor_size.data, 6),
                                       year_built=form.year_built.data,
                                       floor_level=form.floor_level.data,
                                       furnishing=form.furnishing.data,
                                       lease_term=form.lease_term.data,
                                       negotiable_pricing=form.negotiable.data,
                                       is_approved=False,
                                       is_visible=True,
                                       property_name="no name for now",
                                       property_description="no description for now",
                                       created_at=form.rent_approval_date.data,
                                       gender=form.gender.data)
        db.session.add(new_property)
        db.session.commit()
        db.session.refresh(new_property)

        property_id = new_property.property_id

        reformatted_filename = f"{property_id}"

        # save the approval form to the respective folder
        app.config["UPLOAD_FOLDER"] = APPROVAL_FORM_FOLDER
        approval_form_file_path = os.path.join(app.config["UPLOAD_FOLDER"], reformatted_filename+".pdf")
        approval.save(approval_form_file_path)

        # save the image(s) to the respective folder and add it into the property_image database
        # image_url in the property_image database will store all images separated by a comma
        app.config["UPLOAD_FOLDER"] = IMAGE_FOLDER
        image_url = ""
        for i, image in enumerate(form.image.data):
            image_form_file_path = os.path.join(app.config["UPLOAD_FOLDER"], reformatted_filename+f"_{i}.png")
            image.save(image_form_file_path)
            image_url += reformatted_filename+f"_{i}.png" + ", "

        # remove the final comma added
        image_url = image_url[:len(image_url)-2]
        new_property_image = PropertyImages(property_id=property_id,
                                           image_url=image_url)
        db.session.add(new_property_image)
        db.session.commit()

    # tentative return page
    flash("Placeholder success message", "success")
    return render_template("register_property.html", user=current_user, form=form)


# requires @admin annotation but will add it later after hard coding in the admin account
@login_required
@views.route("/manage_approval_document", methods=["GET", "POST"])
def manage_approval_document():
    form = forms.ManageApprovalForm()

    unapproved_properties = Property.query.filter_by(is_approved=0).all()
    list_l = []
    for i in unapproved_properties:
        list_l.append(i.property_id)
    flash(f"Unapproved properties: {list_l}")

    if form.validate_on_submit():
        prop_id = form.property_id.data
        selection = form.selection.data

        if prop_id not in list_l:
            flash("Invalid property ID", "error")
            return render_template("manage_approval.html", user=current_user, form=form)

        if selection == "View documents":
            filename = f"{prop_id}.pdf"
            path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'storage',
                                'approval_documents')
            return send_from_directory(
                directory=path,
                path=filename,
                as_attachment=False)

        elif selection == "Yes":
            Property.approve_property(prop_id)
            flash("Property approved")

        else:
            # selection is "No"
            PropertyImages.reject_property_images(prop_id)
            Property.reject_property(prop_id)
            flash("Property rejected, deleted from database", "error")

    return render_template("manage_approval.html", user=current_user, form=form)

@views.route("/testing")
def testing():
    return property_image_url("8593_1.png")