from flask import (
    Blueprint, render_template,
    redirect, url_for, session, request
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
          SELECT 
            orders.*,
            COALESCE(orders.customer_name, users.name, 'Guest') AS display_customer_name
    FROM orders
    LEFT JOIN users ON orders.customer_id = users.id
    ORDER BY orders.id DESC
        """
    ).fetchall()

    return render_template(
        "orders.html",
        orders=all_orders
    )


# DEMO ONLINE PAYMENT
@orders.route(
    "/customer/payment/<int:order_id>",
    methods=["GET", "POST"]
)
def demo_payment(order_id):

    db = get_db()

    order = db.execute(
        "SELECT * FROM orders WHERE id = ?",
        (order_id,)
    ).fetchone()

    if order is None:
        return "Order not found.", 404

    if order["payment_method"] != "Demo Online Payment":
        return redirect(
            url_for("orders.order_success", order_id=order_id)
        )

    if order["payment_status"] == "Paid (Demo)":
        return redirect(
            url_for("orders.order_success", order_id=order_id)
        )

    if request.method == "POST":

        result = request.form.get("result")

        if result == "success":

            db.execute(
                """
                UPDATE orders
                SET payment_status = ?
                WHERE id = ?
                """,
                ("Paid (Demo)", order_id)
            )

            db.commit()

            return redirect(
                url_for("orders.order_success", order_id=order_id)
            )

        elif result == "failure":

            db.execute(
                """
                UPDATE orders
                SET payment_status = ?
                WHERE id = ?
                """,
                ("Failed", order_id)
            )

            db.commit()

            return redirect(
                url_for("orders.order_success", order_id=order_id)
            )

    return render_template(
        "payment_demo.html",
        order=order
    )


# ORDER SUCCESS / RESULT PAGE
@orders.route("/customer/order-success/<int:order_id>")
def order_success(order_id):

    db = get_db()

    order = db.execute(
        "SELECT * FROM orders WHERE id = ?",
        (order_id,)
    ).fetchone()

    if order is None:
        return "Order not found.", 404

    order_items = db.execute(
        """
        SELECT order_items.*, products.name AS product_name
        FROM order_items
        JOIN products ON order_items.product_id = products.id
        WHERE order_items.order_id = ?
        """,
        (order_id,)
    ).fetchall()

    return render_template(
        "order_success.html",
        order=order,
        order_items=order_items
    )
