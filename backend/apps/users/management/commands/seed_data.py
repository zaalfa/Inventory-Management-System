from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.products.models import Category, Product

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed database with initial demo data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # Create users
        users = [
            {'email': 'admin@ims.com', 'name': 'Admin User', 'role': 'admin', 'password': 'Admin123!'},
            {'email': 'manager@ims.com', 'name': 'Manager User', 'role': 'manager', 'password': 'Manager123!'},
            {'email': 'cashier@ims.com', 'name': 'Cashier User', 'role': 'cashier', 'password': 'Cashier123!'},
        ]
        for u in users:
            if not User.objects.filter(email=u['email']).exists():
                User.objects.create_user(**u)
                self.stdout.write(f"  Created user: {u['email']}")

        # Create categories
        categories_data = ['Electronics', 'Beverages', 'Food & Snacks', 'Stationery', 'Household']
        categories = {}
        for name in categories_data:
            cat, created = Category.objects.get_or_create(name=name)
            categories[name] = cat
            if created:
                self.stdout.write(f'  Created category: {name}')

        # Create products
        products_data = [
            {'name': 'Laptop ASUS VivoBook', 'category': 'Electronics', 'price': 7500000, 'stock': 15, 'min_stock': 3},
            {'name': 'Mouse Wireless Logitech', 'category': 'Electronics', 'price': 250000, 'stock': 40, 'min_stock': 10},
            {'name': 'Keyboard Mechanical', 'category': 'Electronics', 'price': 450000, 'stock': 2, 'min_stock': 5},
            {'name': 'Aqua 600ml', 'category': 'Beverages', 'price': 4000, 'stock': 200, 'min_stock': 50},
            {'name': 'Teh Botol 350ml', 'category': 'Beverages', 'price': 5000, 'stock': 0, 'min_stock': 30},
            {'name': 'Indomie Goreng', 'category': 'Food & Snacks', 'price': 3500, 'stock': 150, 'min_stock': 50},
            {'name': 'Pulpen Pilot G2', 'category': 'Stationery', 'price': 12000, 'stock': 4, 'min_stock': 20},
            {'name': 'Buku Tulis Sidu 58 Lembar', 'category': 'Stationery', 'price': 8000, 'stock': 60, 'min_stock': 25},
            {'name': 'Sabun Lifebuoy 90g', 'category': 'Household', 'price': 6500, 'stock': 80, 'min_stock': 20},
            {'name': 'Shampoo Pantene 170ml', 'category': 'Household', 'price': 18000, 'stock': 3, 'min_stock': 10},
        ]
        for p in products_data:
            if not Product.objects.filter(name=p['name']).exists():
                Product.objects.create(
                    name=p['name'],
                    category=categories[p['category']],
                    price=p['price'],
                    stock=p['stock'],
                    min_stock=p['min_stock'],
                )
                self.stdout.write(f"  Created product: {p['name']}")

        self.stdout.write(self.style.SUCCESS('\nSeed complete!'))
        self.stdout.write('\nDemo accounts:')
        self.stdout.write('  admin@ims.com    / Admin123!   (Admin)')
        self.stdout.write('  manager@ims.com  / Manager123! (Manager)')
        self.stdout.write('  cashier@ims.com  / Cashier123! (Cashier)')
