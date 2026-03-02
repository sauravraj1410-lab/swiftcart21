from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Simple test endpoint (no models required)
    path('simple-test/', views.simple_test, name='simple-test'),
    
    # API endpoints (no 'api/' prefix since it's already in main urls)
    path('', views.ProductListView.as_view(), name='product-list-api'),
    path('create/', views.ProductCreateView.as_view(), name='product-create-api'),
    path('test/', views.TestAPIView.as_view(), name='test-api'),
    path('admin/<uuid:pk>/', views.AdminProductDetailView.as_view(), name='admin-product-detail-api'),
    path('<uuid:pk>/', views.ProductDetailView.as_view(), name='product-detail-api'),
    path('categories/', views.CategoryListView.as_view(), name='category-list-api'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category-create-api'),
    path('categories/<uuid:pk>/', views.CategoryDetailView.as_view(), name='category-detail-api'),
    path('search/', views.ProductSearchView.as_view(), name='product-search-api'),
    
    # Admin endpoints
    path('admin/create/', views.ProductCreateView.as_view(), name='product-create'),
    path('<uuid:pk>/update/', views.ProductUpdateView.as_view(), name='product-update'),
    path('<uuid:pk>/delete/', views.ProductDeleteView.as_view(), name='product-delete'),
]
