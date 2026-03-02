from django.core.management.base import BaseCommand
from products.models import Category

class Command(BaseCommand):
    help = 'Create default product categories'

    def handle(self, *args, **options):
        default_categories = [
            {
                'name': 'Electronics',
                'slug': 'electronics',
                'description': 'Electronic devices and accessories'
            },
            {
                'name': 'Fashion',
                'slug': 'fashion',
                'description': 'Clothing, shoes, and fashion accessories'
            },
            {
                'name': 'Food',
                'slug': 'food',
                'description': 'Food items and beverages'
            },
            {
                'name': 'Appliances (Rasan)',
                'slug': 'appliances-rasan',
                'description': 'Home appliances and kitchen equipment'
            },
            {
                'name': 'Clothing',
                'slug': 'clothing',
                'description': 'Fashion and apparel'
            },
            {
                'name': 'Home & Garden',
                'slug': 'home-garden',
                'description': 'Home improvement and garden supplies'
            },
            {
                'name': 'Books',
                'slug': 'books',
                'description': 'Books and educational materials'
            },
            {
                'name': 'Sports & Outdoors',
                'slug': 'sports-outdoors',
                'description': 'Sports equipment and outdoor gear'
            },
            {
                'name': 'Health & Beauty',
                'slug': 'health-beauty',
                'description': 'Health and beauty products'
            },
            {
                'name': 'Toys & Games',
                'slug': 'toys-games',
                'description': 'Toys and games for all ages'
            },
            {
                'name': 'Automotive',
                'slug': 'automotive',
                'description': 'Car parts and accessories'
            },
            {
                'name': 'Food & Beverages',
                'slug': 'food-beverages',
                'description': 'Food items and beverages'
            },
            {
                'name': 'Other',
                'slug': 'other',
                'description': 'Miscellaneous products'
            }
        ]

        created_count = 0
        for category_data in default_categories:
            category, created = Category.objects.get_or_create(
                slug=category_data['slug'],
                defaults=category_data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Category already exists: {category.name}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} new categories'))
