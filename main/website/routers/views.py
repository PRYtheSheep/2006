import os.path

from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from .custom_decorators import landlord_required
from .. import forms, db, models
from ..models import Property, PropertyImages
from datetime import datetime
import requests

views = Blueprint('views', __name__)

@views.route("/")
def landing_page():
    latest_properties = Property.query.filter_by(is_approved=1).order_by(Property.created_at.desc()).limit(3).all()

    return render_template("landing_page.html", user=current_user, latest_properties=latest_properties, datetime_now = datetime.now())


APPROVAL_FORM_ALLOWED_EXTENSIONS = {"pdf"}
IMAGES_ALLOWED_EXTENSIONS = {"png"}


def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

@views.route("/manage_property/approved")
@login_required
@landlord_required
def manage_property_approved():
    # get all properties owned by user
    property_list = db.paginate(db.select(Property).where(Property.user_id == current_user.user_id, Property.is_approved==True).order_by(Property.created_at.desc()), per_page=10)
    if request.args.get('page'):
        property_list = db.paginate(db.select(Property).where(Property.user_id == current_user.user_id, Property.is_approved==True).order_by(Property.created_at.desc()), per_page=10, page=int(request.args.get('page')))

    return render_template("manage_property_page.html", user=current_user, property_list=property_list, approved=True)

@views.route("/manage_property/unapproved")
@login_required
@landlord_required
def manage_property_unapproved():
    # get all properties owned by user
    property_list = db.paginate(db.select(Property).where(Property.user_id == current_user.user_id, Property.is_approved==False).order_by(Property.created_at.desc()), per_page=10)
    if request.args.get('page'):
        property_list = db.paginate(db.select(Property).where(Property.user_id == current_user.user_id, Property.is_approved==False).order_by(Property.created_at.desc()), per_page=10, page=int(request.args.get('page')))

    return render_template("manage_property_page.html", user=current_user, property_list=property_list, approved=False)


@views.route("/manage_property/registerproperty", methods=["GET", "POST"])
@login_required
@landlord_required
def register_property():
    form = forms.RegisterPropertyForm()

    if form.validate_on_submit():
        # check if the approval form is the correct type
        approval_form_filename = secure_filename(form.approval_form.name)  # get the file name from the form
        approval = request.files[approval_form_filename]  # get the filestorage object

        if approval.filename == "":  # empty file name, no file selected
            flash("No approval file selected", "error")
            return redirect(url_for('views.register_property'))

        if not allowed_file(approval.filename, APPROVAL_FORM_ALLOWED_EXTENSIONS):  # check if file is pdf type
            flash("Invalid approval file type, only .pdf files are allowed", "error")
            return redirect(url_for('views.register_property'))

        # do the same check for image(multiple images can be uploaded)
        for i, image in enumerate(form.image.data):
            if i > 5:
                flash("Max of 5 images are allowed", "error")
                return redirect(url_for('views.register_property'))

            if not allowed_file(secure_filename(image.filename),
                                IMAGES_ALLOWED_EXTENSIONS):  # check if file is png type
                flash("Invalid image file type, only .png files are allowed", "error")
                return redirect(url_for('views.register_property'))

        postal_code = form.postal_code.data
        url = f"https://www.onemap.gov.sg/api/common/elastic/search?searchVal={postal_code}&returnGeom=Y&getAddrDetails=Y&pageNum=1"
        response = requests.request("GET", url)
        response = response.json()
        result_dict = response["results"][0]
        property_latitude = result_dict['LATITUDE']
        property_longitude = result_dict['LONGITUDE']
        property_streetname = result_dict['ROAD_NAME']
        property_building = result_dict['BUILDING'] #if result_dict['BUILDING'] != 'NIL' else result_dict['BLK_NO'] # some properties are using NIL as building name in the csv file, keep it as it is
        property_block = result_dict['BLK_NO']

        new_property = models.Property(user_id=current_user.user_id,
                                       #rent_approval_date=form.rent_approval_date.data, # set approval date only when admin approves
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
                                       property_name=form.property_name.data,
                                       property_description=form.property_description.data,
                                       created_at=datetime.now(),
                                       gender=form.gender.data)
        db.session.add(new_property)
        db.session.commit()
        db.session.refresh(new_property)

        property_id = new_property.property_id

        reformatted_filename = f"{property_id}"

        # save the approval form to the respective folder
        approval_form_file_path = os.path.join(current_app.config["APPROVAL_DOCUMENT_UPLOAD_FOLDER"], reformatted_filename + ".pdf")
        approval.save(approval_form_file_path)
        new_property.approval_form = reformatted_filename + ".pdf"
        db.session.commit()

        # save the image(s) to the respective folder and add it into the property_image database
        # image_url in the property_image database will store all images separated by a comma
        for i, image in enumerate(form.image.data):
            image_form_file_path = os.path.join(current_app.config["IMAGE_UPLOAD_FOLDER"], reformatted_filename + f"_{i}.png")
            image.save(image_form_file_path)
            new_property_image = PropertyImages(property_id=property_id,
                                                image_url=reformatted_filename+f"_{i}.png")
            db.session.add(new_property_image)
            db.session.commit()
        flash("Property registered, pending approval", "success")
        return redirect(url_for('views.manage_property_unapproved'))

    return render_template("register_property.html", user=current_user, form=form)

@views.route("/manage_property/edit_property/<prop_id>", methods=["GET", "POST"])
@landlord_required
def edit_property(prop_id):
    form = forms.EditProperty()
    # get the property with prop_id and prefill in the form with previous information
    current_property = Property.query.filter_by(property_id=prop_id).first()

    if request.method == "GET":
        # prefill the form
        form.property_name.data = current_property.property_name
        form.monthly_rent.data = current_property.monthly_rent
        form.num_bedrooms.data = current_property.number_of_bedrooms
        form.gender.data = current_property.gender
        form.furnishing.data = current_property.furnishing
        form.lease_term.data = current_property.lease_term
        form.negotiable.data = current_property.negotiable_pricing
        form.property_description.data = current_property.property_description
    else:
        if form.validate_on_submit():

            new_monthly_rent = None
            new_num_bedrooms = None
            new_gender = None
            new_furnishing = None
            new_lease_term = None
            new_negotiable = None
            new_name = None
            new_description = None

            # update the data in the property, property image database
            # check if the input data is different from current data
            if form.monthly_rent.data != current_property.monthly_rent:
                new_monthly_rent = form.monthly_rent.data
            if form.num_bedrooms.data != current_property.number_of_bedrooms:
                new_num_bedrooms = form.num_bedrooms.data
            if form.gender.data != current_property.gender:
                new_gender = form.gender.data
            if form.furnishing.data != current_property.furnishing:
                new_furnishing = form.furnishing.data
            if form.lease_term.data != current_property.lease_term:
                new_lease_term = form.lease_term.data
            if form.negotiable != current_property.negotiable_pricing:
                new_negotiable = form.negotiable.data
            if form.property_name != current_property.property_name:
                new_name = form.property_name.data
            if form.property_description != current_property.property_description:
                new_description = form.property_description.data

            Property.update_property(property_id=prop_id,
                                     monthly_rent=new_monthly_rent,
                                     num_bedrooms=new_num_bedrooms,
                                     gender=new_gender,
                                     furnishing=new_furnishing,
                                     lease_term=new_lease_term,
                                     negotiable=new_negotiable,
                                     property_name=new_name,
                                     property_description=new_description)

            # check the images and approval document
            approval_form_filename = secure_filename(form.approval_form.name)  # get the file name from the form
            approval = request.files[approval_form_filename]  # get the filestorage object

            if approval.filename == "":  # empty file name, no file selected
                flash("No approval file selected", "error")
                return redirect(url_for('views.edit_property', prop_id=prop_id))

            if not allowed_file(approval.filename, APPROVAL_FORM_ALLOWED_EXTENSIONS):  # check if file is pdf type
                flash("Invalid approval file type, only .pdf files are allowed", "error")
                return redirect(url_for('views.edit_property', prop_id=prop_id))

            reformatted_filename = f"{prop_id}"
            approval_form_file_path = os.path.join(current_app.config["APPROVAL_DOCUMENT_UPLOAD_FOLDER"], reformatted_filename + ".pdf")

            # delete the old approval form
            if os.path.exists(approval_form_file_path):
                os.remove(approval_form_file_path)

            # save the approval form to the respective folder
            approval.save(approval_form_file_path)
            property = Property.query.filter_by(property_id=prop_id).first()
            property.approval_form = reformatted_filename + ".pdf"
            db.session.commit()

            # check if there is any images uploaded
            if form.image.data:
                # new images were submitted
                # get the list of previous images from property image database
                current_images = PropertyImages.query.filter_by(property_id=prop_id).first()
                image_name_list = current_images.image_url.split(",")

                # delete the old images from storage older
                for image in image_name_list:
                    old_image_file_path = os.path.join(current_app.config["IMAGE_UPLOAD_FOLDER"], image.strip())
                    if os.path.exists(old_image_file_path):
                        # delete the image from folder
                        os.remove(old_image_file_path)

                # delete the old images from database
                PropertyImages.reject_property_images(prop_id)

                # add the new images to the folder
                for i, image in enumerate(form.image.data):
                    image_form_file_path = os.path.join(current_app.config["IMAGE_UPLOAD_FOLDER"], reformatted_filename + f"_{i}.png")
                    image.save(image_form_file_path)
                    new_property_image = PropertyImages(property_id=prop_id,
                                                        image_url=reformatted_filename + f"_{i}.png")
                    db.session.add(new_property_image)
                    db.session.commit()

            # flash success message
            flash("Property info updated", "success")

    return render_template("edit_property.html", user=current_user, form=form, prop_id=prop_id)
