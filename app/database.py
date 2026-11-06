import os
import sqlite3
from flask import current_app, g


def get_db():
    if "db" not in g:

        os.makedirs(
            os.path.dirname(current_app.config["DATABASE"]),
            exist_ok=True
        )

        g.db = sqlite3.connect(
            current_app.config["DATABASE"]
        )

        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as file:
        db.executescript(file.read().decode("utf8"))

    db.commit()