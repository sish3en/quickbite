from functools import wraps

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .database import get_db
from .repositories import MenuRepository, OrderRepository
from .services import MealApiService

main_bp = Blueprint("main", __name__)


def current_user():
    if "user_id" not in session:
        return None
    return get_db().execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if current_user() is None:
            flash("Please log in first.", "error")
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if user is None or not user["is_admin"]:
            flash("Administrator access is required.", "error")
            return redirect(url_for("main.index"))
        return view(*args, **kwargs)
    return wrapped


@main_bp.context_processor
def inject_user():
    return {"current_user": current_user(), "cart_count": sum(session.get("cart", {}).values())}


@main_bp.route("/")
def index():
    category = request.args.get("category", "")
    return render_template("index.html", items=MenuRepository.all(category), categories=MenuRepository.categories())


@main_bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if len(username) < 3 or len(password) < 6:
            flash("Username must have 3 characters and password must have 6 characters.", "error")
        else:
            try:
                db = get_db()
                db.execute("INSERT INTO users(username, password_hash) VALUES (?, ?)", (username, generate_password_hash(password)))
                db.commit()
                flash("Registration successful. You can now log in.", "success")
                return redirect(url_for("main.login"))
            except Exception:
                flash("That username is already in use.", "error")
    return render_template("register.html")


@main_bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        user = get_db().execute("SELECT * FROM users WHERE username = ?", (request.form.get("username", "").strip(),)).fetchone()
        if user and check_password_hash(user["password_hash"], request.form.get("password", "")):
            session.clear()
            session["user_id"] = user["id"]
            session["cart"] = {}
            return redirect(url_for("main.index"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@main_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.index"))


@main_bp.route("/search")
def search():
    query = request.args.get("q", "")
    meals, error = MealApiService(current_app.config["MEALDB_BASE_URL"], current_app.config["MEALDB_TIMEOUT"]).search(query)
    if error:
        flash(error, "error")
    return render_template("search.html", meals=meals, query=query)


@main_bp.post("/cart/add/<int:item_id>")
def add_to_cart(item_id):
    item = MenuRepository.get(item_id)
    if item is None or not item["available"]:
        flash("That menu item is unavailable.", "error")
        return redirect(url_for("main.index"))
    cart = session.setdefault("cart", {})
    key = str(item_id)
    cart[key] = cart.get(key, 0) + 1
    session.modified = True
    flash(f"{item['name']} was added to your cart.", "success")
    return redirect(request.referrer or url_for("main.index"))


@main_bp.route("/cart", methods=("GET", "POST"))
def cart():
    cart_data = session.get("cart", {})
    if request.method == "POST":
        for key, value in request.form.items():
            if key.startswith("quantity_"):
                try:
                    quantity = int(value)
                    if quantity <= 0:
                        cart_data.pop(key.replace("quantity_", ""), None)
                    else:
                        cart_data[key.replace("quantity_", "")] = min(quantity, 99)
                except ValueError:
                    flash("Quantity must be a whole number.", "error")
        session["cart"] = cart_data
        flash("Cart updated.", "success")
    items = []
    for item_id, quantity in cart_data.items():
        item = MenuRepository.get(int(item_id))
        if item:
            items.append((item, quantity))
    total = sum(item["price"] * quantity for item, quantity in items)
    return render_template("cart.html", items=items, total=total)


@main_bp.post("/checkout")
@login_required
def checkout():
    cart_data = session.get("cart", {})
    cart = {}
    for item_id, quantity in cart_data.items():
        item = MenuRepository.get(int(item_id))
        if item and item["available"]:
            cart[item_id] = (item, quantity)
    if not cart:
        flash("Your cart is empty.", "error")
        return redirect(url_for("main.cart"))
    order_id, total = OrderRepository.create(session["user_id"], cart)
    session["cart"] = {}
    flash(f"Order #{order_id} placed successfully. Total: ₱{total:.2f}", "success")
    return redirect(url_for("main.orders"))


@main_bp.get("/orders")
@login_required
def orders():
    return render_template("orders.html", orders=OrderRepository.for_user(session["user_id"]))


@main_bp.get("/admin")
@admin_required
def admin():
    return render_template("admin.html", items=MenuRepository.all(), orders=OrderRepository.all())


@main_bp.post("/admin/menu")
@admin_required
def add_menu_item():
    try:
        name = request.form.get("name", "").strip()
        price = float(request.form.get("price", "-1"))
        if not name or price < 0:
            raise ValueError
        MenuRepository.create(name, request.form.get("description", "").strip(), request.form.get("category", "Main Course").strip(), price, request.form.get("image_url", "").strip())
        flash("Menu item added.", "success")
    except ValueError:
        flash("Enter a valid name and non-negative price.", "error")
    return redirect(url_for("main.admin"))


@main_bp.post("/admin/menu/<int:item_id>/delete")
@admin_required
def delete_menu_item(item_id):
    MenuRepository.delete(item_id)
    flash("Menu item removed.", "success")
    return redirect(url_for("main.admin"))


@main_bp.post("/admin/orders/<int:order_id>/status")
@admin_required
def update_order_status(order_id):
    status = request.form.get("status", "")
    if status in {"Pending", "Preparing", "Ready", "Completed", "Cancelled"}:
        OrderRepository.update_status(order_id, status)
        flash("Order status updated.", "success")
    else:
        flash("Invalid order status.", "error")
    return redirect(url_for("main.admin"))
