import os.path

from flask import Blueprint, render_template, url_for, flash, redirect, request, send_from_directory, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from .custom_decorators import admin_required, landlord_required
from .. import forms, db
from ..models import Property, PropertyImages

admin = Blueprint('admin', __name__)


@admin.route("/")
@login_required
@admin_required
def admin_panel():
    unapproved_properties = db.paginate(Property.query.order_by(Property.created_at.desc()).filter_by(is_approved=0),
                                        per_page=5)
    if request.args.get('page'):
        unapproved_properties = db.paginate(
            Property.query.order_by(Property.created_at.desc()).filter_by(is_approved=0), per_page=5,
            page=int(request.args.get('page')))

    return render_template("admin_panel_page.html", user=current_user, unapproved_properties=unapproved_properties)


APPROVAL_FORM_FOLDER = 'website/storage/approval_documents'
IMAGE_FOLDER = 'website/storage/property_images'


@admin.route("/manage_approval_document", methods=["GET", "POST"])
@login_required
@admin_required
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
            # delete the images from database
            current_image_url_list = PropertyImages.reject_property_images(prop_id)

            # delete the proeprty from database
            Property.reject_property(prop_id)
            current_app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER

            # delete the images
            for image in current_image_url_list:
                old_image_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image.strip())
                if os.path.exists(old_image_file_path):
                    # delete the image from folder
                    os.remove(old_image_file_path)

            current_app.config['UPLOAD_FOLDER'] = APPROVAL_FORM_FOLDER
            reformatted_filename = f"{prop_id}"
            approval_form_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'],
                                                   reformatted_filename + ".pdf")

            # delete the old approval form
            if os.path.exists(approval_form_file_path):
                os.remove(approval_form_file_path)

            flash("Property rejected, deleted from database", "error")

    return render_template("manage_approval.html", user=current_user, form=form)
