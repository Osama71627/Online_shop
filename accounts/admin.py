from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, Address

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False

class AddressInline(admin.TabularInline):
    model = Address
    extra = 1

class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline, AddressInline]
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'email_verified']

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'city', 'address_type', 'is_default']
    list_filter = ['address_type', 'is_default']
