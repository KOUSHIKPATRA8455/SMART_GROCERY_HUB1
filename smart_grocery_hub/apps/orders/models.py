"""
Models for the orders app: shopping cart, order placement, and payment
records. Kept separate from `store` because cart/order logic (totals,
stock deduction, status transitions) is business logic distinct from the
catalog itself.
"""

from decimal import Decimal

from django.conf import settings
from django.db import models

from apps.store.models import Product, Coupon
from apps.accounts.models import Address


class Cart(models.Model):
    """One active cart per logged-in user."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum((item.line_total for item in self.items.all()), Decimal("0.00"))


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["cart", "product"]

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def line_total(self):
        return self.product.display_price * self.quantity


class Order(models.Model):
    """A placed order. Snapshots address/price data at the time of
    placement so later edits to a Product or Address don't silently
    rewrite order history."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PACKED = "packed", "Packed"
        SHIPPED = "shipped", "Shipped"
        OUT_FOR_DELIVERY = "out_for_delivery", "Out for Delivery"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"
        RETURNED = "returned", "Returned"

    class PaymentMethod(models.TextChoices):
        COD = "cod", "Cash on Delivery"
        ONLINE = "online", "Online Payment"

    order_number = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")

    # Address snapshot (not a FK to Address, so editing/deleting a saved
    # address later never changes a past order's shipping details).
    shipping_full_name = models.CharField(max_length=150)
    shipping_phone_number = models.CharField(max_length=16)
    shipping_address_line1 = models.CharField(max_length=255)
    shipping_address_line2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_pincode = models.CharField(max_length=10)
    shipping_country = models.CharField(max_length=100, default="India")

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.CharField(max_length=10, choices=PaymentMethod.choices, default=PaymentMethod.COD)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    placed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-placed_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["order_number"]),
        ]

    def __str__(self):
        return self.order_number

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_order_number():
        import random
        from django.utils import timezone
        timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        suffix = random.randint(100, 999)
        return f"SGH{timestamp}{suffix}"

    @property
    def can_be_cancelled(self):
        return self.status in (self.Status.PENDING, self.Status.CONFIRMED)


class OrderItem(models.Model):
    """Snapshot of a single product line within an order, including the
    price at time of purchase (so price changes don't rewrite history)."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)  # snapshot, survives product deletion
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"


class Payment(models.Model):
    """Payment record for an order. Gateway integration (Razorpay/Stripe)
    is a later module; this model is the stable schema that integration
    will write into."""

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=Order.PaymentMethod.choices)
    status = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.order.order_number} - {self.status}"
