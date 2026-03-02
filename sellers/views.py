from django.shortcuts import render, get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import status, generics, permissions, filters, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Seller, SellerDocument, SellerPayout, SellerEarnings, SellerReview
from .serializers import (
    SellerSerializer, SellerRegistrationSerializer, SellerDocumentSerializer,
    SellerPayoutSerializer, SellerEarningsSerializer, SellerReviewSerializer,
    SellerProfileUpdateSerializer, SellerDashboardSerializer
)
import logging


logger = logging.getLogger(__name__)


def _require_admin(request):
    if not request.user.is_superuser:
        return Response({'error': _('Admin access required.')}, status=status.HTTP_403_FORBIDDEN)
    return None

# Admin API Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def approve_seller(request, seller_id):
    """Approve a seller"""
    admin_error = _require_admin(request)
    if admin_error:
        return admin_error

    try:
        seller = get_object_or_404(Seller, id=seller_id)
        seller.approval_status = 'approved'
        seller.approved_at = timezone.now()
        seller.approved_by = request.user
        seller.save()
        
        # Send notification to seller
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = _('Your Seller Account Has Been Approved')
            message = _(
                f'Congratulations! Your seller account has been approved.\n\n'
                f'You can now start adding products and managing your store.\n'
                f'Login to your seller dashboard to get started.'
            )
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [seller.user.email],
                fail_silently=False,
            )
        except Exception:
            logger.warning('Failed to send seller approval email', exc_info=True)
        
        return Response({
            'message': 'Seller approved successfully',
            'seller': SellerSerializer(seller).data
        })
    except Exception:
        logger.exception('Seller approval failed')
        return Response({'error': _('Unable to approve seller right now.')}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reject_seller(request, seller_id):
    """Reject a seller"""
    admin_error = _require_admin(request)
    if admin_error:
        return admin_error

    try:
        seller = get_object_or_404(Seller, id=seller_id)
        seller.approval_status = 'rejected'
        seller.rejection_reason = request.data.get('reason', 'Application rejected')
        seller.save()
        
        # Send notification to seller
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = _('Your Seller Application Has Been Rejected')
            message = _(
                f'Your seller application has been rejected.\n\n'
                f'Reason: {seller.rejection_reason}\n\n'
                f'If you believe this is a mistake, please contact support.'
            )
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [seller.user.email],
                fail_silently=False,
            )
        except Exception:
            logger.warning('Failed to send seller rejection email', exc_info=True)
        
        return Response({
            'message': 'Seller rejected successfully',
            'seller': SellerSerializer(seller).data
        })
    except Exception:
        logger.exception('Seller rejection failed')
        return Response({'error': _('Unable to reject seller right now.')}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_seller(request, seller_id):
    """Delete a seller"""
    admin_error = _require_admin(request)
    if admin_error:
        return admin_error

    try:
        seller = get_object_or_404(Seller, id=seller_id)
        user = seller.user
        
        # Delete seller and associated user
        seller.delete()
        user.delete()
        
        return Response({
            'message': 'Seller deleted successfully'
        })
    except Exception:
        logger.exception('Seller deletion failed')
        return Response({'error': _('Unable to delete seller right now.')}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SellerRegistrationView(generics.CreateAPIView):
    """Register as a seller"""
    serializer_class = SellerRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        seller = serializer.save()
        
        # Send notification to admin about new seller registration
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = _('New Seller Registration - Action Required')
            message = _(
                f'New seller registration requires your approval:\n\n'
                f'Business Name: {seller.business_name}\n'
                f'Email: {seller.user.email}\n'
                f'Phone: {seller.business_phone}\n'
                f'Business Type: {seller.business_type}\n\n'
                f'Please review and approve/reject in the admin panel.'
            )
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],  # Send to admin email from .env
                fail_silently=False,
            )
        except Exception:
            logger.warning('Failed to send seller registration admin notification', exc_info=True)
        
        return Response({
            'message': _('Seller registration successful. Your application is under review and will be approved by an administrator.'),
            'seller': SellerSerializer(seller).data
        }, status=status.HTTP_201_CREATED)

class SellerProfileView(generics.RetrieveUpdateAPIView):
    """Get and update seller profile"""
    serializer_class = SellerProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        try:
            return self.request.user.seller
        except Seller.DoesNotExist:
            raise serializers.ValidationError(_('You are not registered as a seller.'))

class SellerDashboardView(generics.RetrieveAPIView):
    """Get seller dashboard data"""
    serializer_class = SellerDashboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        try:
            return self.request.user.seller
        except Seller.DoesNotExist:
            raise serializers.ValidationError(_('You are not registered as a seller.'))

class SellerDocumentListCreateView(generics.ListCreateAPIView):
    """List and create seller documents"""
    serializer_class = SellerDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['document_type', 'is_verified']
    search_fields = ['title']
    ordering_fields = ['created_at', 'document_type']
    
    def get_queryset(self):
        try:
            return SellerDocument.objects.filter(seller=self.request.user.seller)
        except Seller.DoesNotExist:
            return SellerDocument.objects.none()

class SellerDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update and delete seller document"""
    serializer_class = SellerDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            return SellerDocument.objects.filter(seller=self.request.user.seller)
        except Seller.DoesNotExist:
            return SellerDocument.objects.none()

class SellerPayoutListView(generics.ListAPIView):
    """List seller payouts"""
    serializer_class = SellerPayoutSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['transaction_id']
    ordering_fields = ['created_at', 'amount', 'period_start']
    
    def get_queryset(self):
        try:
            return SellerPayout.objects.filter(seller=self.request.user.seller)
        except Seller.DoesNotExist:
            return SellerPayout.objects.none()

class SellerEarningsListView(generics.ListAPIView):
    """List seller earnings"""
    serializer_class = SellerEarningsSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['date']
    ordering_fields = ['date', 'total_sales', 'net_earnings']
    
    def get_queryset(self):
        try:
            return SellerEarnings.objects.filter(seller=self.request.user.seller)
        except Seller.DoesNotExist:
            return SellerEarnings.objects.none()

class SellerReviewListCreateView(generics.ListCreateAPIView):
    """List and create seller reviews"""
    serializer_class = SellerReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['rating', 'is_verified_purchase']
    ordering_fields = ['created_at', 'rating']
    
    def get_queryset(self):
        seller_id = self.kwargs.get('seller_id')
        if seller_id:
            return SellerReview.objects.filter(seller_id=seller_id)
        return SellerReview.objects.none()
    
    def perform_create(self, serializer):
        seller_id = self.kwargs.get('seller_id')
        seller = get_object_or_404(Seller, id=seller_id)
        serializer.save(user=self.request.user, seller=seller)

# Admin Views
class SellerListView(generics.ListAPIView):
    """List all sellers (Admin only)"""
    serializer_class = SellerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['approval_status', 'business_type', 'is_featured']
    search_fields = ['business_name', 'user__email', 'business_city']
    ordering_fields = ['created_at', 'business_name', 'total_sales']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Seller.objects.all()
        return Seller.objects.none()

class SellerApprovalView(generics.UpdateAPIView):
    """Approve or reject seller applications (Admin only)"""
    serializer_class = SellerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Seller.objects.all()
        return Seller.objects.none()
    
    def update(self, request, *args, **kwargs):
        seller = self.get_object()
        approval_status = request.data.get('approval_status')
        rejection_reason = request.data.get('rejection_reason', '')
        
        if approval_status not in ['approved', 'rejected', 'suspended']:
            return Response(
                {'error': _('Invalid approval status.')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        seller.approval_status = approval_status
        seller.rejection_reason = rejection_reason
        
        if approval_status == 'approved':
            seller.approved_at = timezone.now()
            seller.approved_by = request.user
            seller.rejection_reason = ''
        
        seller.save()
        
        return Response({
            'message': _('Seller status updated successfully.'),
            'seller': SellerSerializer(seller).data
        })

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_sellers(request):
    """Get list of approved sellers for public display"""
    sellers = Seller.objects.filter(
        approval_status='approved',
        is_featured=True
    ).order_by('-created_at')
    
    serializer = SellerSerializer(sellers, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def seller_detail(request, seller_id):
    """Get seller details for public display"""
    try:
        seller = Seller.objects.get(id=seller_id, approval_status='approved')
        serializer = SellerSerializer(seller)
        return Response(serializer.data)
    except Seller.DoesNotExist:
        return Response(
            {'error': _('Seller not found.')},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_seller_status(request):
    """Get current user's seller registration status"""
    try:
        seller = request.user.seller
        return Response({
            'is_seller': True,
            'seller': SellerSerializer(seller).data
        })
    except Seller.DoesNotExist:
        return Response({
            'is_seller': False,
            'message': _('You are not registered as a seller.')
        })

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def become_seller(request):
    """Convert existing user to seller"""
    try:
        seller = request.user.seller
        return Response(
            {'message': _('You are already registered as a seller.')},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Seller.DoesNotExist:
        # Create basic seller profile
        seller = Seller.objects.create(
            user=request.user,
            business_name=f"{request.user.get_full_name() or request.user.email}'s Store",
            business_description='',
            approval_status='pending'
        )
        
        return Response({
            'message': _('Seller profile created. Please complete your business information.'),
            'seller': SellerSerializer(seller).data
        }, status=status.HTTP_201_CREATED)
