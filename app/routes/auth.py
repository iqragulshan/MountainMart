from flask import (
        Blueprint, render_template, request,
        redirect, url_for, flash, session
    )

from app.services.auth_service import verify_user, create_user
import sqlite3

auth = Blueprint("auth", __name__)


@auth.route("/manager/login", methods=["GET", "POST"])
def manager_login():

        if request.method == "POST":

            email = request.form.get("email")
            password = request.form.get("password")

            user = verify_user(email, password, "manager")

            if user is None:
                flash("Invalid email or password.", "error")
                return redirect(url_for("auth.manager_login"))

            session.clear()
            session["user_id"] = user["id"]
            session["user_role"] = user["role"]
            session["user_name"] = user["name"]

            return redirect(url_for("main.manager_dashboard"))

        return render_template("manager_login.html")

@auth.route("/manager/logout")
def manager_logout():

        session.clear()

        return redirect(url_for("auth.manager_login"))


# CUSTOMER LOGIN
@auth.route("/customer/login", methods=["GET", "POST"])
def customer_login():

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = verify_user(email, password, "customer")

        if user is None:
            flash("Invalid email or password.", "error")
            return redirect(url_for("auth.customer_login"))

        session.clear()
        session["user_id"] = user["id"]
        session["user_role"] = user["role"]
        session["user_name"] = user["name"]

        return redirect(url_for("customer.customer_home"))

    return render_template("customer_login.html")


# CUSTOMER REGISTRATION
@auth.route("/customer/register", methods=["GET", "POST"])
def customer_register():

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not name or not email or not password:
            flash("Please fill in all fields.", "error")
            return redirect(url_for("auth.customer_register"))

        try:
            create_user(name, email, password, "customer")
            flash("Account created successfully! Please login.", "success")
            return redirect(url_for("auth.customer_login"))

        except sqlite3.IntegrityError:
            flash("This email is already registered.", "error")
            return redirect(url_for("auth.customer_register"))

    return render_template("customer_register.html")


# CUSTOMER LOGOUT
@auth.route("/customer/logout")
def customer_logout():

    session.clear()

    return redirect(url_for("customer.customer_home"))