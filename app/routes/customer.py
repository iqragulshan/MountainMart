
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash
)

from app.database import get_db

from flask import make_response

customer = Blueprint("customer", __name__)


# CUSTOMER HOMEPAGE
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

    cart = session.get("cart", {})
    cart_count = sum(int(qty) for qty in cart.values())
    
    response = make_response(render_template(
        "customer_home.html",
        products=products,
        search=search,
        categories=categories,
        selected_category=selected_category,
        cart_count=cart_count
    ))

    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


# ADD PRODUCT TO CART
@customer.route(
    "/customer/cart/add/<int:product_id>",
    methods=["POST"]
)
def add_to_cart(product_id):

    db = get_db()

    search = request.form.get("search", "").strip()
    selected_category = request.form.get("category", "").strip()

    def return_to_products():
        return redirect(url_for(
            "customer.customer_home",
            search=search,
            category=selected_category,
            _anchor="products"
        ))

    product = db.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if product is None:
        flash("Product not found.", "error")
        return return_to_products()

    if product["quantity"] <= 0:
        flash("Sorry, this product is out of stock.", "error")
        return return_to_products()

    cart = session.get("cart", {})
    product_key = str(product_id)

    current_quantity = int(cart.get(product_key, 0))

    if current_quantity + 1 > product["quantity"]:
        flash("Available stock limit reached.", "error")
        return return_to_products()

    cart[product_key] = current_quantity + 1

    session["cart"] = cart
    session.modified = True

    flash("Product added to cart successfully!", "success")

    return return_to_products()


# VIEW SHOPPING CART
@customer.route("/customer/cart")
def view_cart():

    db = get_db()

    cart = session.get("cart", {})
    cart_items = []
    cart_total = 0

    for product_id, quantity in cart.items():

        product = db.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        ).fetchone()

        if product is None:
            continue

        subtotal = product["price"] * quantity

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal
        })

        cart_total += subtotal

    return render_template(
        "cart.html",
        cart_items=cart_items,
        cart_total=cart_total,
        cart_count=sum(cart.values())
    )


# UPDATE CART QUANTITY
@customer.route(
    "/customer/cart/update/<int:product_id>",
    methods=["POST"]
)
def update_cart(product_id):

    db = get_db()

    product = db.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    cart = session.get("cart", {})
    product_key = str(product_id)

    if product is None or product_key not in cart:
        flash("Product not found in cart.", "error")
        return redirect(url_for("customer.view_cart"))

    try:
        quantity = int(request.form.get("quantity", 1))
    except (ValueError, TypeError):
        flash("Invalid quantity.", "error")
        return redirect(url_for("customer.view_cart"))

    if quantity <= 0:
        cart.pop(product_key)

    elif quantity > product["quantity"]:
        flash("Requested quantity exceeds available stock.", "error")

    else:
        cart[product_key] = quantity

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("customer.view_cart"))


# REMOVE PRODUCT FROM CART
@customer.route(
    "/customer/cart/remove/<int:product_id>",
    methods=["POST"]
)
def remove_from_cart(product_id):

    cart = session.get("cart", {})

    cart.pop(str(product_id), None)

    session["cart"] = cart
    session.modified = True

    return redirect(url_for("customer.view_cart"))


# CHECKOUT PAGE
@customer.route("/customer/checkout", methods=["GET", "POST"])
def checkout():

    db = get_db()
    cart = session.get("cart", {})

    if not cart:
        flash("Your cart is empty.", "error")
        return redirect(url_for("customer.view_cart"))

    cart_items = []
    cart_total = 0

    for product_id, quantity in cart.items():

        product = db.execute(
            "SELECT * FROM products WHERE id = ?",
            (product_id,)
        ).fetchone()

        if product is None:
            continue

        quantity = int(quantity)

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": product["price"] * quantity
        })

        cart_total += product["price"] * quantity

    if not cart_items:
        flash("Your cart has no valid products.", "error")
        return redirect(url_for("customer.view_cart"))

    cart_count = sum(int(qty) for qty in cart.values())

    if request.method == "POST":

        customer_name = request.form.get("customer_name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        payment_method = request.form.get("payment_method", "").strip()

        if not customer_name or not phone or not address:
            flash("Please complete all delivery details.", "error")

        elif (
            len(customer_name) > 100
            or len(phone) > 20
            or len(address) > 500
        ):
            flash("Please check the length of your details.", "error")

        elif not phone.replace("+", "").replace("-", "").replace(" ", "").isdigit():
            flash("Please enter a valid phone number.", "error")

        elif payment_method not in [
            "Cash on Delivery",
            "Demo Online Payment"
        ]:
            flash("Please select a valid payment method.", "error")

        else:

            try:
                # Check stock again before placing the order.
                for item in cart_items:

                    latest_product = db.execute(
                        "SELECT quantity FROM products WHERE id = ?",
                        (item["product"]["id"],)
                    ).fetchone()

                    if (
                        latest_product is None
                        or latest_product["quantity"] < item["quantity"]
                    ):
                        raise ValueError(
                            f"Insufficient stock for {item['product']['name']}."
                        )

                customer_id = None

                if session.get("user_role") == "customer":
                    customer_id = session.get("user_id")

                # Create order
                cursor = db.execute(
                    """
                    INSERT INTO orders
                    (
                        customer_id,
                        total_amount,
                        status,
                        phone,
                        customer_name,
                        delivery_address,
                        payment_method,
                        payment_status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        customer_id,
                        cart_total,
                        "Pending",
                        phone,
                        customer_name,
                        address,
                        payment_method,
                        "Pending"
                    )
                )

                order_id = cursor.lastrowid

                # Save order items and reduce stock
                for item in cart_items:

                    product_id = item["product"]["id"]
                    quantity = item["quantity"]
                    price = item["product"]["price"]

                    db.execute(
                        """
                        INSERT INTO order_items
                        (order_id, product_id, quantity, price)
                        VALUES (?, ?, ?, ?)
                        """,
                        (order_id, product_id, quantity, price)
                    )

                    db.execute(
                        """
                        UPDATE products
                        SET quantity = quantity - ?
                        WHERE id = ? AND quantity >= ?
                        """,
                        (quantity, product_id, quantity)
                    )

                    if db.execute("SELECT changes()").fetchone()[0] != 1:
                        raise ValueError(
                            f"Stock changed for {item['product']['name']}."
                        )

                db.commit()

                session["cart"] = {}
                session.modified = True

                if payment_method == "Demo Online Payment":
                    return redirect(
                        url_for("orders.demo_payment", order_id=order_id)
                    )

                return redirect(
                    url_for("orders.order_success", order_id=order_id)
                )

            except ValueError as error:
                db.rollback()
                flash(str(error), "error")

            except Exception:
                db.rollback()
                flash(
                    "Something went wrong while placing your order. Please try again.",
                    "error"
                )

    # Display checkout page for GET and unsuccessful POST requests.
    return render_template(
        "checkout.html",
        cart_items=cart_items,
        cart_total=cart_total,
        cart_count=cart_count
    )
