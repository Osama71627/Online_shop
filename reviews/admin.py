from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'is_verified', 'created_at']
    list_filter = ['rating', 'is_verified']
    list_editable = ['is_verified']
    search_fields = ['user__username', 'product__name', 'comment']
