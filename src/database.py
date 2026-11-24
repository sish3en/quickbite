import sqlite3
from pathlib import Path

from flask import current_app, g
from werkzeug.security import generate_password_hash


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS menu_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    price REAL NOT NULL CHECK(price >= 0),
    image_url TEXT,
    available INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    total REAL NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    menu_item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    unit_price REAL NOT NULL,
    FOREIGN KEY(order_id) REFERENCES orders(id),
    FOREIGN KEY(menu_item_id) REFERENCES menu_items(id)
);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE_PATH"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        get_db().executescript(SCHEMA)
        get_db().commit()


def seed_database(app):
    with app.app_context():
        db = get_db()
        if db.execute("SELECT 1 FROM users WHERE username = ?", ("admin",)).fetchone() is None:
            db.execute(
                "INSERT INTO users(username, password_hash, is_admin) VALUES (?, ?, 1)",
                ("admin", generate_password_hash("admin123")),
            )
        if db.execute("SELECT COUNT(*) AS count FROM menu_items").fetchone()["count"] == 0:
            db.executemany(
                "INSERT INTO menu_items(name, description, category, price, image_url) VALUES (?, ?, ?, ?, ?)",
                [
                    ("Chicken Adobo", "Classic Filipino-style chicken dish.", "Main Course", 120.00, ""),
                    ("Beef Burger", "Juicy burger with lettuce and tomato.", "Main Course", 150.00, ""),
                    ("French Fries", "Crispy golden potato fries.", "Side Dish", 70.00, ""),
                    ("Chocolate Cake", "Moist chocolate cake slice.", "Dessert", 95.00, ""),
                ],
            )
        db.commit()
