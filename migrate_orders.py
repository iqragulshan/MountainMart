
from app import create_app
from app.database import get_db

app = create_app()

with app.app_context():
    db = get_db()

    columns = [
        row["name"]
        for row in db.execute("PRAGMA table_info(orders)").fetchall()
    ]

    if "phone" not in columns:
        db.execute("ALTER TABLE orders ADD COLUMN phone TEXT")

    if "delivery_address" not in columns:
        db.execute("ALTER TABLE orders ADD COLUMN delivery_address TEXT")

    if "payment_method" not in columns:
        db.execute(
        "ALTER TABLE orders ADD COLUMN payment_method TEXT DEFAULT 'Cash on Delivery'"
        )

    if "payment_status" not in columns:
        db.execute(
        "ALTER TABLE orders ADD COLUMN payment_status TEXT DEFAULT 'Pending'"
        )

    if "customer_name" not in columns:
        db.execute(
        "ALTER TABLE orders ADD COLUMN customer_name TEXT"
        )

    db.commit()

    print("Order database migration completed!")
    print([
        row["name"]
        for row in db.execute("PRAGMA table_info(orders)").fetchall()
    ])
