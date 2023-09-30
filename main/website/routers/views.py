from flask import Blueprint, render_template

views = Blueprint('views',__name__)

@views.route("/")
def landing_page():
    return render_template("homepage.html")
    
