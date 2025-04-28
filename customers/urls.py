from django.urls import path
from . import views
urlpatterns = [
    path('inquire/', views.inquire, name='inquire'),
    path('invite-a-neighbor/', views.add_customer, name='add_customer'),
]
   