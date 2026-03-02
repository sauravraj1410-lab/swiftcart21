from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.db import models
from .models import Seller, SellerDocument, SellerPayout, SellerEarnings, SellerReview

class SellerSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = Seller
        fields = '__all__'
        read_only_fields = ('id', 'user', 'total_sales', 'total_orders', 'average_rating', 
                          'total_reviews', 'approved_at', 'approved_by', 'created_at', 'updated_at')

class SellerRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for seller registration"""
    user_first_name = serializers.CharField(write_only=True)
    user_last_name = serializers.CharField(write_only=True)
    user_email = serializers.EmailField(write_only=True)
    user_password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = Seller
        fields = ('business_name', 'business_description', 'business_type', 'business_email',
                 'business_phone', 'business_address', 'business_city', 'business_state',
                 'business_country', 'business_postal_code', 'user_first_name', 'user_last_name',
                 'user_email', 'user_password')
    
    def validate_user_email(self, value):
        from accounts.models import User
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError(_('A user with this email already exists.'))
        return value.lower()
    
    def create(self, validated_data):
        from accounts.models import User
        
        # Extract user data
        user_data = {
            'email': validated_data.pop('user_email'),
            'first_name': validated_data.pop('user_first_name'),
            'last_name': validated_data.pop('user_last_name'),
            'password': validated_data.pop('user_password'),
            'role': 'seller'
        }
        
        # Create user
        user = User.objects.create_user(**user_data)
        
        # Create seller
        seller = Seller.objects.create(user=user, **validated_data)
        
        return seller

class SellerDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerDocument
        fields = '__all__'
        read_only_fields = ('id', 'seller', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        validated_data['seller'] = self.context['request'].user.seller
        return super().create(validated_data)

class SellerPayoutSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.business_name', read_only=True)
    
    class Meta:
        model = SellerPayout
        fields = '__all__'
        read_only_fields = ('id', 'seller', 'status', 'processed_at', 'processed_by', 'created_at', 'updated_at')

class SellerEarningsSerializer(serializers.ModelSerializer):
    seller_name = serializers.CharField(source='seller.business_name', read_only=True)
    
    class Meta:
        model = SellerEarnings
        fields = '__all__'
        read_only_fields = ('id', 'seller', 'created_at', 'updated_at')

class SellerReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = SellerReview
        fields = '__all__'
        read_only_fields = ('id', 'user', 'is_verified_purchase', 'created_at', 'updated_at')
    
    def validate(self, attrs):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            seller = attrs.get('seller')
            if seller and SellerReview.objects.filter(seller=seller, user=request.user).exists():
                raise serializers.ValidationError(_('You have already reviewed this seller.'))
        return attrs

class SellerProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for sellers to update their profile"""
    class Meta:
        model = Seller
        fields = ('business_name', 'business_description', 'business_type', 'logo',
                 'business_email', 'business_phone', 'business_website', 'business_address',
                 'business_city', 'business_state', 'business_country', 'business_postal_code',
                 'bank_account_name', 'bank_account_number', 'bank_name', 'bank_branch', 'ifsc_code')
    
    def validate(self, attrs):
        # Ensure user can only update their own seller profile
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            try:
                seller = request.user.seller
                if self.instance and self.instance != seller:
                    raise serializers.ValidationError(_('You can only update your own profile.'))
            except Seller.DoesNotExist:
                raise serializers.ValidationError(_('You are not registered as a seller.'))
        return attrs

class SellerDashboardSerializer(serializers.ModelSerializer):
    """Serializer for seller dashboard data"""
    pending_orders = serializers.SerializerMethodField()
    recent_sales = serializers.SerializerMethodField()
    monthly_earnings = serializers.SerializerMethodField()
    top_products = serializers.SerializerMethodField()
    
    class Meta:
        model = Seller
        fields = ('business_name', 'total_sales', 'total_orders', 'average_rating', 
                 'total_reviews', 'pending_orders', 'recent_sales', 'monthly_earnings', 'top_products')
    
    def get_pending_orders(self, obj):
        # This would be implemented when we have the orders app
        return 0
    
    def get_recent_sales(self, obj):
        # This would be implemented when we have the orders app
        return []
    
    def get_monthly_earnings(self, obj):
        from django.utils import timezone
        from datetime import timedelta
        start_date = timezone.now().date().replace(day=1)
        
        earnings = SellerEarnings.objects.filter(
            seller=obj,
            date__gte=start_date
        ).aggregate(
            total=models.Sum('net_earnings')
        )['total'] or 0
        
        return float(earnings)
    
    def get_top_products(self, obj):
        # This would be implemented when we have the products app
        return []
