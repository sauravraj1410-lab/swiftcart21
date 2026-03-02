# Generated migration for seller category
from django.db import migrations

def create_seller_category(apps, schema_editor):
    """Create seller category"""
    from products.models import Category
    # Check if category already exists
    if not Category.objects.filter(name='Seller Products').exists():
        # Create the category
        Category.objects.create(name='Seller Products', slug='seller-products', is_active=True)
        print("Created 'Seller Products' category")

class Migration(migrations.Migration):
    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_seller_category,
            reverse_code=migrations.RunPython.noop
        ),
    ]
