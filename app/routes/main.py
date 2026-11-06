from flask import Blueprint, redirect, url_for, session, render_template
from app.database import get_db

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return "Welcome to Mountain Mart!"


@main.route("/manager/dashboard")
def manager_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.manager_login"))

    if session.get("user_role") != "manager":
        return "Access denied!", 403

    db = get_db()

    total_products = db.execute(
        "SELECT COUNT(*) FROM products"
    ).fetchone()[0]

    low_stock = db.execute(
        """
        SELECT COUNT(*) FROM products
        WHERE quantity > 0 AND quantity <= min_stock
        """
    ).fetchone()[0]

    out_of_stock = db.execute(
        """
        SELECT COUNT(*) FROM products
        WHERE quantity = 0
        """
    ).fetchone()[0]

    total_inventory = db.execute(
        "SELECT COALESCE(SUM(quantity), 0) FROM products"
    ).fetchone()[0]

    return render_template(
        "manager_dashboard.html",
        total_products=total_products,
        low_stock=low_stock,
        out_of_stock=out_of_stock,
        total_inventory=total_inventory
    )