from django.urls import path
from . import views
urlpatterns = [
    path('loyalty-points/', views.loyalty_points, name='loyalty_points'),
    path('redeemed-loyalty-points/', views.redeemed_loyalty_points, name='redeemed_loyalty_points'),
    path('loyalty-qr-code/', views.loyalty_qr_code, name='loyalty_qr_code'),
    path('loyalty-membership/', views.loyalty_membership, name='loyalty_membership'),
    path('customer-adding-loyalty-points/', views.customer_adding_loyalty_points, name='customer_adding_loyalty_points'),
    path('borrow-points/', views.borrow_points_view, name='borrow_points'),
    path('repay-points/', views.repay_points_view, name='repay_points'),
]