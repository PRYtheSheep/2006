from flask import Blueprint, render_template
from flask_login import login_required, current_user

views = Blueprint('views',__name__)

@views.route("/")
def landing_page():
    return render_template("homepage.html", user=current_user)
    
@views.route("/map")
@login_required
def map_page():
    return render_template("homepage.html", user=current_user) # temp
