from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.http import JsonResponse
from .models import Review
from .forms import ReviewForm
from products.models import Product

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            if Review.objects.filter(user=request.user, product=product).exists():
                messages.error(request, _('You have already reviewed this product.'))
                return redirect('products:detail', slug=product.slug)
            review.save()
            reviews = Review.objects.filter(product=product)
            avg_rating = sum(r.rating for r in reviews) / reviews.count()
            product.rating = round(avg_rating, 2)
            product.review_count = reviews.count()
            product.save()
            messages.success(request, _('Review added successfully!'))
            return redirect('products:detail', slug=product.slug)
    return redirect('products:detail', slug=product.slug)

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product = review.product
    review.delete()
    reviews = Review.objects.filter(product=product)
    if reviews:
        avg_rating = sum(r.rating for r in reviews) / reviews.count()
        product.rating = round(avg_rating, 2)
    else:
        product.rating = 0
    product.review_count = reviews.count()
    product.save()
    messages.success(request, _('Review deleted.'))
    return redirect('products:detail', slug=product.slug)
