from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import Order, OrderItem
from cart.models import Cart
from accounts.models import Address

@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    if cart.get_item_count() == 0:
        messages.warning(request, _('Your cart is empty.'))
        return redirect('cart:cart')
    addresses = Address.objects.filter(user=request.user)
    context = {
        'cart': cart,
        'addresses': addresses,
    }
    return render(request, 'checkout/checkout.html', context)

@login_required
def place_order(request):
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user)
        if cart.get_item_count() == 0:
            return redirect('cart:cart')
        address_id = request.POST.get('address')
        if address_id:
            address = get_object_or_404(Address, id=address_id, user=request.user)
        else:
            address = Address.objects.create(
                user=request.user,
                full_name=request.POST.get('full_name'),
                phone=request.POST.get('phone'),
                street=request.POST.get('street'),
                city=request.POST.get('city'),
                state=request.POST.get('state', ''),
                zip_code=request.POST.get('zip_code', ''),
            )
        subtotal = cart.get_subtotal()
        shipping_fee = Decimal('0') if subtotal > Decimal('200') else Decimal('29.99')
        tax_amount = subtotal * Decimal('0.15')
        total_price = subtotal + shipping_fee + tax_amount - cart.discount_amount
        order = Order.objects.create(
            user=request.user,
            subtotal=subtotal,
            shipping_fee=shipping_fee,
            tax_amount=tax_amount,
            discount_amount=cart.discount_amount,
            total_price=total_price,
            shipping_full_name=address.full_name,
            shipping_phone=address.phone,
            shipping_street=address.street,
            shipping_city=address.city,
            shipping_state=address.state,
            shipping_zip=address.zip_code,
            shipping_country=address.country,
            payment_method=request.POST.get('payment_method', 'credit_card'),
        )
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                product_price=item.product.discount_price or item.product.price,
                quantity=item.quantity,
                subtotal=item.get_total(),
            )
            product = item.product
            product.stock -= item.quantity
            product.save()
        cart.items.all().delete()
        cart.discount_amount = 0
        cart.coupon_code = None
        cart.save()
        messages.success(request, _('Order placed successfully! Order number: {}').format(order.order_number))
        return redirect('orders:detail', order_id=order.id)
    return redirect('cart:cart')

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.save()
        messages.success(request, _('Order cancelled successfully.'))
    else:
        messages.error(request, _('Order cannot be cancelled.'))
    return redirect('orders:detail', order_id=order.id)
