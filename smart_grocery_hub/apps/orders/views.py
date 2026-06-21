"""
Views for the orders app: cart management and the checkout -> order
placement flow.

Stock deduction and order-total calculation happen inside a single
transaction in `place_order_view` so a crash mid-checkout can never leave
stock decremented without a corresponding order (or vice versa).
"""

from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from apps.accounts.models import Address
from apps.store.models import Product, Coupon

from .models import Cart, CartItem, Order, OrderItem


@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related("product").all()
    return render(request, "orders/cart.html", {"cart": cart, "items": items})


@login_required
@require_POST
def cart_add_view(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    try:
        quantity = int(request.POST.get("quantity") or 1)
    except ValueError:
        quantity = 1
    if quantity < 1:
        quantity = 1

    if product.stock_quantity < 1:
        messages.error(request, f"{product.name} is currently out of stock.")
        return redirect("store:product_detail", slug=slug)

    quantity = min(quantity, product.stock_quantity)

    item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={"quantity": quantity})
    if not created:
        item.quantity = min(item.quantity + quantity, product.stock_quantity)
        item.save()

    messages.success(request, f"Added {product.name} to cart.")
    next_url = request.POST.get("next")
    if next_url:
        return redirect(next_url)
    return redirect("orders:cart")


@login_required
@require_POST
def cart_update_view(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except ValueError:
        quantity = item.quantity

    if quantity < 1:
        item.delete()
        messages.info(request, "Item removed from cart.")
    else:
        item.quantity = min(quantity, item.product.stock_quantity) if item.product.stock_quantity > 0 else quantity
        item.save()
    return redirect("orders:cart")


@login_required
@require_POST
def cart_remove_view(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    item.delete()
    messages.info(request, "Item removed from cart.")
    return redirect("orders:cart")


@login_required
def checkout_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = list(cart.items.select_related("product").all())

    if not items:
        messages.warning(request, "Your cart is empty.")
        return redirect("orders:cart")

    addresses = request.user.addresses.all()
    subtotal = cart.subtotal

    if request.method == "POST":
        return _place_order(request, cart, items, subtotal)

    return render(
        request,
        "orders/checkout.html",
        {"items": items, "addresses": addresses, "subtotal": subtotal},
    )


def _place_order(request, cart, items, subtotal):
    address_id = request.POST.get("address_id")
    address = get_object_or_404(Address, pk=address_id, user=request.user)
    payment_method = request.POST.get("payment_method", Order.PaymentMethod.COD)
    coupon_code = request.POST.get("coupon_code", "").strip()

    discount_amount = Decimal("0.00")
    coupon = None
    if coupon_code:
        coupon = Coupon.objects.filter(code__iexact=coupon_code).first()
        if not coupon or not coupon.is_valid():
            messages.error(request, "Invalid or expired coupon code.")
            return redirect("orders:checkout")
        if subtotal < coupon.min_order_value:
            messages.error(request, f"Minimum order value for this coupon is ₹{coupon.min_order_value}.")
            return redirect("orders:checkout")

        if coupon.discount_type == Coupon.DiscountType.PERCENTAGE:
            discount_amount = subtotal * (coupon.discount_value / Decimal("100"))
            if coupon.max_discount_amount:
                discount_amount = min(discount_amount, coupon.max_discount_amount)
        else:
            discount_amount = coupon.discount_value

    delivery_charge = Decimal("0.00") if subtotal >= Decimal("499") else Decimal("40.00")
    tax_amount = sum(
        (item.product.display_price * item.quantity * item.product.gst_percentage / Decimal("100")
         for item in items),
        Decimal("0.00"),
    )
    total_amount = subtotal - discount_amount + delivery_charge + tax_amount

    try:
        with transaction.atomic():
            # Lock product rows to prevent overselling under concurrent checkouts.
            for item in items:
                locked_product = Product.objects.select_for_update().get(pk=item.product_id)
                if locked_product.stock_quantity < item.quantity:
                    raise ValueError(f"Not enough stock for {locked_product.name}.")

            order = Order.objects.create(
                user=request.user,
                shipping_full_name=address.full_name,
                shipping_phone_number=address.phone_number,
                shipping_address_line1=address.address_line1,
                shipping_address_line2=address.address_line2,
                shipping_city=address.city,
                shipping_state=address.state,
                shipping_pincode=address.pincode,
                shipping_country=address.country,
                subtotal=subtotal,
                discount_amount=discount_amount,
                delivery_charge=delivery_charge,
                tax_amount=tax_amount,
                total_amount=total_amount,
                coupon=coupon,
                payment_method=payment_method,
                status=Order.Status.PENDING,
            )

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    unit_price=item.product.display_price,
                    quantity=item.quantity,
                )
                Product.objects.filter(pk=item.product_id).update(
                    stock_quantity=F("stock_quantity") - item.quantity
                )

            if coupon:
                Coupon.objects.filter(pk=coupon.pk).update(times_used=F("times_used") + 1)

            cart.items.all().delete()

    except ValueError as exc:
        messages.error(request, str(exc))
        return redirect("orders:cart")

    messages.success(request, f"Order {order.order_number} placed successfully!")
    return redirect("orders:order_detail", order_number=order.order_number)


@login_required
def order_list_view(request):
    orders = request.user.orders.prefetch_related("items")
    return render(request, "orders/order_list.html", {"orders": orders})


@login_required
def order_detail_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    # Linear progress steps for the visual tracker. Cancelled/returned
    # orders are excluded from this view in the template since they
    # don't fit a forward-moving progress bar.
    step_order = [
        Order.Status.PENDING,
        Order.Status.CONFIRMED,
        Order.Status.PACKED,
        Order.Status.SHIPPED,
        Order.Status.OUT_FOR_DELIVERY,
        Order.Status.DELIVERED,
    ]
    status_labels = dict(Order.Status.choices)
    order_steps = [(i + 1, status_labels[status]) for i, status in enumerate(step_order)]
    current_step = step_order.index(order.status) + 1 if order.status in step_order else 0

    return render(
        request,
        "orders/order_detail.html",
        {"order": order, "order_steps": order_steps, "current_step": current_step},
    )


@login_required
@require_POST
def order_cancel_view(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    if order.can_be_cancelled:
        with transaction.atomic():
            order.status = Order.Status.CANCELLED
            order.save()
            for item in order.items.all():
                if item.product:
                    Product.objects.filter(pk=item.product_id).update(
                        stock_quantity=F("stock_quantity") + item.quantity
                    )
        messages.success(request, f"Order {order.order_number} cancelled.")
    else:
        messages.error(request, "This order can no longer be cancelled.")
    return redirect("orders:order_detail", order_number=order_number)


@login_required
@require_POST
def reorder_view(request, order_number):
    """Add all items from a past order back into the current cart."""
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    added, skipped = 0, 0
    for item in order.items.select_related("product"):
        if item.product and item.product.is_active and item.product.stock_quantity > 0:
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart, product=item.product, defaults={"quantity": item.quantity}
            )
            if not created:
                cart_item.quantity += item.quantity
                cart_item.save()
            added += 1
        else:
            skipped += 1

    if skipped:
        messages.warning(request, f"{skipped} item(s) from this order are no longer available.")
    messages.success(request, f"{added} item(s) added to your cart.")
    return redirect("orders:cart")
