from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Seller, SellerDocument, SellerPayout, SellerEarnings, SellerReview

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user_email', 'approval_status', 'total_sales', 'total_orders', 'average_rating', 'is_featured', 'created_at')
    list_filter = ('approval_status', 'is_featured', 'business_type', 'created_at')
    search_fields = ('business_name', 'user__email', 'business_city', 'business_country')
    ordering = ('-created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at', 'total_sales', 'total_orders', 'average_rating', 'total_reviews')
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('user', 'business_name', 'business_description', 'logo', 'business_type')
        }),
        (_('Business Details'), {
            'fields': ('registration_number', 'tax_id', 'business_email', 'business_phone', 'business_website')
        }),
        (_('Business Address'), {
            'fields': ('business_address', 'business_city', 'business_state', 'business_country', 'business_postal_code')
        }),
        (_('Approval Status'), {
            'fields': ('approval_status', 'rejection_reason', 'approved_at', 'approved_by')
        }),
        (_('Financial Information'), {
            'fields': ('bank_account_name', 'bank_account_number', 'bank_name', 'bank_branch', 'ifsc_code')
        }),
        (_('Performance Metrics'), {
            'fields': ('total_sales', 'total_orders', 'average_rating', 'total_reviews', 'commission_rate', 'is_featured')
        }),
        (_('Timestamps'), {
            'fields': ('id', 'created_at', 'updated_at')
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = _('Email')
    
    actions = ['approve_sellers', 'reject_sellers', 'suspend_sellers', 'feature_sellers', 'unfeature_sellers']
    
    def approve_sellers(self, request, queryset):
        from django.utils import timezone
        for seller in queryset:
            seller.approval_status = 'approved'
            seller.approved_at = timezone.now()
            seller.approved_by = request.user
            seller.save()
        self.message_user(request, _('Selected sellers have been approved.'))
    approve_sellers.short_description = _('Approve selected sellers')
    
    def reject_sellers(self, request, queryset):
        queryset.update(approval_status='rejected')
        self.message_user(request, _('Selected sellers have been rejected.'))
    reject_sellers.short_description = _('Reject selected sellers')
    
    def suspend_sellers(self, request, queryset):
        queryset.update(approval_status='suspended')
        self.message_user(request, _('Selected sellers have been suspended.'))
    suspend_sellers.short_description = _('Suspend selected sellers')
    
    def feature_sellers(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, _('Selected sellers have been featured.'))
    feature_sellers.short_description = _('Feature selected sellers')
    
    def unfeature_sellers(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, _('Selected sellers have been unfeatured.'))
    unfeature_sellers.short_description = _('Unfeature selected sellers')

@admin.register(SellerDocument)
class SellerDocumentAdmin(admin.ModelAdmin):
    list_display = ('seller', 'document_type', 'title', 'is_verified', 'created_at')
    list_filter = ('document_type', 'is_verified', 'created_at')
    search_fields = ('seller__business_name', 'title')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Document Information'), {
            'fields': ('seller', 'document_type', 'title', 'file')
        }),
        (_('Verification'), {
            'fields': ('is_verified', 'verification_notes')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['verify_documents', 'unverify_documents']
    
    def verify_documents(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, _('Selected documents have been verified.'))
    verify_documents.short_description = _('Verify selected documents')
    
    def unverify_documents(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, _('Selected documents have been unverified.'))
    unverify_documents.short_description = _('Unverify selected documents')

@admin.register(SellerPayout)
class SellerPayoutAdmin(admin.ModelAdmin):
    list_display = ('seller', 'amount', 'period', 'status', 'processed_at', 'transaction_id')
    list_filter = ('status', 'period_start', 'period_end', 'processed_at')
    search_fields = ('seller__business_name', 'transaction_id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    def period(self, obj):
        return f"{obj.period_start} to {obj.period_end}"
    period.short_description = _('Period')
    
    fieldsets = (
        (_('Payout Information'), {
            'fields': ('seller', 'amount', 'period_start', 'period_end', 'status')
        }),
        (_('Processing'), {
            'fields': ('transaction_id', 'notes', 'processed_at', 'processed_by')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['process_payouts', 'complete_payouts', 'fail_payouts']
    
    def process_payouts(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='processing', processed_at=timezone.now(), processed_by=request.user)
        self.message_user(request, _('Selected payouts have been marked as processing.'))
    process_payouts.short_description = _('Process selected payouts')
    
    def complete_payouts(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='completed', processed_at=timezone.now(), processed_by=request.user)
        self.message_user(request, _('Selected payouts have been completed.'))
    complete_payouts.short_description = _('Complete selected payouts')
    
    def fail_payouts(self, request, queryset):
        queryset.update(status='failed')
        self.message_user(request, _('Selected payouts have been marked as failed.'))
    fail_payouts.short_description = _('Fail selected payouts')

@admin.register(SellerEarnings)
class SellerEarningsAdmin(admin.ModelAdmin):
    list_display = ('seller', 'date', 'total_sales', 'total_orders', 'commission_amount', 'net_earnings')
    list_filter = ('date', 'seller')
    search_fields = ('seller__business_name',)
    ordering = ('-date',)
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        (_('Earnings Information'), {
            'fields': ('seller', 'date', 'total_sales', 'total_orders', 'commission_amount', 'net_earnings')
        }),
        (_('Timestamps'), {
            'fields': ('id', 'created_at', 'updated_at')
        }),
    )

@admin.register(SellerReview)
class SellerReviewAdmin(admin.ModelAdmin):
    list_display = ('seller', 'user_email', 'rating', 'is_verified_purchase', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'created_at')
    search_fields = ('seller__business_name', 'user__email', 'comment')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = _('User Email')
    
    fieldsets = (
        (_('Review Information'), {
            'fields': ('seller', 'user', 'rating', 'comment', 'is_verified_purchase')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
