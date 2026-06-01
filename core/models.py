from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(400, 400)],
        format='JPEG',
        options={'quality': 80}
    )
    description = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

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
        return self.name

class Banner(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='banners/')
    image_thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(1920, 800)],
        format='JPEG',
        options={'quality': 85}
    )
    link = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

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
        return self.title

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=200, default='HomeStore')
    tagline = models.CharField(max_length=300, blank=True)
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    favicon = models.ImageField(upload_to='site/', blank=True, null=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    facebook = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    about_us = RichTextField(blank=True)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=15)

    class Meta:
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name

class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email

class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"
