from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import Profile, Address

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        if password1 != password2:
            messages.error(request, _('Passwords do not match.'))
            return render(request, 'accounts/register.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, _('Username already exists.'))
            return render(request, 'accounts/register.html')
        if User.objects.filter(email=email).exists():
            messages.error(request, _('Email already registered.'))
            return render(request, 'accounts/register.html')
        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        messages.success(request, _('Account created successfully!'))
        return redirect('core:home')
    return render(request, 'accounts/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, _('Welcome back, {}!').format(user.username))
            next_url = request.GET.get('next', 'core:home')
            return redirect(next_url)
        else:
            messages.error(request, _('Invalid username or password.'))
    return render(request, 'accounts/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.info(request, _('Logged out successfully.'))
    return redirect('core:home')

@login_required
def dashboard(request):
    from orders.models import Order
    from wishlist.models import Wishlist
    orders = Order.objects.filter(user=request.user)[:5]
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    addresses = Address.objects.filter(user=request.user)
    context = {
        'orders': orders,
        'wishlist': wishlist,
        'addresses': addresses,
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        profile = user.profile
        profile.phone = request.POST.get('phone', '')
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        profile.save()
        messages.success(request, _('Profile updated successfully!'))
        return redirect('accounts:profile')
    return render(request, 'accounts/profile.html')

@login_required
def add_address(request):
    if request.method == 'POST':
        address = Address.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name'),
            phone=request.POST.get('phone'),
            street=request.POST.get('street'),
            city=request.POST.get('city'),
            state=request.POST.get('state', ''),
            zip_code=request.POST.get('zip_code', ''),
            country=request.POST.get('country', 'Saudi Arabia'),
            address_type=request.POST.get('address_type', 'home'),
        )
        if request.POST.get('is_default'):
            Address.objects.filter(user=request.user).update(is_default=False)
            address.is_default = True
            address.save()
        messages.success(request, _('Address added successfully.'))
        return redirect('accounts:dashboard')
    return render(request, 'accounts/add_address.html')

@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, _('Address deleted.'))
    return redirect('accounts:dashboard')
