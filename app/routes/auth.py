from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session
)

from app.services.auth_service import verify_user

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