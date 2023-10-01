from functools import wraps
from flask_login import current_user
from flask import flash, redirect, url_for

def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.account_type == "admin":
            return f(*args, **kwargs)
        else:
            return redirect(url_for('auth.page404'))

    return wrap

def landlord_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.account_type == "landlord":
            return f(*args, **kwargs)
        else:
            return redirect(url_for('auth.page404'))

    return wrap


