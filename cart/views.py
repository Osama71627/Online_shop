from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.utils.translation import gettext as _
from .models import Cart, CartItem
from products.models import Product

@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/cart.html', {'cart': cart})

@login_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, status='active')
    cart, cart_created = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        item.quantity += 1
        item.save()
    return JsonResponse({
        'status': 'success',
        'message': _('{} added to cart').format(product.name),
        'cart_count': cart.get_item_count(),
        'cart_total': str(cart.get_total()),
    })

@login_required
@require_POST
def update_cart(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    quantity = int(request.POST.get('quantity', 1))
    if quantity > 0:
        item.quantity = quantity
        item.save()
    else:
        item.delete()
    return JsonResponse({
        'status': 'success',
        'cart_count': cart.get_item_count(),
        'cart_total': str(cart.get_total()),
        'item_total': str(item.get_total()) if quantity > 0 else '0',
    })

@login_required
@require_POST
def remove_from_cart(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    return JsonResponse({
        'status': 'success',
        'cart_count': cart.get_item_count(),
        'cart_total': str(cart.get_total()),
    })

@login_required
@require_GET
def cart_count(request):
    cart = Cart.objects.filter(user=request.user).first()
    count = cart.get_item_count() if cart else 0
    return JsonResponse({'count': count})
