"""
Views for the store app: home page, product listing/search/filter,
product detail with reviews, and wishlist.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .models import Category, Product, Review, Wishlist
from .forms import ReviewForm


def home_view(request):
    categories = Category.objects.filter(is_active=True)[:8]
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    new_arrivals = Product.objects.filter(is_active=True).order_by("-created_at")[:8]
    return render(
        request,
        "store/home.html",
        {
            "categories": categories,
            "featured_products": featured_products,
            "new_arrivals": new_arrivals,
        },
    )


def shop_view(request):
    """Main product listing page with search, category filter, sorting,
    and pagination."""
    products = Product.objects.filter(is_active=True).select_related("category", "brand")

    query = request.GET.get("q", "").strip()
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    category_slug = request.GET.get("category")
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    sort = request.GET.get("sort", "")
    sort_map = {
        "price_low": "price",
        "price_high": "-price",
        "newest": "-created_at",
        "name": "name",
    }
    if sort in sort_map:
        products = products.order_by(sort_map[sort])

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    categories = Category.objects.filter(is_active=True)

    return render(
        request,
        "store/shop.html",
        {
            "page_obj": page_obj,
            "categories": categories,
            "selected_category": selected_category,
            "query": query,
            "sort": sort,
        },
    )


def category_detail_view(request, slug):
    """Convenience redirect-style view: reuses shop_view's template via
    its own render so URLs like /category/fruits/ are friendly and
    bookmarkable."""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(is_active=True, category=category)

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    categories = Category.objects.filter(is_active=True)

    return render(
        request,
        "store/shop.html",
        {
            "page_obj": page_obj,
            "categories": categories,
            "selected_category": category,
            "query": "",
            "sort": "",
        },
    )


def product_detail_view(request, slug):
    product = get_object_or_404(Product.objects.select_related("category", "brand"), slug=slug, is_active=True)
    reviews = product.reviews.filter(is_approved=True).select_related("user")
    related_products = Product.objects.filter(
        category=product.category, is_active=True
    ).exclude(pk=product.pk)[:4]

    user_has_reviewed = False
    review_form = None
    if request.user.is_authenticated:
        user_has_reviewed = Review.objects.filter(product=product, user=request.user).exists()
        if not user_has_reviewed:
            review_form = ReviewForm()

    is_wishlisted = (
        request.user.is_authenticated
        and Wishlist.objects.filter(user=request.user, product=product).exists()
    )

    return render(
        request,
        "store/product_detail.html",
        {
            "product": product,
            "reviews": reviews,
            "related_products": related_products,
            "review_form": review_form,
            "user_has_reviewed": user_has_reviewed,
            "is_wishlisted": is_wishlisted,
        },
    )


@login_required
def add_review_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if request.method == "POST":
        if Review.objects.filter(product=product, user=request.user).exists():
            messages.warning(request, "You've already reviewed this product.")
        else:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.save()
                messages.success(request, "Thank you for your review!")
    return redirect("store:product_detail", slug=slug)


@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user).select_related("product")
    return render(request, "store/wishlist.html", {"items": items})


@login_required
def wishlist_toggle_view(request, slug):
    product = get_object_or_404(Product, slug=slug)
    item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        item.delete()
        messages.info(request, f"Removed {product.name} from wishlist.")
    else:
        messages.success(request, f"Added {product.name} to wishlist.")

    next_url = request.POST.get("next") or request.GET.get("next") or "store:product_detail"
    if next_url == "store:product_detail":
        return redirect("store:product_detail", slug=slug)
    return redirect(next_url)
