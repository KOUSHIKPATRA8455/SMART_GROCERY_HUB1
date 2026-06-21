from django.contrib import admin

from .models import Category, Brand, Product, ProductImage, Review, Wishlist, Coupon


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name", "sku", "category", "brand", "price", "discount_price",
        "stock_quantity", "is_active", "is_featured",
    )
    list_filter = ("category", "brand", "is_active", "is_featured")
    search_fields = ("name", "sku", "barcode")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]
    list_editable = ("price", "discount_price", "stock_quantity", "is_active")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "is_approved", "created_at")
    list_filter = ("is_approved", "rating")
    search_fields = ("product__name", "user__username")
    actions = ["approve_reviews", "unapprove_reviews"]

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    def unapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "added_at")
    search_fields = ("user__username", "product__name")


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        "code", "discount_type", "discount_value", "valid_from", "valid_until",
        "times_used", "usage_limit", "is_active",
    )
    list_filter = ("discount_type", "is_active")
    search_fields = ("code",)
