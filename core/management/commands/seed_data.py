from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Category, Banner, SiteSettings
from products.models import Product
from accounts.models import Profile

class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **kwargs):
        # Create superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@homestore.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Superuser created (admin/admin123)'))

        # Site settings
        if not SiteSettings.objects.exists():
            SiteSettings.objects.create(
                site_name='HomeStore',
                tagline='Your Premium Home Appliance Destination',
                email='info@homestore.com',
                phone='+966 55 123 4567',
                address='123 King Fahd Road, Riyadh, Saudi Arabia',
            )
            self.stdout.write(self.style.SUCCESS('Site settings created'))

        # Categories
        categories = [
            {'name': 'Kitchen Appliances', 'is_featured': True},
            {'name': 'Refrigerators & Freezers', 'is_featured': True},
            {'name': 'Washing Machines', 'is_featured': True},
            {'name': 'Air Conditioners', 'is_featured': True},
            {'name': 'Televisions & Entertainment', 'is_featured': True},
            {'name': 'Home Décor', 'is_featured': True},
            {'name': 'Cleaning Tools', 'is_featured': False},
            {'name': 'Lighting', 'is_featured': False},
        ]
        for cat_data in categories:
            Category.objects.get_or_create(name=cat_data['name'], defaults={'is_featured': cat_data['is_featured']})
        self.stdout.write(self.style.SUCCESS(f'{len(categories)} categories created'))

        # Sample Products
        products_data = [
            {'name': 'Smart Refrigerator 650L', 'category': 'Refrigerators & Freezers', 'price': 4599, 'discount_price': 3999, 'stock': 15, 'is_featured': True, 'is_best_seller': True, 'description': '<p>Smart refrigerator with large 650L capacity, energy efficient, and touch screen display.</p>', 'short_description': '650L Smart Refrigerator with energy saving technology'},
            {'name': 'Front Load Washer 12kg', 'category': 'Washing Machines', 'price': 3299, 'discount_price': 2799, 'stock': 20, 'is_featured': True, 'is_best_seller': True, 'description': '<p>12kg front load washing machine with steam cleaning and smart inverter motor.</p>', 'short_description': '12kg Front Load Washer with steam technology'},
            {'name': 'Inverter Split AC 24,000 BTU', 'category': 'Air Conditioners', 'price': 2899, 'discount_price': 2499, 'stock': 10, 'is_featured': True, 'is_best_seller': True, 'description': '<p>24,000 BTU inverter split AC with smart cooling and energy saving mode.</p>', 'short_description': '24,000 BTU Inverter AC with smart cooling'},
            {'name': '55" 4K Smart TV', 'category': 'Televisions & Entertainment', 'price': 3499, 'discount_price': 2999, 'stock': 8, 'is_featured': True, 'is_flash_sale': True, 'description': '<p>55-inch 4K Ultra HD Smart TV with HDR and built-in streaming apps.</p>', 'short_description': '55" 4K UHD Smart TV with HDR'},
            {'name': 'Professional Blender Set', 'category': 'Kitchen Appliances', 'price': 599, 'discount_price': 449, 'stock': 50, 'is_featured': True, 'description': '<p>Professional grade blender with 6 speeds, 2L capacity and multiple attachments.</p>', 'short_description': 'Professional blender with 6 speeds'},
            {'name': 'Stainless Steel Cookware Set', 'category': 'Kitchen Appliances', 'price': 1299, 'discount_price': 999, 'stock': 25, 'is_best_seller': True, 'description': '<p>Premium 10-piece stainless steel cookware set with tempered glass lids.</p>', 'short_description': '10-piece premium stainless steel cookware set'},
            {'name': 'Smart Vacuum Cleaner', 'category': 'Cleaning Tools', 'price': 1899, 'discount_price': 1499, 'stock': 12, 'is_featured': True, 'is_flash_sale': True, 'description': '<p>Robot vacuum cleaner with smart mapping, self-emptying, and app control.</p>', 'short_description': 'Smart robot vacuum with self-emptying feature'},
            {'name': 'Modern LED Chandelier', 'category': 'Lighting', 'price': 899, 'discount_price': 699, 'stock': 18, 'is_featured': True, 'description': '<p>Elegant modern LED chandelier with dimmable lights and remote control.</p>', 'short_description': 'Modern LED chandelier with remote control'},
            {'name': 'Stand Mixer 5L', 'category': 'Kitchen Appliances', 'price': 1499, 'stock': 30, 'is_best_seller': True, 'description': '<p>5L stand mixer with 10 speeds, stainless steel bowl, and multiple attachments.</p>', 'short_description': '5L stand mixer with 10 speeds'},
            {'name': 'Smart Coffee Machine', 'category': 'Kitchen Appliances', 'price': 2499, 'discount_price': 1999, 'stock': 0, 'is_featured': True, 'description': '<p>Automatic espresso machine with built-in grinder, milk frother, and touch display.</p>', 'short_description': 'Automatic espresso machine with grinder'},
        ]
        for pd in products_data:
            cat = Category.objects.get(name=pd['category'])
            Product.objects.get_or_create(
                name=pd['name'],
                defaults={
                    'category': cat,
                    'price': pd['price'],
                    'discount_price': pd.get('discount_price'),
                    'stock': pd['stock'],
                    'is_featured': pd.get('is_featured', False),
                    'is_best_seller': pd.get('is_best_seller', False),
                    'is_flash_sale': pd.get('is_flash_sale', False),
                    'description': pd['description'],
                    'short_description': pd['short_description'],
                    'rating': 4.5,
                    'review_count': 12,
                }
            )
        self.stdout.write(self.style.SUCCESS(f'{len(products_data)} products created'))
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
