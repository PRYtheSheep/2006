import os.path

from flask import Blueprint, render_template, url_for, flash, redirect, request, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
from .custom_decorators import admin_required, landlord_required
from .. import forms, db
from ..models import Property, PropertyImages, Notifications

admin = Blueprint('admin', __name__)

@admin.route("/unapproved_properties")
@login_required
@admin_required
def admin_panel():
    properties = db.paginate(Property.query.order_by(Property.created_at.desc()).filter_by(is_approved=0),
                                        per_page=5)
    if request.args.get('page'):
        properties = db.paginate(
            Property.query.order_by(Property.created_at.desc()).filter_by(is_approved=0), per_page=5,
            page=int(request.args.get('page')))

    return render_template("admin_panel_page.html", user=current_user, properties=properties, unapproved=1, pending_deletion=0)

@admin.route("/pending_deletion")
@login_required
@admin_required
def admin_panel_pending_deletion():
    properties = db.paginate(Property.query.order_by(Property.created_at.desc()).filter_by(is_pending_deletion=1),
                                        per_page=5)
    if request.args.get('page'):
        properties = db.paginate(
            Property.query.order_by(Property.created_at.desc()).filter_by(is_pending_deletion=1), per_page=5,
            page=int(request.args.get('page')))

    return render_template("admin_panel_page.html", user=current_user, properties=properties, pending_deletion=1, unapproved=0)

@admin.route("/manage_property_listing/property-<int:property_id>/<string:manage_type>", methods=["GET", "POST"])
@login_required
@admin_required
def manage_approval(property_id, manage_type):
    form = forms.AdminPropertyViewForm()
    property = Property.query.filter_by(property_id=property_id).first()

    if not property:
        flash("Invalid Property ID", "error")
        return redirect(url_for("admin.admin_panel"))
    
    # fill up form with existing data
    form.user_id.data = property.user_id
    form.full_name.data = property.user.first_name + " " + property.user.last_name
    form.email.data = property.user.email
    form.property_id.data = property.property_id
    form.property_name.data = property.property_name
    form.property_description.data = property.property_description
    form.block.data = property.block
    form.street_name.data = property.street_name
    form.building.data = property.building
    form.postal_code.data = property.postal
    form.town.data = property.town
    form.flat_type.data = property.flat_type
    form.monthly_rent.data = property.monthly_rent
    form.num_bedrooms.data = property.number_of_bedrooms
    form.floor_size.data = property.floorsize
    form.ppsm.data = property.price_per_square_metre
    form.year_built.data = property.year_built
    form.furnishing.data = property.furnishing
    form.floor_level.data = property.floor_level
    form.lease_term.data = property.lease_term
    form.negotiable.data = property.negotiable_pricing
    form.created_at.data = property.created_at

    # approve property
    if form.validate_on_submit() and form.approve_field.data:
        Notifications.new_notification(property.user_id, "Property Approved", f"Your property '{property.property_name}' has been approved.")
        property.is_approved = True
        property.rent_approval_date = datetime.now()
        db.session.commit()

        flash(f"Property {property_id} approved",'success')
        return redirect(url_for("admin.admin_panel"))

    # reject property
    elif form.validate_on_submit() and form.reject_field.data:
        Notifications.new_notification(property.user_id, "Property Rejected", f"Your property '{property.property_name}' has been rejected, reason: {form.reject_reason.data}. Current listing will be deleted. You can resubmit your property again.")

        # delete the images from database
        current_image_url_list = PropertyImages.reject_property_images(property_id)

        # delete the property from database
        approval_document = Property.reject_property(property_id)

        # delete the images
        for image in current_image_url_list:
            old_image_file_path = os.path.join(current_app.config['IMAGE_UPLOAD_FOLDER'], image.strip())
            if os.path.exists(old_image_file_path):
                # delete the image from folder
                os.remove(old_image_file_path)

       # delete the old approval form
        approval_form_file_path = os.path.join(current_app.config['APPROVAL_DOCUMENT_UPLOAD_FOLDER'],
                                                approval_document)
        if os.path.exists(approval_form_file_path):
            os.remove(approval_form_file_path)

        flash(f"Property {property_id} rejected", "success")
        return redirect(url_for("admin.admin_panel"))

    # delete property
    elif form.validate_on_submit() and form.delete_field:
        Notifications.new_notification(property.user_id, "Property Deleted", f"Your request for property '{property.property_name}' to be deleted has been approved.")
        # delete the images from database
        current_image_url_list = PropertyImages.reject_property_images(property_id)

        # delete the property from database
        approval_document = Property.reject_property(property_id)

        # delete the images
        for image in current_image_url_list:
            old_image_file_path = os.path.join(current_app.config['IMAGE_UPLOAD_FOLDER'], image.strip())
            if os.path.exists(old_image_file_path):
                # delete the image from folder
                os.remove(old_image_file_path)

        # delete the old approval form
        approval_form_file_path = os.path.join(current_app.config['APPROVAL_DOCUMENT_UPLOAD_FOLDER'],
                                                approval_document)
        if os.path.exists(approval_form_file_path):
            os.remove(approval_form_file_path)

        flash(f"Property {property_id} deleted", "success")
        return redirect(url_for("admin.admin_panel"))

    return render_template("admin_manage_properties_page.html", user=current_user, property=property, form=form, manage_type=manage_type)


@admin.route("/storage/<path:filename>")
@login_required
@admin_required
def approval_document_url(filename):
    path = (os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'website', 'storage', 'approval_documents'))
    return send_from_directory(directory=path, path=filename)