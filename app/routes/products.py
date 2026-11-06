
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash
)

from app.database import get_db

products = Blueprint("products", __name__)


@products.route("/manager/products/add", methods=["GET", "POST"])
def add_product():

    if "user_id" not in session:
        return redirect(url_for("auth.manager_login"))

    if session.get("user_role") != "manager":
        return "Access denied!", 403

    if request.method == "POST":

        name = request.form.get("name")
        category = request.form.get("category")
        price = request.form.get("price")
        quantity = request.form.get("quantity")
        min_stock = request.form.get("min_stock")
        description = request.form.get("description")

        db = get_db()

        db.execute(
            """
            INSERT INTO products
            (name, category, price, quantity, min_stock, description)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, category, price, quantity, min_stock, description)
        )

        db.commit()

        flash("Product added successfully!", "success")

        return redirect(url_for("products.add_product"))

    return render_template("add_product.html")

@products.route("/manager/products")
def view_products():

    if "user_id" not in session:
        return redirect(url_for("auth.manager_login"))

    if session.get("user_role") != "manager":
        return "Access denied!", 403

    db = get_db()

    all_products = db.execute(
        "SELECT * FROM products ORDER BY id DESC"
    ).fetchall()

    return render_template(
        "view_products.html",
        products=all_products
    )

@products.route("/manager/products/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):

    if "user_id" not in session:
        return redirect(url_for("auth.manager_login"))

    if session.get("user_role") != "manager":
        return "Access denied!", 403

    db = get_db()

    product = db.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if product is None:
        return "Product not found!", 404

    if request.method == "POST":

        name = request.form.get("name")
        category = request.form.get("category")
        price = request.form.get("price")
        quantity = request.form.get("quantity")
        min_stock = request.form.get("min_stock")
        description = request.form.get("description")

        db.execute(
            """
            UPDATE products
            SET name = ?,
                category = ?,
                price = ?,
                quantity = ?,
                min_stock = ?,
                description = ?
            WHERE id = ?
            """,
            (
                name, category, price, quantity,
                min_stock, description, product_id
            )
        )

        db.commit()

        flash("Product updated successfully!", "success")

        return redirect(url_for("products.view_products"))

    return render_template(
        "edit_product.html",
        product=product
    )

@products.route("/manager/products/delete/<int:product_id>", methods=["POST"])
def delete_product(product_id):

    if "user_id" not in session:
        return redirect(url_for("auth.manager_login"))

    if session.get("user_role") != "manager":
        return "Access denied!", 403

    db = get_db()

    db.execute(
        "DELETE FROM products WHERE id = ?",
        (product_id,)
    )

    db.commit()

    flash("Product deleted successfully!", "success")

    return redirect(url_for("products.view_products"))

@products.route("/manager/inventory")
def inventory():

    if "user_id" not in session:
        return redirect(url_for("auth.manager_login"))

    if session.get("user_role") != "manager":
        return "Access denied!", 403

    db = get_db()

    all_products = db.execute(
        "SELECT * FROM products ORDER BY name ASC"
    ).fetchall()

    return render_template(
        "inventory.html",
        products=all_products
    )

@products.route("/manager/inventory/update/<int:product_id>", methods=["POST"])
def update_stock(product_id):

    if "user_id" not in session:
        return redirect(url_for("auth.manager_login"))

    if session.get("user_role") != "manager":
        return "Access denied!", 403

    quantity = request.form.get("quantity", type=int)

    if quantity is None or quantity < 0:
        flash("Please enter a valid quantity.", "error")
        return redirect(url_for("products.inventory"))

    db = get_db()

    db.execute(
        "UPDATE products SET quantity = ? WHERE id = ?",
        (quantity, product_id)
    )

    db.commit()

    flash("Stock updated successfully!", "success")

    return redirect(url_for("products.inventory"))