from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.translation import gettext as _
from .models import Category, Banner, Newsletter, ContactMessage
from products.models import Product
from reviews.models import Review

def home(request):
    banners = Banner.objects.filter(is_active=True)
    featured_products = Product.objects.filter(is_featured=True, status='active')[:8]
    best_sellers = Product.objects.filter(is_best_seller=True, status='active')[:8]
    flash_sales = Product.objects.filter(is_flash_sale=True, status='active')[:8]
    categories = Category.objects.filter(is_featured=True)[:6]
    latest_products = Product.objects.filter(status='active')[:8]
    reviews = Review.objects.filter(is_verified=True)[:6]

    context = {
        'banners': banners,
        'featured_products': featured_products,
        'best_sellers': best_sellers,
        'flash_sales': flash_sales,
        'categories': categories,
        'latest_products': latest_products,
        'reviews': reviews,
    }
    return render(request, 'index.html', context)

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message,
        )
        wa_text = f"New message from {name} ({email})%0A%0ASubject: {subject}%0A%0AMessage: {message}"
        wa_url = f"https://wa.me/966570904651?text={wa_text}"
        return JsonResponse({'status': 'success', 'message': _('Message sent successfully!'), 'whatsapp_url': wa_url})
    return render(request, 'contact.html')

@require_POST
def subscribe_newsletter(request):
    email = request.POST.get('email')
    if email:
        Newsletter.objects.get_or_create(email=email)
        return JsonResponse({'status': 'success', 'message': _('Subscribed successfully!')})
    return JsonResponse({'status': 'error', 'message': _('Invalid email')}, status=400)

def search_products(request):
    query = request.GET.get('q', '')
    products = Product.objects.filter(name__icontains=query, status='active')[:10]
    data = [{'id': p.id, 'name': p.name, 'price': str(p.discount_price or p.price), 'image': p.image.url} for p in products]
    return JsonResponse(data, safe=False)
