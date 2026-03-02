#!/usr/bin/env python
import os
import sys
import django

# Add the project path
sys.path.append('c:/Users/Saurav Kumar/OneDrive/Apps/dropdhip windwurf')

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dropshipping.settings')

# Setup Django
import django
from django.conf import settings
from django.contrib.auth import get_user_model

# Configure Django
django.setup()

# Test User model import
try:
    User = get_user_model()
    print(f"✅ User model imported successfully: {User}")
    print(f"✅ User model fields: {[f.name for f in User._meta.fields]}")
    print(f"✅ User manager: {User.objects}")
    print(f"✅ Required fields: {getattr(User, 'REQUIRED_FIELDS', 'None')}")
    
    # Test creating a user
    try:
        test_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        print(f"✅ Test data: {test_data}")
        
        # Test serializer
        from accounts.serializers import UserRegistrationSerializer
        serializer = UserRegistrationSerializer(data=test_data)
        
        print(f"✅ Serializer created: {serializer}")
        print(f"✅ Serializer valid: {serializer.is_valid()}")
        
        if serializer.is_valid():
            print("✅ Serializer validation passed")
            user = serializer.save()
            print(f"✅ User created: {user.email}")
        else:
            print(f"❌ Serializer errors: {serializer.errors}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        
except Exception as e:
    print(f"❌ Django setup error: {e}")
    import traceback
    print(f"Full traceback: {traceback.format_exc()}")
