def cart_count(request):
    if request.user.is_authenticated:
        from .models import Cart
        cart = Cart.objects.filter(user=request.user).first()
        count = cart.get_item_count() if cart else 0
    else:
        count = 0
    return {'cart_item_count': count}
