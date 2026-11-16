
from flask import Blueprint, render_template, redirect, url_for, session, request

from app.database import get_db

customers = Blueprint("customers", __name__)


# CUSTOMER LIST
@customers.route("/manager/customers")
def customer_list():

    if "user_id" not in session:
        return redirect(url_for("auth.manager_login"))

    if session.get("user_role") != "manager":
        return "Access denied!", 403

    search = request.args.get("search", "").strip()
    db = get_db()

    # Registered customers
    registered = db.execute(
        """
        SELECT
            users.id,
            users.name,
            users.email,
            users.created_at,
            (
                SELECT COUNT(*)
                FROM orders
                WHERE orders.customer_id = users.id
            ) AS total_orders,
            (
                SELECT COALESCE(SUM(total_amount), 0)
                FROM orders
                WHERE orders.customer_id = users.id
            ) AS total_spent,
            'Registered' AS customer_type,
            NULL AS phone
        FROM users
        WHERE users.role = 'customer'
          AND (
              users.name LIKE ?
              OR users.email LIKE ?
          )
        """,
        (f"%{search}%", f"%{search}%")
    ).fetchall()

    # Guest customers who placed orders without login
    guests = db.execute(
        """
        SELECT
            NULL AS id,
            customer_name AS name,
            NULL AS email,
            MIN(created_at) AS created_at,
            COUNT(*) AS total_orders,
            SUM(total_amount) AS total_spent,
            'Guest' AS customer_type,
            phone
        FROM orders
        WHERE customer_id IS NULL
          AND (
              customer_name LIKE ?
              OR phone LIKE ?
          )
        GROUP BY customer_name, phone
        """,
        (f"%{search}%", f"%{search}%")
    ).fetchall()

    all_customers = [
        dict(customer) for customer in registered
    ] + [
        dict(customer) for customer in guests
    ]

    all_customers.sort(
        key=lambda customer: customer["created_at"] or "",
        reverse=True
    )

    return render_template(
        "customers.html",
        customers=all_customers,
        search=search
    )


# REGISTERED CUSTOMER DETAILS
@customers.route("/manager/customers/<int:customer_id>")
def customer_details(customer_id):

    if "user_id" not in session:
        return redirect(url_for("auth.manager_login"))

    if session.get("user_role") != "manager":
        return "Access denied!", 403

    db = get_db()

    customer = db.execute(
        """
        SELECT id, name, email, created_at
        FROM users
        WHERE id = ? AND role = 'customer'
        """,
        (customer_id,)
    ).fetchone()

    if customer is None:
        return "Customer not found.", 404

    customer_orders = db.execute(
        """
        SELECT *
        FROM orders
        WHERE customer_id = ?
        ORDER BY created_at DESC, id DESC
        """,
        (customer_id,)
    ).fetchall()

    return render_template(
        "customer_details.html",
        customer=customer,
        orders=customer_orders
    )


# GUEST CUSTOMER DETAILS
@customers.route("/manager/guest-customers/<path:phone>")
def guest_customer_details(phone):

    if "user_id" not in session:
        return redirect(url_for("auth.manager_login"))

    if session.get("user_role") != "manager":
        return "Access denied!", 403

    db = get_db()

    guest = db.execute(
        """
        SELECT
            customer_name AS name,
            phone,
            MIN(created_at) AS created_at
        FROM orders
        WHERE customer_id IS NULL AND phone = ?
        GROUP BY customer_name, phone
        """,
        (phone,)
    ).fetchone()

    if guest is None:
        return "Customer not found.", 404

    guest_orders = db.execute(
        """
        SELECT *
        FROM orders
        WHERE customer_id IS NULL AND phone = ?
        ORDER BY created_at DESC, id DESC
        """,
        (phone,)
    ).fetchall()

    return render_template(
        "customer_details.html",
        customer=guest,
        orders=guest_orders,
        is_guest=True
    )
