
from flask import (
    Blueprint, redirect, url_for, session,
    render_template, request, flash
)
from app.database import get_db

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return "Welcome to Mountain Mart!"


# MANAGER DASHBOARD
@main.route("/manager/dashboard")
def manager_dashboard():

    manager = session.get("manager")

    if not manager:
        return redirect(url_for("auth.manager_login"))

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

    new_orders = db.execute(
        """
        SELECT COUNT(*) FROM orders
        WHERE status = 'Pending'
        """
    ).fetchone()[0]

    return render_template(
        "manager_dashboard.html",
        total_products=total_products,
        low_stock=low_stock,
        out_of_stock=out_of_stock,
        total_inventory=total_inventory,
        new_orders=new_orders
    )


# SALES REPORTS
@main.route("/manager/reports")
def sales_reports():

    if not session.get("manager"):
        return redirect(url_for("auth.manager_login"))

    db = get_db()

    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")

    date_condition = ""
    params = []

    if start_date:
        date_condition += " AND DATE(orders.created_at) >= DATE(?)"
        params.append(start_date)

    if end_date:
        date_condition += " AND DATE(orders.created_at) <= DATE(?)"
        params.append(end_date)

    completed_sales = db.execute(
        f"""
        SELECT COALESCE(SUM(total_amount), 0)
        FROM orders
        WHERE status = 'Delivered'
        {date_condition.replace('orders.', '')}
        """,
        params
    ).fetchone()[0]

    total_orders = db.execute(
        f"""
        SELECT COUNT(*)
        FROM orders
        WHERE 1=1 {date_condition}
        """,
        params
    ).fetchone()[0]

    delivered_orders = db.execute(
        f"""
        SELECT COUNT(*)
        FROM orders
        WHERE status = 'Delivered' {date_condition}
        """,
        params
    ).fetchone()[0]

    pending_value = db.execute(
        f"""
        SELECT COALESCE(SUM(total_amount), 0)
        FROM orders
        WHERE status NOT IN ('Delivered', 'Cancelled')
        {date_condition}
        """,
        params
    ).fetchone()[0]

    monthly_sales = db.execute(
        f"""
        SELECT
            strftime('%Y-%m', created_at) AS month,
            SUM(total_amount) AS revenue
        FROM orders
        WHERE status = 'Delivered'
        {date_condition.replace('orders.', '')}
        GROUP BY strftime('%Y-%m', created_at)
        ORDER BY month ASC
        LIMIT 6
        """,
        params
    ).fetchall()

    best_selling_products = db.execute(
        f"""
        SELECT
            products.name AS product_name,
            SUM(order_items.quantity) AS total_sold,
            SUM(order_items.quantity * order_items.price) AS revenue
        FROM order_items
        JOIN products ON order_items.product_id = products.id
        JOIN orders ON order_items.order_id = orders.id
        WHERE orders.status = 'Delivered'
        {date_condition}
        GROUP BY products.id, products.name
        ORDER BY total_sold DESC
        LIMIT 5
        """,
        params
    ).fetchall()

    return render_template(
        "reports.html",
        completed_sales=completed_sales,
        total_orders=total_orders,
        delivered_orders=delivered_orders,
        pending_value=pending_value,
        monthly_sales=monthly_sales,
        best_selling_products=best_selling_products,
        start_date=start_date,
        end_date=end_date
    )


# SALES CHART DATA
@main.route("/manager/reports/chart-data")
def sales_chart_data():

    if not session.get("manager"):
        return {"error": "Unauthorized"}, 401

    db = get_db()

    monthly_sales = db.execute(
        """
        SELECT
            strftime('%Y-%m', created_at) AS month,
            SUM(total_amount) AS revenue
        FROM orders
        WHERE status = 'Delivered'
        GROUP BY month
        ORDER BY month ASC
        LIMIT 6
        """
    ).fetchall()

    return {
        "labels": [row["month"] for row in monthly_sales],
        "values": [row["revenue"] for row in monthly_sales]
    }


# MANAGER REVIEWS
@main.route("/manager/reviews")
def manager_reviews():

    if not session.get("manager"):
        return redirect(url_for("auth.manager_login"))

    db = get_db()

    reviews = db.execute("""
        SELECT
            reviews.id,
            reviews.rating,
            reviews.comment,
            reviews.created_at,
            COALESCE(
                NULLIF(orders.customer_name, ''),
                users.name,
                'Guest'
            ) AS customer_name
        FROM reviews
        LEFT JOIN orders
            ON reviews.order_id = orders.id
        LEFT JOIN users
            ON reviews.customer_id = users.id
        ORDER BY reviews.created_at DESC
    """).fetchall()

    review_stats = db.execute("""
        SELECT
            COUNT(*) AS total_reviews,
            COALESCE(AVG(rating), 0) AS average_rating
        FROM reviews
    """).fetchone()

    return render_template(
        "manager_reviews.html",
        reviews=reviews,
        review_stats=review_stats
    )


# STORE SETTINGS
@main.route("/manager/settings", methods=["GET", "POST"])
def store_settings():

    if not session.get("manager"):
        return redirect(url_for("auth.manager_login"))

    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS store_settings (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            store_name TEXT NOT NULL DEFAULT 'Mountain Mart',
            phone TEXT,
            address TEXT,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    db.execute("""
        INSERT OR IGNORE INTO store_settings (id)
        VALUES (1)
    """)
    db.commit()

    if request.method == "POST":

        store_name = request.form.get("store_name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        description = request.form.get("description", "").strip()

        if not store_name:
            flash("Store name is required.", "error")
        else:
            db.execute("""
                UPDATE store_settings
                SET store_name = ?,
                    phone = ?,
                    address = ?,
                    description = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = 1
            """, (store_name, phone, address, description))

            db.commit()
            flash("Store settings updated successfully!", "success")

        return redirect(url_for("main.store_settings"))

    settings = db.execute("""
        SELECT * FROM store_settings
        WHERE id = 1
    """).fetchone()

    return render_template(
        "store_settings.html",
        settings=settings
    )
