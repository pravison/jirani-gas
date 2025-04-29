from django.urls import path
from . import views
urlpatterns = [
    path('add-loyalty-points-to-customer/', views.add_loyalty_points_to_customer, name='add_loyalty_points_to_customer'),
    path('all-loyalty-points/', views.all_loyalty_points, name='all_loyalty_points'),
    path('redeemed-loyalty-points/', views.redeemed_loyalty_points, name='redeemed_loyalty_points'),
    path('loyalty-qr-code/', views.loyalty_qr_code, name='loyalty_qr_code'),
    path('loyalty-membership/', views.loyalty_membership, name='loyalty_membership'),
    path('borrow-points/', views.borrow_points_view, name='borrow_points'),
    path('repay-points/', views.repay_points_view, name='repay_points'),
]