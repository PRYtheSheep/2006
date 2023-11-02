from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_required, current_user

from .. import forms, db
from ..models import User, Notifications
from werkzeug.security import generate_password_hash, check_password_hash

account_views = Blueprint('account_views', __name__)

@account_views.route('/settings')
@account_views.route('/settings/<string:setting_type>', methods=["GET", "POST"])
@login_required
def account_settings(setting_type=None):
    if not setting_type:
        return render_template("account_settings_page.html", user=current_user, setting_type=setting_type)
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
                    return redirect(url_for('account_views.account_settings'))
                else:
                    flash("Password entered is wrong", 'error')
                    return redirect(url_for('account_views.account_settings', setting_type='account'))
            return render_template("account_settings_page.html", user=current_user, setting_type=setting_type, form=form)
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
                    return redirect(url_for('account_views.account_settings'))
                else:
                    flash("Current Password is wrong", 'error')
                    return redirect(url_for('account_views.account_settings', setting_type='password'))
            return render_template("account_settings_page.html", user=current_user, setting_type=setting_type, form=form)
        else:
            return render_template("404.html", user=current_user)

@account_views.route('/notifications')
@login_required
def notifications_page(page=1):
    all_notifications = db.paginate(db.select(Notifications).where(Notifications.user_id == current_user.user_id).order_by(Notifications.created_at.desc()), per_page=2)
    if request.args.get('page'):
        all_notifications = db.paginate(db.select(Notifications).where(Notifications.user_id == current_user.user_id).order_by(Notifications.created_at.desc()), per_page=2, page=int(request.args.get('page')))
    return render_template("notifications_page.html", user=current_user, all_notifications=all_notifications)
