from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.utils.translation import gettext as _
from .models import Product
from core.models import Category
from reviews.models import Review
from reviews.forms import ReviewForm

def product_list(request):
    products = Product.objects.filter(status='active')
    categories = Category.objects.all()
    selected_category = request.GET.get('category')
    sort_by = request.GET.get('sort', '-created_at')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    search_query = request.GET.get('q', '')

    if selected_category:
        products = products.filter(category__slug=selected_category)
    if search_query:
        products = products.filter(name__icontains=search_query)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    sort_options = {
        '-created_at': _('Newest'),
        'created_at': _('Oldest'),
        'price': _('Price: Low to High'),
        '-price': _('Price: High to Low'),
        '-rating': _('Top Rated'),
        'name': _('Name: A-Z'),
    }
    if sort_by in sort_options:
        products = products.order_by(sort_by)

    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products_page = paginator.get_page(page)

    context = {
        'products': products_page,
        'categories': categories,
        'selected_category': selected_category,
        'sort_by': sort_by,
        'sort_options': sort_options,
        'search_query': search_query,
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, status='active')
    related_products = Product.objects.filter(category=product.category, status='active').exclude(id=product.id)[:4]
    reviews = Review.objects.filter(product=product, is_verified=True)
    review_form = ReviewForm()

    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'review_count': reviews.count(),
        'review_form': review_form,
    }
    return render(request, 'products/product_detail.html', context)
