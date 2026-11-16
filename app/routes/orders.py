
from flask import (
    Blueprint, render_template,
    redirect, url_for, session, request, flash
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
            COALESCE(orders.customer_name, users.name, 'Guest')
            AS display_customer_name
        FROM orders
        LEFT JOIN users ON orders.customer_id = users.id
        ORDER BY orders.id DESC
        """
    ).fetchall()

    return render_template(
        "orders.html",
        orders=all_orders
    )


# ORDER DETAILS
@orders.route("/manager/orders/<int:order_id>")
def order_details(order_id):

    if "user_id" not in session:
        return redirect(url_for("auth.manager_login"))

    if session.get("user_role") != "manager":
        return "Access denied!", 403

    db = get_db()

    order = db.execute(
        """
        SELECT orders.*,
               COALESCE(orders.customer_name, users.name, 'Guest')
               AS display_customer_name
        FROM orders
        LEFT JOIN users ON orders.customer_id = users.id
        WHERE orders.id = ?
        """,
        (order_id,)
    ).fetchone()

    if order is None:
        return "Order not found.", 404

    order_items = db.execute(
        """
        SELECT order_items.*,
               products.name AS product_name
        FROM order_items
        JOIN products ON order_items.product_id = products.id
        WHERE order_items.order_id = ?
        """,
        (order_id,)
    ).fetchall()

    return render_template(
        "order_details.html",
        order=order,
        order_items=order_items
    )


# UPDATE ORDER STATUS
@orders.route(
    "/manager/orders/update-status/<int:order_id>",
    methods=["POST"]
)
def update_order_status(order_id):

    if "user_id" not in session:
        return redirect(url_for("auth.manager_login"))

    if session.get("user_role") != "manager":
        return "Access denied!", 403

    allowed_statuses = [
        "Pending",
        "Confirmed",
        "Processing",
        "Dispatched",
        "Delivered",
        "Cancelled"
    ]

    new_status = request.form.get("status")

    if new_status not in allowed_statuses:
        return "Invalid order status.", 400

    db = get_db()

    db.execute(
        "UPDATE orders SET status = ? WHERE id = ?",
        (new_status, order_id)
    )
    db.commit()

    return redirect(
        url_for("orders.order_details", order_id=order_id)
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


# CUSTOMER ORDER HISTORY
@orders.route("/customer/orders")
def customer_order_history():

    if "user_id" not in session or session.get("user_role") != "customer":
        return redirect(url_for("auth.customer_login"))

    db = get_db()

    customer_orders = db.execute(
        """
        SELECT *
        FROM orders
        WHERE customer_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    return render_template(
        "customer_orders.html",
        orders=customer_orders
    )


# CUSTOMER ORDER DETAILS
@orders.route("/customer/orders/<int:order_id>")
def customer_order_details(order_id):

    if "user_id" not in session or session.get("user_role") != "customer":
        return redirect(url_for("auth.customer_login"))

    db = get_db()

    order = db.execute(
        """
        SELECT *
        FROM orders
        WHERE id = ? AND customer_id = ?
        """,
        (order_id, session["user_id"])
    ).fetchone()

    if order is None:
        return "Order not found.", 404

    order_items = db.execute(
        """
        SELECT
            order_items.*,
            products.name AS product_name
        FROM order_items
        JOIN products ON order_items.product_id = products.id
        WHERE order_items.order_id = ?
        """,
        (order_id,)
    ).fetchall()

    # FETCH EXISTING CUSTOMER REVIEW
    review = db.execute(
        """
        SELECT *
        FROM reviews
        WHERE order_id = ? AND customer_id = ?
        """,
        (order_id, session["user_id"])
    ).fetchone()

    return render_template(
        "customer_order_details.html",
        order=order,
        order_items=order_items,
        review=review
    )


# CUSTOMER SUBMIT REVIEW
@orders.route(
    "/customer/orders/<int:order_id>/review",
    methods=["POST"]
)
def submit_review(order_id):

    if "user_id" not in session or session.get("user_role") != "customer":
        return redirect(url_for("auth.customer_login"))

    db = get_db()

    order = db.execute(
        """
        SELECT *
        FROM orders
        WHERE id = ? AND customer_id = ?
        """,
        (order_id, session["user_id"])
    ).fetchone()

    if order is None:
        return "Order not found.", 404

    if order["status"] != "Delivered":
        flash("You can only review delivered orders.", "error")
        return redirect(
            url_for("orders.customer_order_details", order_id=order_id)
        )

    # CHECK IF REVIEW ALREADY EXISTS
    existing_review = db.execute(
        """
        SELECT id
        FROM reviews
        WHERE order_id = ?
        """,
        (order_id,)
    ).fetchone()

    if existing_review:
        flash("You have already reviewed this order.", "error")
        return redirect(
            url_for("orders.customer_order_details", order_id=order_id)
        )

    # ACCEPT HALF-STAR RATINGS
    try:
        rating = float(request.form.get("rating", 0))
    except (ValueError, TypeError):
        rating = 0

    comment = request.form.get("comment", "").strip()

    # VALIDATE RATING: 0.5, 1, 1.5, 2 ... 5
    if (
        not 0.5 <= rating <= 5
        or rating * 2 != int(rating * 2)
    ):
        flash(
            "Please select a valid rating between 0.5 and 5 stars.",
            "error"
        )
        return redirect(
            url_for("orders.customer_order_details", order_id=order_id)
        )

    # VALIDATE COMMENT LENGTH
    if len(comment) > 1000:
        flash("Review cannot exceed 1000 characters.", "error")
        return redirect(
            url_for("orders.customer_order_details", order_id=order_id)
        )

    # SAVE REVIEW
    db.execute(
        """
        INSERT INTO reviews (
            order_id, customer_id, rating, comment
        )
        VALUES (?, ?, ?, ?)
        """,
        (order_id, session["user_id"], rating, comment)
    )

    db.commit()

    flash("Thank you! Your review has been submitted.", "success")

    return redirect(
        url_for("orders.customer_order_details", order_id=order_id)
    )
