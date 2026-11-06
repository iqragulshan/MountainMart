from werkzeug.security import generate_password_hash
from app.database import get_db
from werkzeug.security import check_password_hash

def create_user(name, email, password, role):

    db = get_db()

    password_hash = generate_password_hash(password)

    db.execute(
        """
        INSERT INTO users (name, email, password_hash, role)
        VALUES (?, ?, ?, ?)
        """,
        (name, email, password_hash, role)
    )

    db.commit()

def verify_user(email, password, role):

    db = get_db()

    user = db.execute(
        "SELECT * FROM users WHERE email = ? AND role = ?",
        (email, role)
    ).fetchone()

    if user is None:
        return None

    if not check_password_hash(user["password_hash"], password):
        return None

    return user    