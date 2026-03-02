from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from core.models import TimeStampedModel, SoftDeleteModel
import uuid

class Seller(TimeStampedModel):
    """Seller/Vendor model for dropshipping platform"""
    APPROVAL_STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('suspended', _('Suspended')),
    )
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='seller'
    )
    business_name = models.CharField(_('business name'), max_length=200)
    business_description = models.TextField(_('business description'), max_length=1000)
    logo = models.ImageField(_('business logo'), upload_to='sellers/logos/', blank=True, null=True)
    
    # Business Information
    business_type = models.CharField(_('business type'), max_length=50, default='individual')
    registration_number = models.CharField(_('registration number'), max_length=100, blank=True)
    tax_id = models.CharField(_('tax ID'), max_length=50, blank=True)
    
    # Contact Information
    business_email = models.EmailField(_('business email'), blank=True)
    business_phone = models.CharField(_('business phone'), max_length=20, blank=True)
    business_website = models.URLField(_('business website'), blank=True)
    
    # Address
    business_address = models.TextField(_('business address'), blank=True)
    business_city = models.CharField(_('business city'), max_length=100, blank=True)
    business_state = models.CharField(_('business state'), max_length=100, blank=True)
    business_country = models.CharField(_('business country'), max_length=100, blank=True)
    business_postal_code = models.CharField(_('business postal code'), max_length=20, blank=True)
    
    # Approval Status
    approval_status = models.CharField(
        _('approval status'),
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='pending'
    )
    rejection_reason = models.TextField(_('rejection reason'), blank=True)
    approved_at = models.DateTimeField(_('approved at'), null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_sellers'
    )
    
    # Financial Information
    bank_account_name = models.CharField(_('bank account name'), max_length=200, blank=True)
    bank_account_number = models.CharField(_('bank account number'), max_length=50, blank=True)
    bank_name = models.CharField(_('bank name'), max_length=200, blank=True)
    bank_branch = models.CharField(_('bank branch'), max_length=200, blank=True)
    ifsc_code = models.CharField(_('IFSC code'), max_length=20, blank=True)
    
    # Performance Metrics
    total_sales = models.DecimalField(_('total sales'), max_digits=15, decimal_places=2, default=0)
    total_orders = models.PositiveIntegerField(_('total orders'), default=0)
    average_rating = models.DecimalField(_('average rating'), max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(_('total reviews'), default=0)
    
    # Settings
    commission_rate = models.DecimalField(_('commission rate'), max_digits=5, decimal_places=2, default=10.00)
    is_featured = models.BooleanField(_('featured seller'), default=False)
    
    class Meta:
        verbose_name = _('Seller')
        verbose_name_plural = _('Sellers')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.business_name} ({self.user.email})"
    
    @property
    def is_approved(self):
        return self.approval_status == 'approved'
    
    @property
    def is_pending(self):
        return self.approval_status == 'pending'
    
    @property
    def is_rejected(self):
        return self.approval_status == 'rejected'
    
    @property
    def is_suspended(self):
        return self.approval_status == 'suspended'

class SellerDocument(TimeStampedModel):
    """Documents uploaded by sellers for verification"""
    DOCUMENT_TYPES = (
        ('business_registration', _('Business Registration')),
        ('tax_certificate', _('Tax Certificate')),
        ('identity_proof', _('Identity Proof')),
        ('address_proof', _('Address Proof')),
        ('bank_statement', _('Bank Statement')),
        ('other', _('Other')),
    )
    
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(_('document type'), max_length=50, choices=DOCUMENT_TYPES)
    title = models.CharField(_('title'), max_length=200)
    file = models.FileField(_('file'), upload_to='sellers/documents/')
    is_verified = models.BooleanField(_('verified'), default=False)
    verification_notes = models.TextField(_('verification notes'), blank=True)
    
    class Meta:
        verbose_name = _('Seller Document')
        verbose_name_plural = _('Seller Documents')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.seller.business_name} - {self.title}"

class SellerPayout(TimeStampedModel):
    """Payout records for sellers"""
    PAYOUT_STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
    )
    
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(_('amount'), max_digits=15, decimal_places=2)
    period_start = models.DateField(_('period start'))
    period_end = models.DateField(_('period end'))
    status = models.CharField(_('status'), max_length=20, choices=PAYOUT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(_('transaction ID'), max_length=100, blank=True)
    notes = models.TextField(_('notes'), blank=True)
    processed_at = models.DateTimeField(_('processed at'), null=True, blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_payouts'
    )
    
    class Meta:
        verbose_name = _('Seller Payout')
        verbose_name_plural = _('Seller Payouts')
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.seller.business_name} - {self.amount} ({self.status})"

class SellerEarnings(TimeStampedModel):
    """Daily/weekly earnings tracking for sellers"""
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='earnings')
    date = models.DateField(_('date'))
    total_sales = models.DecimalField(_('total sales'), max_digits=15, decimal_places=2, default=0)
    total_orders = models.PositiveIntegerField(_('total orders'), default=0)
    commission_amount = models.DecimalField(_('commission amount'), max_digits=15, decimal_places=2, default=0)
    net_earnings = models.DecimalField(_('net earnings'), max_digits=15, decimal_places=2, default=0)
    
    class Meta:
        verbose_name = _('Seller Earnings')
        verbose_name_plural = _('Seller Earnings')
        ordering = ['-date']
        unique_together = ['seller', 'date']
        
    def __str__(self):
        return f"{self.seller.business_name} - {self.date}: {self.net_earnings}"

class SellerReview(TimeStampedModel):
    """Reviews for sellers"""
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='seller_reviews')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='given_seller_reviews'
    )
    rating = models.PositiveIntegerField(_('rating'), choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(_('comment'), max_length=1000)
    is_verified_purchase = models.BooleanField(_('verified purchase'), default=False)
    
    class Meta:
        verbose_name = _('Seller Review')
        verbose_name_plural = _('Seller Reviews')
        ordering = ['-created_at']
        unique_together = ['seller', 'user']
        
    def __str__(self):
        return f"{self.seller.business_name} - {self.rating} stars by {self.user.email}"
