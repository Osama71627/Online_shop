from django.contrib import admin
from .models import Product, ProductImage, ProductSpecification

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 3

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'discount_price', 'stock', 'status', 'is_featured', 'rating']
    list_filter = ['status', 'is_featured', 'is_best_seller', 'category']
    list_editable = ['price', 'discount_price', 'stock', 'status', 'is_featured']
    search_fields = ['name', 'sku', 'brand']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductSpecificationInline]
    fieldsets = (
        ('Basic Information', {'fields': ('category', 'name', 'slug', 'description', 'short_description')}),
        ('Pricing & Stock', {'fields': ('price', 'discount_price', 'stock', 'sku')}),
        ('Media', {'fields': ('image',)}),
        ('Status & Flags', {'fields': ('status', 'is_featured', 'is_best_seller', 'is_flash_sale', 'flash_sale_end')}),
        ('Additional Info', {'fields': ('brand', 'weight', 'warranty')}),
    )

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'is_primary']

@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = ['product', 'key', 'value']
