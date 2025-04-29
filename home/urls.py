from django.urls import path, include
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('pricing/', views.pricing, name='pricing'),
    path('profile/', views.profile, name='profile'),
    path('customer/', views.all_customers, name='all_customers')
    ]
   