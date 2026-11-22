
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.database import get_db

suppliers = Blueprint("suppliers", __name__)


def manager_required():
    if not session.get("manager"):
        return redirect(url_for("auth.manager_login"))

    return None


@suppliers.route("/manager/suppliers")
def view_suppliers():

    access = manager_required()
    if access:
        return access

    db = get_db()

    all_suppliers = db.execute(
        "SELECT * FROM suppliers ORDER BY supplier_name ASC"
    ).fetchall()

    return render_template(
        "suppliers.html",
        suppliers=all_suppliers
    )


@suppliers.route("/manager/suppliers/add", methods=["GET", "POST"])
def add_supplier():

    access = manager_required()
    if access:
        return access

    if request.method == "POST":

        name = request.form.get("supplier_name", "").strip()
        contact = request.form.get("contact_person", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()

        if not name or not phone:
            flash("Supplier name and phone are required.", "error")
            return redirect(url_for("suppliers.add_supplier"))

        if len(name) > 100 or len(phone) > 20:
            flash("Please check the length of your details.", "error")
            return redirect(url_for("suppliers.add_supplier"))

        db = get_db()

        db.execute(
            """
            INSERT INTO suppliers
            (supplier_name, contact_person, phone, email, address)
            VALUES (?, ?, ?, ?, ?)
            """,
            (name, contact, phone, email, address)
        )

        db.commit()

        flash("Supplier added successfully!", "success")
        return redirect(url_for("suppliers.view_suppliers"))

    return render_template("add_supplier.html")


@suppliers.route("/manager/suppliers/edit/<int:supplier_id>", methods=["GET", "POST"])
def edit_supplier(supplier_id):

    access = manager_required()
    if access:
        return access

    db = get_db()

    supplier = db.execute(
        "SELECT * FROM suppliers WHERE id = ?",
        (supplier_id,)
    ).fetchone()

    if supplier is None:
        flash("Supplier not found.", "error")
        return redirect(url_for("suppliers.view_suppliers"))

    if request.method == "POST":

        name = request.form.get("supplier_name", "").strip()
        contact = request.form.get("contact_person", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()

        if not name or not phone or len(name) > 100 or len(phone) > 20:
            flash("Please enter valid supplier details.", "error")
            return redirect(url_for("suppliers.edit_supplier", supplier_id=supplier_id))

        db.execute(
            """
            UPDATE suppliers
            SET supplier_name = ?, contact_person = ?,
                phone = ?, email = ?, address = ?
            WHERE id = ?
            """,
            (name, contact, phone, email, address, supplier_id)
        )

        db.commit()

        flash("Supplier updated successfully!", "success")
        return redirect(url_for("suppliers.view_suppliers"))

    return render_template("edit_supplier.html", supplier=supplier)


@suppliers.route("/manager/suppliers/delete/<int:supplier_id>", methods=["POST"])
def delete_supplier(supplier_id):

    access = manager_required()
    if access:
        return access

    db = get_db()

    db.execute(
        "DELETE FROM suppliers WHERE id = ?",
        (supplier_id,)
    )

    db.commit()

    flash("Supplier deleted successfully!", "success")
    return redirect(url_for("suppliers.view_suppliers"))
