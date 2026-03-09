from django.shortcuts import render, get_object_or_404
from django.conf import settings
from django.utils.text import slugify
from rest_framework import generics, permissions, status, views, filters, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, ProductImage, ProductVariant
from .serializers import (
    ProductSerializer, ProductListSerializer, CategorySerializer
)
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import uuid
import logging


logger = logging.getLogger(__name__)


def _clean_optional_number(value):
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = value.strip().lower()
        if cleaned in ('', 'null', 'none', 'undefined'):
            return None
    return value


def _debug_endpoint_allowed(request):
    return settings.DEBUG or (request.user.is_authenticated and request.user.is_superuser)

# Simple test endpoint that doesn't require models
@api_view(['GET'])
def simple_test(request):
    """Simple test endpoint to verify URL routing works"""
    if not _debug_endpoint_allowed(request):
        return JsonResponse({'error': 'Not found'}, status=404)

    return JsonResponse({
        'message': 'Simple API test working!',
        'method': request.method,
        'path': request.path,
        'debug': 'URL routing is working'
    })

class TestAPIView(views.APIView):
    """Test API endpoint to verify system is working"""
    permission_classes = [permissions.AllowAny]  # Allow any user for debugging
    
    def get(self, request):
        if not _debug_endpoint_allowed(request):
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'message': 'API is working!',
            'user': str(request.user) if request.user.is_authenticated else 'Anonymous',
            'is_authenticated': request.user.is_authenticated,
            'is_superuser': request.user.is_superuser if request.user.is_authenticated else False,
            'method': request.method,
            'debug': 'Test endpoint is accessible'
        })
    
    def post(self, request):
        if not _debug_endpoint_allowed(request):
            return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            'message': 'POST request working!',
            'user': str(request.user) if request.user.is_authenticated else 'Anonymous',
            'is_authenticated': request.user.is_authenticated,
            'is_superuser': request.user.is_superuser if request.user.is_authenticated else False,
            'method': request.method,
            'data_received': request.data
        })

class ProductListView(generics.ListAPIView):
    """Product list view"""
    queryset = Product.objects.filter(status='active').select_related('category').prefetch_related('images')
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'featured', 'digital']
    search_fields = ['name', 'description', 'short_description']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']

class ProductDetailView(generics.RetrieveAPIView):
    """Product detail view"""
    queryset = Product.objects.filter(status='active').select_related('category').prefetch_related('images', 'variants')
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

class CategoryListView(generics.ListAPIView):
    """Category list view"""
    queryset = Category.objects.filter(is_active=True).select_related('parent')
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class CategoryDetailView(generics.RetrieveAPIView):
    """Category detail view with products"""
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True).select_related('parent')
    
    def retrieve(self, request, *args, **kwargs):
        category = self.get_object()
        # Get products in this category
        products = Product.objects.filter(
            category=category, 
            status='active'
        ).select_related('category').prefetch_related('images')
        
        # Serialize products
        product_serializer = ProductListSerializer(products, many=True)
        
        # Serialize category
        category_serializer = self.get_serializer(category)
        
        return Response({
            'category': category_serializer.data,
            'products': product_serializer.data
        })


class CategoryCreateView(generics.CreateAPIView):
    """Create category - Admin only"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser, FormParser]

    def create(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response(
                {'success': False, 'error': 'Only admin users can create categories.'},
                status=status.HTTP_403_FORBIDDEN
            )

        name = (request.data.get('name') or '').strip()
        description = (request.data.get('description') or '').strip()
        if not name:
            return Response(
                {'success': False, 'error': 'Category name is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        existing = Category.objects.filter(name__iexact=name).first()
        if existing:
            return Response(
                {
                    'success': True,
                    'message': 'Category already exists.',
                    'category': CategorySerializer(existing, context={'request': request}).data,
                },
                status=status.HTTP_200_OK
            )

        base_slug = slugify(name) or 'category'
        slug = base_slug
        counter = 1
        while Category.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{counter}'
            counter += 1

        category = Category.objects.create(
            name=name,
            slug=slug,
            description=description,
            is_active=True,
        )

        return Response(
            {
                'success': True,
                'message': 'Category created successfully.',
                'category': CategorySerializer(category, context={'request': request}).data,
            },
            status=status.HTTP_201_CREATED
        )

class ProductSearchView(generics.ListAPIView):
    """Product search view"""
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'short_description', 'sku']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Product.objects.filter(status='active').select_related('category').prefetch_related('images')
        search_query = self.request.query_params.get('q', '')
        if search_query:
            queryset = queryset.filter(
                name__icontains=search_query
            ) | queryset.filter(
                description__icontains=search_query
            ) | queryset.filter(
                short_description__icontains=search_query
            ) | queryset.filter(
                sku__icontains=search_query
            )
        return queryset

# Frontend views
def products_list(request):
    """Products listing page"""
    from core.models import SiteSettings
    site_settings = SiteSettings.objects.first()
    
    # Get search query
    search_query = request.GET.get('search', '')
    
    context = {
        'site_settings': site_settings,
        'search_query': search_query,
    }
    
    return render(request, 'core/products_list.html', context)

class ProductCreateView(generics.CreateAPIView):
    """Create new product - Admin only"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def create(self, request, *args, **kwargs):
        """Create product with proper error handling"""
        try:
            # Check user permissions
            if not request.user.is_superuser:
                return Response({
                    'success': False,
                    'error': 'Only admin users can create products'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Validate required fields
            required_fields = ['name', 'sku', 'price', 'quantity', 'short_description', 'description']
            errors = {}
            
            for field in required_fields:
                if field not in request.data:
                    errors[field] = f'{field.replace("_", " ").title()} is missing'
                elif not request.data[field]:
                    errors[field] = f'{field.replace("_", " ").title()} is required'
            
            # Handle category
            if 'category' not in request.data:
                errors['category'] = 'Category is missing'
            elif not request.data['category']:
                errors['category'] = 'Category is required'
            
            if errors:
                return Response({
                    'success': False,
                    'error': 'Validation failed',
                    'errors': errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate slug if not provided
            if 'slug' not in request.data or not request.data['slug']:
                import re
                name = request.data['name']
                slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
                request.data._mutable = True
                request.data['slug'] = slug
                request.data._mutable = False
            
            # Set default values and sanitize nullable numeric fields.
            image_file = request.FILES.get('image')
            request_data = request.data
            if hasattr(request_data, '_mutable'):
                request_data._mutable = True

            request_data['compare_price'] = _clean_optional_number(request_data.get('compare_price'))
            request_data['weight'] = _clean_optional_number(request_data.get('weight'))
            request_data['cost_price'] = _clean_optional_number(request_data.get('cost_price'))
            request_data['seller_upi_id'] = getattr(settings, 'ADMIN_UPI_ID', '')
            request_data['seller'] = None
            request_data['barcode'] = ''

            # Keep uploaded file for ProductImage and remove unknown field from Product serializer payload.
            if hasattr(request_data, 'pop'):
                request_data.pop('image', None)

            if hasattr(request_data, '_mutable'):
                request_data._mutable = False

            # Create product
            response = super().create(request, *args, **kwargs)

            image_upload_warning = ''

            # Persist uploaded primary image for storefront rendering.
            if image_file and response.status_code == status.HTTP_201_CREATED:
                product_id = response.data.get('id')
                created_product = Product.objects.select_related('category', 'seller').prefetch_related('images', 'variants').filter(id=product_id).first()
                if created_product:
                    try:
                        ProductImage.objects.create(
                            product=created_product,
                            image=image_file,
                            alt_text=created_product.name,
                            is_primary=True,
                            sort_order=0,
                        )
                        # Refresh serialized data so image relation is reflected.
                        refreshed_product = Product.objects.select_related('category', 'seller').prefetch_related('images', 'variants').filter(id=product_id).first()
                        if refreshed_product:
                            response.data = self.get_serializer(refreshed_product).data
                    except Exception:
                        logger.exception('Product image upload failed for product %s', product_id)
                        image_upload_warning = (
                            'Product was created, but image upload failed. '
                            'Please check server time / media storage configuration and try uploading again.'
                        )

            response_payload = {
                'success': True,
                'message': 'Product added successfully! UPI payment method has been automatically configured.',
                'product': response.data
            }
            if image_upload_warning:
                response_payload['warning'] = image_upload_warning

            return Response(response_payload, status=status.HTTP_201_CREATED)
            
        except serializers.ValidationError as e:
            return Response({
                'success': False,
                'error': 'Validation failed',
                'errors': e.detail
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception:
            logger.exception('Product creation failed')
            return Response({
                'success': False,
                'error': 'Failed to create product. Please review the data and try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def perform_create(self, serializer):
        """Set default values for admin products"""
        admin_upi_id = getattr(settings, 'ADMIN_UPI_ID', '')
        
        serializer.save(
            seller_upi_id=admin_upi_id,
            seller=None,
            barcode='',
            cost_price=None
        )

class ProductUpdateView(generics.UpdateAPIView):
    """Update product - Admin only"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        # Only allow superusers to update products
        if not self.request.user.is_superuser:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admin users can update products")
        return Product.objects.all()

class ProductDeleteView(generics.DestroyAPIView):
    """Delete product - Admin only"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        # Only allow superusers to delete products
        if not self.request.user.is_superuser:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admin users can delete products")
        return Product.objects.all()


class AdminProductDetailView(generics.RetrieveAPIView):
    """Admin product detail view for all statuses"""
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_superuser:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admin users can view admin product details")
        return Product.objects.select_related('category', 'seller').prefetch_related('images', 'variants')

