from app import create_app
from app.database import init_db, get_db

app = create_app()

with app.app_context():
    init_db()
    db = get_db()

    columns = db.execute("PRAGMA table_info(products)").fetchall()

    if "image" not in [column["name"] for column in columns]:
        db.execute("ALTER TABLE products ADD COLUMN image TEXT")
        db.commit()
        print("Image column added successfully!")
    else:
        print("Image column already exists!")
    print("Users table created successfully!")