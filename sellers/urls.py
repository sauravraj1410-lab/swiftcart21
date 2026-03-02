from django.urls import path
from . import views

app_name = 'sellers'

urlpatterns = [
    # Seller Registration and Profile
    path('register/', views.SellerRegistrationView.as_view(), name='register'),
    path('profile/', views.SellerProfileView.as_view(), name='profile'),
    path('dashboard/', views.SellerDashboardView.as_view(), name='dashboard'),
    path('status/', views.my_seller_status, name='status'),
    path('become/', views.become_seller, name='become'),
    
    # Seller Documents
    path('documents/', views.SellerDocumentListCreateView.as_view(), name='document-list'),
    path('documents/<int:pk>/', views.SellerDocumentDetailView.as_view(), name='document-detail'),
    
    # Seller Payouts and Earnings
    path('payouts/', views.SellerPayoutListView.as_view(), name='payout-list'),
    path('earnings/', views.SellerEarningsListView.as_view(), name='earnings-list'),
    
    # Seller Reviews
    path('<uuid:seller_id>/reviews/', views.SellerReviewListCreateView.as_view(), name='review-list'),
    
    # Public Seller Views
    path('public/', views.public_sellers, name='public-list'),
    path('public/<uuid:seller_id>/', views.seller_detail, name='public-detail'),
    
    # Admin Views
    path('admin/list/', views.SellerListView.as_view(), name='admin-list'),
    path('admin/<uuid:pk>/approve/', views.SellerApprovalView.as_view(), name='admin-approve'),
    
    # Admin API Views
    path('admin/sellers/<uuid:seller_id>/approve/', views.approve_seller, name='admin-approve-seller'),
    path('admin/sellers/<uuid:seller_id>/reject/', views.reject_seller, name='admin-reject-seller'),
    path('admin/sellers/<uuid:seller_id>/delete/', views.delete_seller, name='admin-delete-seller'),
]
