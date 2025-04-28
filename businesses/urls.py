from django.urls import path
from . import views
urlpatterns = [
    path('add-business/', views.add_business, name='add_business'),
    # will update use of these two line dont delete them 
    path('<slug:slug>/view_coupon/', views.view_coupon, name='view_coupon'),
    
    path('', views.business, name='business'),
    path('<slug:slug>/', views.dashboard, name='dashboard'),
    path('<slug:slug>/add-staff', views.add_staff, name='add_staff'),
    path('<slug:slug>/customers/', views.customers, name='customers'),
    path('<slug:slug>/create-store-Challenge/', views.create_store_challenge, name='create_store_challenge'),
    path('<slug:slug>/store-challenges/', views.store_challenges, name='store_challenges'),
    path('<slug:slug>/view-store-challenge/', views.view_store_challenge, name='view_store_challenge'),
    # i used stand-a-chance-to-win rather than add_challenge_participant because the url is readable after scan and we want to encourage customers to paticipate 
    path('<slug:slug>/stand-a-chance-to-win/', views.add_challenge_participant, name='add_challenge_participant'),
    path('<slug:slug>/loyalty-points-category/', views.loyalty_points_category, name='loyalty_points_category'),
    path('<slug:slug>/edit-loyalty-category/', views.edit_loyalty_category, name='edit_loyalty_category'),
    path('<slug:slug>/add-loyalty-points-to-customer/', views.add_loyalty_points_to_customer, name='add_loyalty_points_to_customer'),
    path('<slug:slug>/create-refferal-code/', views.create_refferal_code, name='create_refferal_code'),
]