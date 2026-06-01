from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['product', 'product_name', 'product_price', 'quantity', 'subtotal']
    extra = 0
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'status', 'payment_status', 'total_price', 'created_at']
    list_filter = ['status', 'payment_status', 'payment_method', 'created_at']
    list_editable = ['status', 'payment_status']
    search_fields = ['order_number', 'user__username', 'user__email']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Info', {'fields': ('order_number', 'user', 'status', 'payment_status')}),
        ('Pricing', {'fields': ('subtotal', 'shipping_fee', 'tax_amount', 'discount_amount', 'total_price')}),
        ('Shipping', {'fields': ('shipping_full_name', 'shipping_phone', 'shipping_street', 'shipping_city', 'shipping_state', 'shipping_zip', 'shipping_country')}),
        ('Payment', {'fields': ('payment_method', 'tracking_number', 'notes')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
