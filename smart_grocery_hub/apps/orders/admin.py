from django.contrib import admin

from .models import Cart, CartItem, Order, OrderItem, Payment


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("product", "quantity")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "total_items", "subtotal", "updated_at")
    inlines = [CartItemInline]
    search_fields = ("user__username",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "product_name", "unit_price", "quantity", "line_total")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number", "user", "status", "payment_method",
        "total_amount", "placed_at",
    )
    list_filter = ("status", "payment_method", "placed_at")
    search_fields = ("order_number", "user__username", "shipping_phone_number")
    inlines = [OrderItemInline]
    readonly_fields = ("order_number", "subtotal", "total_amount", "placed_at")
    list_editable = ("status",)
    date_hierarchy = "placed_at"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("order", "amount", "method", "status", "transaction_id", "created_at")
    list_filter = ("status", "method")
    search_fields = ("order__order_number", "transaction_id")
