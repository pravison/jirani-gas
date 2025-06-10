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
    path('create-vote-challenge/', views.create_vote_challenge, name='create_vote_challenge'),
    path('<slug:slug>/business-vote-challenges/', views.business_vote_challenges, name='business_vote_challenges'),
    path('invite-vote-challenge-patners/', views.invite_vote_challenge_patners, name='invite_vote_challenge_patners'),
    path('<slug:slug>/challenge-patnership-invite/', views.challenge_patnership_invite, name='challenge_patnership_invite'),
    path('cast-vote-for-participant/<int:id>/', views.cast_vote_for_participant, name='cast_vote_for_participant'),
]
   