"""
Context processor that makes the cart item count available in every
template (used for the navbar cart badge) without each view needing to
pass it explicitly.
"""

from .models import Cart


def cart_context(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return {"cart_item_count": cart.total_items}
    return {"cart_item_count": 0}
