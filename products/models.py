from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from ckeditor.fields import RichTextField
from core.models import Category
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

class Product(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('draft', 'Draft'),
        ('archived', 'Archived'),
    ]
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True)
    description = RichTextField(blank=True)
    short_description = models.TextField(blank=True, max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.IntegerField(default=0)
    sku = models.CharField(max_length=100, unique=True, blank=True)
    image = models.ImageField(upload_to='products/')
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(400, 400)],
        format='JPEG',
        options={'quality': 80}
    )
    is_featured = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    is_flash_sale = models.BooleanField(default=False)
    flash_sale_end = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.IntegerField(default=0)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    brand = models.CharField(max_length=200, blank=True)
    warranty = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            import random
            self.sku = f"SKU-{random.randint(10000, 99999)}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products:detail', args=[self.slug])

    @property
    def image_url(self):
        try:
            if self.image:
                return self.image.url
            return '/static/images/placeholder.svg'
        except Exception:
            return '/static/images/placeholder.svg'

    @property
    def thumbnail_url(self):
        try:
            if self.image:
                return self.image_thumbnail.url
            return '/static/images/placeholder.svg'
        except Exception:
            return '/static/images/placeholder.svg'

    def discount_percentage(self):
        if self.discount_price:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(200, 200)],
        format='JPEG',
        options={'quality': 80}
    )
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)

    @property
    def image_url(self):
        try:
            return self.image.url
        except ValueError:
            return '/static/images/placeholder.svg'

    @property
    def thumbnail_url(self):
        try:
            if self.image:
                return self.image_thumbnail.url
            return '/static/images/placeholder.svg'
        except Exception:
            return '/static/images/placeholder.svg'

    def __str__(self):
        return f"Image for {self.product.name}"

class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    key = models.CharField(max_length=200)
    value = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.key}: {self.value}"
