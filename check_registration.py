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

from accounts.models import User, EmailVerification
from django.utils import timezone

print("=== REGISTRATION SYSTEM TEST ===")

# Check if user was created
try:
    user = User.objects.get(email='user12345@example.com')
    print(f"✅ User found: {user.email}")
    print(f"✅ User ID: {user.id}")
    print(f"✅ User name: {user.first_name} {user.last_name}")
    print(f"✅ Email verified: {user.is_email_verified}")
    print(f"✅ User role: {user.role}")
    print(f"✅ Created at: {user.created_at}")
    
    # Check if email verification was created
    try:
        email_verification = EmailVerification.objects.filter(user=user).first()
        if email_verification:
            print(f"✅ Email verification found")
            print(f"✅ OTP token: {email_verification.token}")
            print(f"✅ Expires at: {email_verification.expires_at}")
            print(f"✅ Is verified: {email_verification.is_verified}")
            print(f"✅ Is expired: {email_verification.is_expired()}")
        else:
            print("❌ No email verification found")
    except Exception as e:
        print(f"❌ Error checking email verification: {e}")
        
except User.DoesNotExist:
    print("❌ User not found")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n=== ALL USERS ===")
for user in User.objects.all():
    print(f"- {user.email} ({user.first_name} {user.last_name}) - Verified: {user.is_email_verified}")

print("\n=== EMAIL VERIFICATIONS ===")
for ev in EmailVerification.objects.all():
    print(f"- {ev.user.email} - OTP: {ev.token} - Verified: {ev.is_verified} - Expired: {ev.is_expired()}")
