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

        image_file = request.files.get("image")
        image_path = None

        if image_file and image_file.filename:

            if not allowed_file(image_file.filename):
                flash("Only PNG, JPG, JPEG and WEBP images are allowed.", "error")
                return redirect(url_for("products.add_product"))

            filename = secure_filename(image_file.filename)

            upload_folder = os.path.join(
                current_app.static_folder, "uploads"
            )

            os.makedirs(upload_folder, exist_ok=True)

            image_file.save(os.path.join(upload_folder, filename))

            image_path = f"uploads/{filename}"

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

        image_file = request.files.get("image")
        image_path = product["image"]

        if image_file and image_file.filename:

            if not allowed_file(image_file.filename):
                flash("Only PNG, JPG, JPEG and WEBP images are allowed.", "error")
                return redirect(
                    url_for("products.edit_product", product_id=product_id)
             )

            filename = secure_filename(image_file.filename)

            upload_folder = os.path.join(
                current_app.static_folder, "uploads"
           )

            os.makedirs(upload_folder, exist_ok=True)

            image_file.save(os.path.join(upload_folder, filename))

            image_path = f"uploads/{filename}"
        
        db.execute(
            """
            UPDATE products
            SET name = ?,
                category = ?,
                price = ?,
                quantity = ?,
                min_stock = ?,
                description = ?,
                image = ?
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