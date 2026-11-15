
from flask import Blueprint, redirect, url_for, session, render_template, request
from app.database import get_db

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return "Welcome to Mountain Mart!"


# MANAGER DASHBOARD
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

    if "user_id" not in session:
        return redirect(url_for("auth.manager_login"))

    if session.get("user_role") != "manager":
        return "Access denied!", 403

    db = get_db()

    # DATE FILTER
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

    # COMPLETED SALES
    completed_sales = db.execute(
        f"""
        SELECT COALESCE(SUM(total_amount), 0)
        FROM orders
        WHERE status = 'Delivered'
        {date_condition.replace('orders.', '')}
        """,
        params
    ).fetchone()[0]

    # TOTAL ORDERS
    total_orders = db.execute(
        f"""
        SELECT COUNT(*)
        FROM orders
        WHERE 1=1 {date_condition}
        """,
        params
    ).fetchone()[0]

    # DELIVERED ORDERS
    delivered_orders = db.execute(
        f"""
        SELECT COUNT(*)
        FROM orders
        WHERE status = 'Delivered' {date_condition}
        """,
        params
    ).fetchone()[0]

    # PENDING ORDER VALUE
    pending_value = db.execute(
        f"""
        SELECT COALESCE(SUM(total_amount), 0)
        FROM orders
        WHERE status NOT IN ('Delivered', 'Cancelled')
        {date_condition}
        """,
        params
    ).fetchone()[0]

    # MONTHLY SALES
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

    # BEST-SELLING PRODUCTS
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

    if "user_id" not in session:
        return {"error": "Unauthorized"}, 401

    if session.get("user_role") != "manager":
        return {"error": "Access denied"}, 403

    db = get_db()

    monthly_sales = db.execute(
        """
        SELECT
            strftime('%Y-%m', created_at) AS month,
            SUM(total_amount) AS revenue
        FROM orders
        WHERE status = 'Delivered'
        GROUP BY strftime('%Y-%m', created_at)
        ORDER BY month ASC
        LIMIT 6
        """
    ).fetchall()

    return {
        "labels": [row["month"] for row in monthly_sales],
        "values": [row["revenue"] for row in monthly_sales]
    }
