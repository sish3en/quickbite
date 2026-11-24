from .database import get_db


class MenuRepository:
    @staticmethod
    def all(category=None):
        db = get_db()
        if category:
            return db.execute(
                "SELECT * FROM menu_items WHERE available = 1 AND category = ? ORDER BY name",
                (category,),
            ).fetchall()
        return db.execute("SELECT * FROM menu_items WHERE available = 1 ORDER BY name").fetchall()

    @staticmethod
    def categories():
        return get_db().execute("SELECT DISTINCT category FROM menu_items ORDER BY category").fetchall()

    @staticmethod
    def get(item_id):
        return get_db().execute("SELECT * FROM menu_items WHERE id = ?", (item_id,)).fetchone()

    @staticmethod
    def create(name, description, category, price, image_url):
        db = get_db()
        db.execute(
            "INSERT INTO menu_items(name, description, category, price, image_url) VALUES (?, ?, ?, ?, ?)",
            (name, description, category, price, image_url),
        )
        db.commit()

    @staticmethod
    def delete(item_id):
        db = get_db()
        db.execute("UPDATE menu_items SET available = 0 WHERE id = ?", (item_id,))
        db.commit()


class OrderRepository:
    @staticmethod
    def create(user_id, cart):
        db = get_db()
        total = sum(item["price"] * quantity for item, quantity in cart.values())
        order = db.execute("INSERT INTO orders(user_id, total) VALUES (?, ?)", (user_id, total))
        order_id = order.lastrowid
        for item, quantity in cart.values():
            db.execute(
                "INSERT INTO order_items(order_id, menu_item_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                (order_id, item["id"], quantity, item["price"]),
            )
        db.commit()
        return order_id, total

    @staticmethod
    def for_user(user_id):
        return get_db().execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
        ).fetchall()

    @staticmethod
    def all():
        return get_db().execute(
            "SELECT orders.*, users.username FROM orders JOIN users ON users.id = orders.user_id ORDER BY created_at DESC"
        ).fetchall()

    @staticmethod
    def update_status(order_id, status):
        db = get_db()
        db.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        db.commit()
