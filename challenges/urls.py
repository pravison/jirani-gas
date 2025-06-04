from django.urls import path
from . import views
urlpatterns = [
    path('challenge-opportunities/', views.refferal_challenge_opportunities, name='refferal_challenge_opportunities'),
    path('challenge-opportunities/<int:id>/', views.view_refferal_challenge, name='view_refferal_challenge'),
    path('join-refferal-challenge/<int:id>/', views.join_refferal_challenge, name='join_refferal_challenge'),
    path('vote-challenge-opportunities/', views.vote_challenge_opportunities, name='vote_challenge_opportunities'),
    path('vote-challenge-opportunities/<int:id>/', views.view_vote_challenge, name='view_vote_challenge'),
    path('join-vote-challenge/<int:id>/', views.join_vote_challenge, name='join_vote_challenge'),
    path('view-vote-challenge-participant/<int:id>/', views.view_vote_challenge_participant, name='view_vote_challenge_participant'),
]
   