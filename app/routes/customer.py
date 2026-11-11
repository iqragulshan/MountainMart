from flask import Blueprint, render_template, request
from app.database import get_db

customer = Blueprint("customer", __name__)


@customer.route("/customer")
def customer_home():

    db = get_db()

    search = request.args.get("search", "").strip()
    selected_category = request.args.get("category", "").strip()

    categories = db.execute(
        """
        SELECT DISTINCT category
        FROM products
        WHERE category IS NOT NULL AND category != ''
        ORDER BY category ASC
        """
    ).fetchall()                                    

    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if search:
        query += " AND (name LIKE ? OR category LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if selected_category:
        query += " AND category = ?"
        params.append(selected_category)

    query += " ORDER BY name ASC"

    products = db.execute(query, params).fetchall()

    return render_template(
        "customer_home.html",
        products=products,
        search=search,
        categories=categories,
        selected_category=selected_category
    )