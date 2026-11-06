from app import create_app
from app.database import get_db

app = create_app()

with app.app_context():
    db = get_db()

    products = db.execute(
        "SELECT * FROM products"
    ).fetchall()

    print("Products in database:")

    for product in products:
        print(dict(product))