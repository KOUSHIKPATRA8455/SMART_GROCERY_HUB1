# Smart Grocery Hub

A Django-based grocery store management system — final-year project, Module 1 (Customer Panel core flow).

This is **Phase 1** of the full Smart Grocery Hub spec: a complete, working
e-commerce core (catalog, cart, checkout, orders, accounts) built on Django +
Bootstrap 5. It's designed to be extended module-by-module (Inventory, POS,
Delivery, CRM, Reports, AI features, Multi-Store) rather than faked all at
once — see [`ROADMAP.md`](ROADMAP.md) for what's next.

## What's included in this phase

- **Accounts**: registration, login/logout, forgot password (email-based reset),
  profile editing with avatar upload, multiple saved addresses
- **Catalog**: categories, brands, products with images, search, category
  filter, sorting, pagination
- **Product detail**: ratings & reviews (one review per user per product),
  wishlist, related products
- **Cart**: add / update / remove, stock-aware quantities
- **Checkout**: address selection, COD or "online" (gateway integration is a
  later module), coupon codes, GST + delivery charge calculation
- **Orders**: order placement (atomic stock deduction), order history, order
  detail with a status tracker, cancel, reorder
- **Admin panel**: Django admin wired up for every model, with inline editing
  for product images, cart items, and order items
- **Demo data seeder**: one command populates 11 categories and ~28 products
  across them

## Tech stack

- Django 5.0 (Python)
- MySQL in production / SQLite for instant local setup (toggle via `.env`)
- Bootstrap 5 + Font Awesome (CDN) for UI
- django-crispy-forms + crispy-bootstrap5 for form rendering
- Pillow for image handling
- django-environ for config

## Project structure

```
smart_grocery_hub/
├── apps/
│   ├── accounts/   # custom User model, Address, auth views
│   ├── store/      # Category, Brand, Product, Review, Wishlist, Coupon
│   ├── orders/     # Cart, CartItem, Order, OrderItem, Payment
│   └── core/       # shared utilities, demo data seeder
├── config/         # settings, root urls, wsgi/asgi
├── templates/      # base.html (shared layout)
├── static/css/     # theme.css (brand identity)
├── media/          # user-uploaded files (product images, avatars)
├── requirements.txt
└── .env.example
```

## Setup (local development)

> **Note:** this project was hand-written file-by-file in an offline sandbox
> with no network access, so it could not be run through `pip install` or
> `manage.py runserver` before being handed to you. Every file has been
> manually reviewed for syntax and Django-5.0 API correctness, but **please
> run through this setup yourself and tell me about anything that breaks** —
> I'll fix it immediately.

### 1. Clone/copy the project, then create a virtual environment

```bash
cd smart_grocery_hub
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

If `mysqlclient` fails to build (common on Windows/Mac without MySQL dev
headers installed), you can skip it for now — the project defaults to SQLite
and only needs `mysqlclient` once you switch `DB_ENGINE=mysql` in `.env`.
Remove that one line from `requirements.txt` and reinstall if it blocks you.

### 3. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and set a real `SECRET_KEY` (any long random string works for
development — generate one with:
`python -c "import secrets; print(secrets.token_urlsafe(50))"`).

Leave `DB_ENGINE=sqlite` to start immediately with zero database setup.

### 4. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create an admin (superuser) account

```bash
python manage.py createsuperuser
```

### 6. Load demo data (optional but recommended for your demo/viva)

```bash
python manage.py seed_demo_data
```

This creates the 11 categories from the spec (Fruits, Vegetables, Dairy
Products, Rice, Pulses, Beverages, Snacks, Frozen Food, Bakery, Personal
Care, Household Items) and ~28 sample products spread across them.

### 7. Run the development server

```bash
python manage.py runserver
```

Visit:
- **Storefront**: http://127.0.0.1:8000/
- **Admin panel**: http://127.0.0.1:8000/admin/

### Switching to MySQL

1. Create a database: `CREATE DATABASE smart_grocery_hub CHARACTER SET utf8mb4;`
2. In `.env`, set `DB_ENGINE=mysql` and fill in `DB_NAME`, `DB_USER`,
   `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
3. Re-run `python manage.py migrate`.

## Known limitations of this phase (by design)

- **Payments**: only Cash on Delivery is functional. The "Online Payment"
  option exists in the checkout UI and the `Payment` model/schema is in
  place, but Razorpay/Stripe integration is a separate module.
- **Inventory module**: stock is tracked as a single `stock_quantity` field
  on `Product`. Batch tracking, expiry dates, barcode scanning, and
  warehouse-level inventory come in the Inventory Management module.
- **POS, Delivery Management, CRM, Reports/Analytics, AI features,
  Multi-Store**: not yet built. See `ROADMAP.md`.
- **Email/SMS notifications**: password reset emails work (console backend
  in dev — they print to your terminal instead of actually sending, until
  you configure a real SMTP provider in `.env`). Order/marketing
  notifications aren't built yet.
- **select_for_update() on SQLite**: SQLite doesn't support row locking, so
  this is a silent no-op there. The concurrency protection in checkout
  becomes meaningful once you switch to MySQL.

## If something doesn't run

Since this couldn't be tested in a live Django environment before delivery,
if you hit an error:

1. Copy the exact traceback.
2. Tell me which step in this README you were on.

I'll fix the specific file immediately rather than you having to debug
Django internals yourself.
