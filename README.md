# QuickBite: Food Ordering and Management System

QuickBite is a Flask-based food ordering application. Customers can browse a menu, search TheMealDB for meal information, add products to a cart, and place orders. Administrators can manage menu items and update order statuses.

## Features

- Customer registration and login
- Menu browsing and category filtering
- TheMealDB meal-search API integration
- Shopping cart and quantity updates
- Order placement and order history
- Administrator menu and order management
- SQLite database
- Input validation and API error handling
- MVC-style routes with repository classes

## Requirements

- Python 3.10 or newer
- Internet connection for the meal-search feature

## Installation

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` if configuration changes are needed. TheMealDB's educational test key is already the default.

## Run the application

```bash
python run.py
```

Open `http://127.0.0.1:5000` in a browser.

## Open the application on another device

Both devices must be connected to the same Wi-Fi network. Find the computer's local IPv4 address using `ipconfig` on Windows. If the address is `192.168.1.8`, open this address on the other device:

```text
http://192.168.1.8:5000
```

The Flask server listens on the local network through `0.0.0.0`. If Windows Firewall asks for permission, allow Python on private networks. Do not expose this development server directly to the public internet.

## Demo accounts

The application creates an administrator account on first startup:

- Username: `admin`
- Password: `admin123`

Change the password before deploying publicly.

## Testing

```bash
pytest
```

## Suggested Git workflow

Use focused feature branches such as `feature/menu`, `feature/api-search`, and `feature/orders`. Commit meaningful changes, open pull requests, merge tested branches, and tag the final release as `v1.0.0`.

## API

The application uses TheMealDB's search endpoint:

```text
https://www.themealdb.com/api/json/v1/1/search.php?s=<meal-name>
```

The API is used for meal discovery only. QuickBite's own database stores menu prices, availability, users, carts, and orders.
