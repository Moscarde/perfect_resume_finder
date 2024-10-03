from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" not in session or not session["logged_in"]:
            flash("You must be logged in to access this page.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin":
            session["logged_in"] = True
            session["username"] = username
            flash("Login successful!", "success")
            return redirect(url_for("home.home"))
        else:
            flash("Invalid credentials, please try again.", "danger")

    return render_template("login.html")

@auth_bp.route("/logout")
@login_required
def logout():
    session.pop("logged_in", None)
    flash("Logout successful!", "success")
    return redirect(url_for("auth.login"))
