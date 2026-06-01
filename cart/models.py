from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from products.models import Product

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    coupon_code = models.CharField(max_length=50, blank=True, null=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Cart for {self.user.username}"

    def get_subtotal(self):
        return sum(item.get_total() for item in self.items.all())

    def get_tax(self):
        return self.get_subtotal() * Decimal('0.15')

    def get_discount(self):
        return self.discount_amount

    def get_total(self):
        return self.get_subtotal() + self.get_tax() - self.get_discount()

    def get_item_count(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'product']

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def price(self):
        return self.product.discount_price or self.product.price

    @property
    def subtotal(self):
        return self.price * self.quantity

    def get_total(self):
        return self.subtotal
