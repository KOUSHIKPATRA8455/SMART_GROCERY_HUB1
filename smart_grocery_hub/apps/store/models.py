"""
Models for the store app: catalog (Category, Product, ProductImage),
shopping cart (Cart, CartItem), Wishlist, and product Reviews.
"""

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """Top-level product category, e.g. Fruits, Dairy Products, Snacks."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("store:category_detail", kwargs={"slug": self.slug})


class Brand(models.Model):
    """Product brand, e.g. Amul, Tata, Nestle."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    logo = models.ImageField(upload_to="brands/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """A purchasable product. `stock_quantity` is the single source of
    truth for availability in this module; a dedicated Inventory model
    with batch/expiry tracking is planned for the Inventory Management
    module and will wrap this field rather than replace it."""

    class Unit(models.TextChoices):
        KG = "kg", "Kilogram"
        GRAM = "g", "Gram"
        LITRE = "l", "Litre"
        ML = "ml", "Millilitre"
        PIECE = "pc", "Piece"
        PACK = "pack", "Pack"
        DOZEN = "dozen", "Dozen"

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name="products")

    description = models.TextField(blank=True)
    sku = models.CharField("SKU", max_length=50, unique=True)
    barcode = models.CharField(max_length=50, blank=True, db_index=True)

    unit = models.CharField(max_length=10, choices=Unit.choices, default=Unit.PIECE)
    unit_value = models.DecimalField(
        max_digits=8, decimal_places=2, default=1,
        help_text="e.g. 500 for '500 g', 1 for '1 piece'",
    )

    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Selling price (MRP)")
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Optional discounted price; leave blank if no discount",
    )
    gst_percentage = models.DecimalField(max_digits=4, decimal_places=2, default=0)

    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=10)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("store:product_detail", kwargs={"slug": self.slug})

    @property
    def display_price(self):
        """The price to charge: discount price if set and lower, else MRP."""
        if self.discount_price and self.discount_price < self.price:
            return self.discount_price
        return self.price

    @property
    def discount_percentage(self):
        if self.discount_price and self.discount_price < self.price and self.price > 0:
            return round((1 - (self.discount_price / self.price)) * 100)
        return 0

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0

    @property
    def is_low_stock(self):
        return 0 < self.stock_quantity <= self.low_stock_threshold

    @property
    def average_rating(self):
        agg = self.reviews.aggregate(models.Avg("rating"))
        return round(agg["rating__avg"] or 0, 1)

    @property
    def review_count(self):
        return self.reviews.count()


class ProductImage(models.Model):
    """Additional gallery images for a product (the first/primary image
    is shown on listing pages)."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    is_primary = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ["-is_primary", "id"]

    def __str__(self):
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(product=self.product, is_primary=True).exclude(
                pk=self.pk
            ).update(is_primary=False)
        super().save(*args, **kwargs)


class Review(models.Model):
    """A customer's rating + written review for a product."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()  # 1-5, validated in the form
    comment = models.TextField(blank=True)
    is_approved = models.BooleanField(default=True)  # admin moderation flag
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["product", "user"]  # one review per user per product

    def __str__(self):
        return f"{self.user.username} rated {self.product.name}: {self.rating}/5"


class Wishlist(models.Model):
    """Many-to-many through table: which users have wishlisted which products."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlisted_by")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["user", "product"]
        ordering = ["-added_at"]

    def __str__(self):
        return f"{self.user.username} -> {self.product.name}"


class Coupon(models.Model):
    """Discount coupon applied at checkout."""

    class DiscountType(models.TextChoices):
        PERCENTAGE = "percentage", "Percentage"
        FLAT = "flat", "Flat amount"

    code = models.CharField(max_length=30, unique=True)
    discount_type = models.CharField(max_length=12, choices=DiscountType.choices, default=DiscountType.PERCENTAGE)
    discount_value = models.DecimalField(max_digits=8, decimal_places=2)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(default=1, help_text="Max total uses across all customers")
    times_used = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active
            and self.valid_from <= now <= self.valid_until
            and self.times_used < self.usage_limit
        )
