
import sqlite3
from config import Config

db = sqlite3.connect(Config.DATABASE)

try:
    db.execute("PRAGMA foreign_keys = OFF")
    db.execute("BEGIN")

    db.execute("""
        CREATE TABLE reviews_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL UNIQUE,
            customer_id INTEGER NOT NULL,
            rating REAL NOT NULL CHECK (
                rating >= 0.5 AND rating <= 5
                AND rating * 2 = CAST(rating * 2 AS INTEGER)
            ),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (customer_id) REFERENCES users(id)
        )
    """)

    db.execute("""
        INSERT INTO reviews_new (
            id, order_id, customer_id, rating, comment, created_at
        )
        SELECT id, order_id, customer_id, rating, comment, created_at
        FROM reviews
    """)

    db.execute("DROP TABLE reviews")
    db.execute("ALTER TABLE reviews_new RENAME TO reviews")

    db.commit()

    print("Reviews table updated successfully!")
    print("Ratings from 0.5 to 5 are now supported.")

except Exception:
    db.rollback()
    raise

finally:
    db.close()
