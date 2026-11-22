
import os

from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash, current_app
)

from werkzeug.utils import secure_filename
from app.database import get_db

products = Blueprint("products", __name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


# MANAGER AUTHENTICATION
def manager_required():

    if not session.get("manager"):
        return redirect(url_for("auth.manager_login"))

    return None


def save_product_image(image_file):
    if not image_file or not image_file.filename:
        return None

    if not allowed_file(image_file.filename):
        return False

    filename = secure_filename(image_file.filename)

    upload_folder = os.path.join(
        current_app.static_folder, "uploads"
    )
    os.makedirs(upload_folder, exist_ok=True)

    image_file.save(os.path.join(upload_folder, filename))

    return f"uploads/{filename}"


@products.route("/manager/products/add", methods=["GET", "POST"])
def add_product():

    access_error = manager_required()
    if access_error:
        return access_error

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip().lower()
        price = request.form.get("price")
        quantity = request.form.get("quantity")
        min_stock = request.form.get("min_stock")
        description = request.form.get("description", "").strip()

        if not name or not category or price is None:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("products.add_product"))

        image_path = save_product_image(request.files.get("image"))

        if image_path is False:
            flash("Only PNG, JPG, JPEG and WEBP images are allowed.", "error")
            return redirect(url_for("products.add_product"))

        db = get_db()

        db.execute(
            """
            INSERT INTO products
            (name, category, price, quantity, min_stock, description, image)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, category, price, quantity, min_stock, description, image_path)
        )

        db.commit()

        flash("Product added successfully!", "success")
        return redirect(url_for("products.view_products"))

    return render_template("add_product.html")


@products.route("/manager/products")
def view_products():

    access_error = manager_required()
    if access_error:
        return access_error

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

    access_error = manager_required()
    if access_error:
        return access_error

    db = get_db()

    product = db.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if product is None:
        flash("Product not found.", "error")
        return redirect(url_for("products.view_products"))

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip().lower()
        price = request.form.get("price")
        quantity = request.form.get("quantity")
        min_stock = request.form.get("min_stock")
        description = request.form.get("description", "").strip()

        image_path = product["image"]

        new_image = save_product_image(request.files.get("image"))

        if new_image is False:
            flash("Only PNG, JPG, JPEG and WEBP images are allowed.", "error")
            return redirect(
                url_for("products.edit_product", product_id=product_id)
            )

        if new_image:
            image_path = new_image

        db.execute(
            """
            UPDATE products
            SET name = ?, category = ?, price = ?, quantity = ?,
                min_stock = ?, description = ?, image = ?
            WHERE id = ?
            """,
            (
                name, category, price, quantity,
                min_stock, description, image_path, product_id
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

    access_error = manager_required()
    if access_error:
        return access_error

    db = get_db()

    product = db.execute(
        "SELECT id FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if product is None:
        flash("Product not found.", "error")
    else:
        db.execute(
            "DELETE FROM products WHERE id = ?",
            (product_id,)
        )
        db.commit()
        flash("Product deleted successfully!", "success")

    return redirect(url_for("products.view_products"))


@products.route("/manager/inventory")
def inventory():

    access_error = manager_required()
    if access_error:
        return access_error

    db = get_db()

    all_products = db.execute(
        "SELECT * FROM products ORDER BY name COLLATE NOCASE"
    ).fetchall()

    return render_template(
        "inventory.html",
        products=all_products
    )


@products.route("/manager/inventory/update/<int:product_id>", methods=["POST"])
def update_stock(product_id):

    access_error = manager_required()
    if access_error:
        return access_error

    quantity = request.form.get("quantity", type=int)

    if quantity is None or quantity < 0:
        flash("Please enter a valid stock quantity.", "error")
        return redirect(url_for("products.inventory"))

    db = get_db()

    product = db.execute(
        "SELECT id FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if product is None:
        flash("Product not found.", "error")
    else:
        db.execute(
            "UPDATE products SET quantity = ? WHERE id = ?",
            (quantity, product_id)
        )
        db.commit()
        flash("Stock updated successfully!", "success")

    return redirect(url_for("products.inventory"))
