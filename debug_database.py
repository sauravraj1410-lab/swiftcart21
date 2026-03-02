#!/usr/bin/env python
import os
import sys
import django

# Add the project path
sys.path.append('c:/Users/Saurav Kumar/OneDrive/Apps/dropdhip windwurf')

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dropshipping.settings')

# Setup Django
django.setup()

from django.conf import settings
from decouple import config

print("=== DATABASE DEBUG ===")
print(f"DB_ENGINE from .env: {config('DB_ENGINE', default='NOT_SET')}")
print(f"RAW_DB_ENGINE: {settings.RAW_DB_ENGINE if hasattr(settings, 'RAW_DB_ENGINE') else 'NOT_FOUND'}")
print(f"DB_ENGINE_ALIASES: {settings.DB_ENGINE_ALIASES if hasattr(settings, 'DB_ENGINE_ALIASES') else 'NOT_FOUND'}")
print(f"DB_ENGINE: {settings.DB_ENGINE if hasattr(settings, 'DB_ENGINE') else 'NOT_FOUND'}")
print(f"DATABASES: {settings.DATABASES}")

# Test database connection
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("✅ Database connection successful")
except Exception as e:
    print(f"❌ Database connection failed: {e}")

# Check if we can access User model
try:
    from accounts.models import User
    user_count = User.objects.count()
    print(f"✅ User model accessible, count: {user_count}")
except Exception as e:
    print(f"❌ User model error: {e}")
