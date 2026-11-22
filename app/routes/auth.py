
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session
)

from app.services.auth_service import verify_user, create_user
from app.database import get_db
import sqlite3

auth = Blueprint("auth", __name__)


# MANAGER LOGIN
@auth.route("/manager/login", methods=["GET", "POST"])
def manager_login():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        user = verify_user(email, password, "manager")

        if user is None:
            flash("Invalid email or password.", "error")
            return redirect(url_for("auth.manager_login"))

        session.pop("user_id", None)
        session.pop("user_role", None)
        session.pop("user_name", None)

        session["manager"] = {
            "user_id": user["id"],
            "user_role": user["role"],
            "user_name": user["name"]
        }

        return redirect(url_for("main.manager_dashboard"))

    return render_template("manager_login.html")


# MANAGER LOGOUT
@auth.route("/manager/logout")
def manager_logout():

    session.pop("manager", None)
    return redirect(url_for("auth.manager_login"))


# CUSTOMER REGISTRATION
@auth.route("/customer/register", methods=["GET", "POST"])
def customer_register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password or not confirm_password:
            flash("Please fill in all fields.", "error")

        elif password != confirm_password:
            flash("Passwords do not match.", "error")

        elif len(password) < 8:
            flash("Password must be at least 8 characters.", "error")

        else:
            try:
                create_user(name, email, password, "customer")
                flash("Account created successfully. Please login.", "success")
                return redirect(url_for("auth.customer_login"))

            except sqlite3.IntegrityError:
                get_db().rollback()
                flash("This email is already registered.", "error")

    return render_template("customer_register.html")


# CUSTOMER LOGIN
@auth.route("/customer/login", methods=["GET", "POST"])
def customer_login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = verify_user(email, password, "customer")

        if user is None:
            flash("Invalid email or password.", "error")
            return redirect(url_for("auth.customer_login"))

        session["customer"] = {
            "user_id": user["id"],
            "user_role": user["role"],
            "user_name": user["name"]
        }

        return redirect(url_for("customer.customer_home"))

    return render_template("customer_login.html")


# CUSTOMER LOGOUT
@auth.route("/customer/logout")
def customer_logout():

    session.pop("customer", None)
    return redirect(url_for("customer.customer_home"))
