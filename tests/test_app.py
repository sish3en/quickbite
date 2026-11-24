import pytest

from src import create_app


@pytest.fixture()
def app(tmp_path):
    return create_app({"TESTING": True, "SECRET_KEY": "test", "DATABASE_PATH": str(tmp_path / "test.db")})


@pytest.fixture()
def client(app):
    return app.test_client()


def login(client, username="admin", password="admin123"):
    return client.post("/login", data={"username": username, "password": password}, follow_redirects=True)


def test_homepage_displays_menu(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Chicken Adobo" in response.data


def test_registration_and_login(client):
    response = client.post("/register", data={"username": "customer", "password": "secret1"}, follow_redirects=True)
    assert b"Registration successful" in response.data
    response = login(client, "customer", "secret1")
    assert b"QuickBite Menu" in response.data


def test_add_to_cart_and_checkout_requires_login(client):
    response = client.post("/cart/add/1", follow_redirects=True)
    assert b"Chicken Adobo was added" in response.data
    response = client.post("/checkout", follow_redirects=True)
    assert b"Please log in first" in response.data


def test_admin_can_place_order_and_update_status(client):
    login(client)
    client.post("/cart/add/1")
    response = client.post("/checkout", follow_redirects=True)
    assert b"placed successfully" in response.data
    response = client.post("/admin/orders/1/status", data={"status": "Preparing"}, follow_redirects=True)
    assert b"Order status updated" in response.data
