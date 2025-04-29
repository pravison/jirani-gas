from django.urls import path
from . import views
urlpatterns = [
    path('<slug:slug>/products/', views.products, name='products'),
    path('<slug:slug>/add-products/', views.add_product, name='add_product'),
]
   
    