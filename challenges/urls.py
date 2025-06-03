from django.urls import path
from . import views
urlpatterns = [
    path('challenge-opportunities/', views.refferal_challenge_opportunities, name='refferal_challenge_opportunities'),
    path('challenge-opportunities/<int:id>/', views.view_refferal_challenge, name='view_refferal_challenge'),
    path('join-refferal-challenge/<int:id>/', views.join_refferal_challenge, name='join_refferal_challenge'),
]
   