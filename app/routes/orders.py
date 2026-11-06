from flask import (
    Blueprint, render_template,
    redirect, url_for, session
)

from app.database import get_db

orders = Blueprint("orders", __name__)


@orders.route("/manager/orders")
def view_orders():

    if "user_id" not in session:
        return redirect(url_for("auth.manager_login"))

    if session.get("user_role") != "manager":
        return "Access denied!", 403

    db = get_db()

    all_orders = db.execute(
        """
        SELECT orders.*, users.name AS customer_name
        FROM orders
        LEFT JOIN users ON orders.customer_id = users.id
        ORDER BY orders.id DESC
        """
    ).fetchall()

    return render_template(
        "orders.html",
        orders=all_orders
    )