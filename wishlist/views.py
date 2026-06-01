from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.translation import gettext as _
from .models import Wishlist, WishlistItem
from products.models import Product

@login_required
def wishlist_view(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    return render(request, 'wishlist/wishlist.html', {'wishlist': wishlist})

@login_required
@require_POST
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)
    if created:
        return JsonResponse({'status': 'added', 'message': _('Added to wishlist!')})
    else:
        item.delete()
        return JsonResponse({'status': 'removed', 'message': _('Removed from wishlist!')})

@login_required
@require_POST
def remove_from_wishlist(request, item_id):
    wishlist = get_object_or_404(Wishlist, user=request.user)
    item = get_object_or_404(WishlistItem, id=item_id, wishlist=wishlist)
    product_name = item.product.name
    item.delete()
    return JsonResponse({'status': 'success', 'message': _('{} removed from wishlist').format(product_name)})
