import os.path
import webbrowser

from flask import Blueprint, render_template, url_for, flash, redirect, request, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from .custom_decorators import admin_required, landlord_required
from .. import forms, db, models
from ..models import User, Property, PropertyFavourites
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

        # do the same check for image
        image_filename = secure_filename(form.image.name)
        image = request.files[image_filename]

        if approval.filename == "":  # empty file name, no file selected
            flash("No image selected", "error")
            return render_template("register_property.html", user=current_user, form=form)

        if not allowed_file(image.filename, IMAGES_ALLOWED_EXTENSIONS):
            flash("Invalid image file type, only .png files are allowed", "error")
            return render_template("register_property.html", user=current_user, form=form)

        postal_code = form.postal_code.data
        url = f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={postal_code}&returnGeom=Y&getAddrDetails=N&pageNum=1"
        response = requests.request("GET", url)
        response = response.json()
        test_response = {'found': 2, 'totalNumPages': 1, 'pageNum': 1, 'results': [{'SEARCHVAL': '459 JURONG WEST '
                                                                                                 'STREET 41 SINGAPORE'
                                                                                                 ' 640459',
                                                                                    'X': '15490.380174702',
                                                                                    'Y': '36938.330370849',
                                                                                    'LATITUDE': '1.35032904500392',
                                                                                    'LONGITUDE': '103.720911817526'},
                                                                                   {'SEARCHVAL': 'MY FIRST SKOOL',
                                                                                    'X': '15490.3806892578',
                                                                                    'Y': '36938.3301892411',
                                                                                    'LATITUDE': '1.35032904336173',
                                                                                    'LONGITUDE': '103.72091182215'}]}
        result_list = response["results"]


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
        db.session.refresh(new_property)

        property_id = new_property.property_id

        reformatted_filename = f"{property_id}"

        # save the approval form to the respective folder
        app.config["UPLOAD_FOLDER"] = APPROVAL_FORM_FOLDER
        approval_form_file_path = os.path.join(app.config["UPLOAD_FOLDER"], reformatted_filename+".pdf")
        approval.save(approval_form_file_path)

        # save the image to the respective folder
        app.config["UPLOAD_FOLDER"] = IMAGE_FOLDER
        image_file_path = os.path.join(app.config["UPLOAD_FOLDER"], reformatted_filename+".png")
        image.save(image_file_path)

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

        if selection == "View documents":
            filename = f"{prop_id}.pdf"
            # use absolute path for now
            return send_from_directory(
                directory='C:/Users/user/PycharmProjects/2006/main/website/storage/approval_documents',
                path=filename,
                as_attachment=False)

    return render_template("manage_approval.html", user=current_user, form=form)
