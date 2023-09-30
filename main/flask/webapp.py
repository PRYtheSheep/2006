from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("homepage.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        form_data = request.form
        return redirect(url_for("user", usr=form_data["username"]))
    else:
        return render_template("loginpage.html")

@app.route("/<usr>")
def user(usr):
    return f"<h1>{usr}</h1>"


if __name__ == "__main__":
    app.run()