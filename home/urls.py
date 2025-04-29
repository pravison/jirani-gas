from django.urls import path, include
from store.views import business_store, e_store
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('pricing/', views.pricing, name='pricing'),
    path('profile/', views.profile, name='profile'),
    path('customer/', views.all_customers, name='all_customers'),
    path('e-store/', e_store, name='e_store'),
    # business -store commers 
    path('<slug:slug>/e-store/', business_store, name='business_store')
    ]
   