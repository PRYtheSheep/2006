from flask import Blueprint, render_template, url_for, flash, redirect
from flask_login import login_required, current_user

from .. import forms, db
from ..models import User
from werkzeug.security import generate_password_hash, check_password_hash

account_views = Blueprint('account_views', __name__)

@account_views.route('/settings')
@account_views.route('/settings/<string:setting_type>', methods=["GET", "POST"])
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

