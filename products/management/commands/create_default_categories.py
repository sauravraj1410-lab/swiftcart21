from django.core.management.base import BaseCommand
from products.models import Category
import uuid

class Command(BaseCommand):
    help = 'Create default categories if they don\'t exist'

    def handle(self, *args, **options):
        # Create default categories
        categories = [
            {
                'name': 'Electronics',
                'slug': 'electronics',
                'description': 'Electronic devices and accessories'
            },
            {
                'name': 'Clothing',
                'slug': 'clothing', 
                'description': 'Clothing and fashion items'
            },
            {
                'name': 'Home & Garden',
                'slug': 'home-garden',
                'description': 'Home and garden products'
            },
            {
                'name': 'Books',
                'slug': 'books',
                'description': 'Books and educational materials'
            },
            {
                'name': 'General',
                'slug': 'general',
                'description': 'General products'
            }
        ]
        
        created_count = 0
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'id': uuid.uuid4(),
                    'name': cat_data['name'],
                    'description': cat_data['description']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created category: {category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Category already exists: {category.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} categories')
        )
