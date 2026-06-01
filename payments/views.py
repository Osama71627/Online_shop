from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.http import JsonResponse
from django.conf import settings
from .models import Payment
from orders.models import Order

@login_required
def payment_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'payments/payment.html', {
        'order': order,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
    })

@login_required
def process_payment(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, user=request.user)
        payment_method = request.POST.get('payment_method')
        payment = Payment.objects.create(
            user=request.user,
            order=order,
            payment_method=payment_method,
            amount=order.total_price,
            transaction_id=f"TXN-{order.order_number}",
            status='completed',
        )
        order.payment_status = 'paid'
        if order.status == 'pending':
            order.status = 'confirmed'
        order.save()
        messages.success(request, _('Payment completed successfully!'))
        return redirect('orders:detail', order_id=order.id)
    return redirect('payments:payment', order_id=order_id)

@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'payments/success.html', {'order': order})

@login_required
def payment_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'payments/cancel.html', {'order': order})
