"""
Management command to populate the database with realistic demo data:
categories, brands, and products covering all the grocery categories from
the spec. Useful for screenshots, the project demo, and viva.

Usage:
    python manage.py seed_demo_data
"""

from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.store.models import Category, Brand, Product


CATEGORIES = [
    "Fruits", "Vegetables", "Dairy Products", "Rice", "Pulses",
    "Beverages", "Snacks", "Frozen Food", "Bakery", "Personal Care",
    "Household Items",
]

BRANDS = ["Amul", "Tata", "Nestle", "ITC", "Britannia", "Patanjali", "Generic"]

# (name, category, unit, unit_value, price, discount_price, gst, stock)
PRODUCTS = [
    ("Fresh Bananas (Dozen)", "Fruits", "dozen", 1, 60, 50, 0, 120),
    ("Royal Gala Apples", "Fruits", "kg", 1, 220, 199, 0, 80),
    ("Alphonso Mangoes", "Fruits", "kg", 1, 450, None, 0, 30),
    ("Fresh Tomatoes", "Vegetables", "kg", 1, 40, None, 0, 150),
    ("Onions", "Vegetables", "kg", 1, 35, None, 0, 200),
    ("Potatoes", "Vegetables", "kg", 1, 30, None, 0, 200),
    ("Amul Toned Milk", "Dairy Products", "l", 1, 58, None, 5, 100),
    ("Amul Butter", "Dairy Products", "g", 500, 270, 250, 12, 60),
    ("Amul Paneer", "Dairy Products", "g", 200, 90, None, 5, 70),
    ("India Gate Basmati Rice", "Rice", "kg", 5, 650, 599, 5, 40),
    ("Sona Masoori Rice", "Rice", "kg", 10, 750, None, 5, 35),
    ("Toor Dal", "Pulses", "kg", 1, 160, 145, 5, 90),
    ("Chana Dal", "Pulses", "kg", 1, 130, None, 5, 90),
    ("Moong Dal", "Pulses", "kg", 1, 145, None, 5, 90),
    ("Tata Tea Gold", "Beverages", "g", 500, 280, 259, 5, 50),
    ("Nescafe Classic Coffee", "Beverages", "g", 100, 280, None, 12, 40),
    ("Real Mixed Fruit Juice", "Beverages", "l", 1, 120, 99, 12, 60),
    ("Lay's Classic Salted", "Snacks", "g", 52, 20, None, 12, 200),
    ("Britannia Good Day Cookies", "Snacks", "g", 200, 40, None, 18, 150),
    ("Haldiram's Bhujia", "Snacks", "g", 200, 60, 55, 12, 100),
    ("McCain Frozen Peas", "Frozen Food", "g", 500, 110, None, 5, 45),
    ("Frozen Mixed Vegetables", "Frozen Food", "g", 500, 95, None, 5, 45),
    ("Britannia Brown Bread", "Bakery", "g", 400, 55, None, 5, 60),
    ("Whole Wheat Bread", "Bakery", "g", 400, 45, None, 5, 60),
    ("Colgate Toothpaste", "Personal Care", "g", 150, 95, 89, 18, 80),
    ("Dove Soap", "Personal Care", "g", 100, 55, None, 18, 100),
    ("Vim Dishwash Liquid", "Household Items", "ml", 500, 150, 135, 18, 70),
    ("Harpic Toilet Cleaner", "Household Items", "ml", 500, 99, None, 18, 70),
]


class Command(BaseCommand):
    help = "Seed the database with demo categories, brands, and products."

    def handle(self, *args, **options):
        category_objs = {}
        for name in CATEGORIES:
            cat, created = Category.objects.get_or_create(name=name)
            category_objs[name] = cat
            if created:
                self.stdout.write(f"Created category: {name}")

        brand_objs = {}
        for name in BRANDS:
            brand, created = Brand.objects.get_or_create(name=name)
            brand_objs[name] = brand

        created_count = 0
        for idx, (name, cat_name, unit, unit_value, price, discount, gst, stock) in enumerate(PRODUCTS):
            sku = f"SGH-{idx + 1:04d}"
            product, created = Product.objects.get_or_create(
                sku=sku,
                defaults=dict(
                    name=name,
                    category=category_objs[cat_name],
                    brand=brand_objs.get("Generic"),
                    unit=unit,
                    unit_value=unit_value,
                    price=Decimal(str(price)),
                    discount_price=Decimal(str(discount)) if discount else None,
                    gst_percentage=Decimal(str(gst)),
                    stock_quantity=stock,
                    is_active=True,
                    is_featured=(idx % 5 == 0),
                    description=f"Premium quality {name.lower()}, sourced fresh for Smart Grocery Hub.",
                ),
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seed complete: {len(category_objs)} categories, {len(brand_objs)} brands, "
            f"{created_count} new products created."
        ))
