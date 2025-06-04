from django.contrib import admin
from .models import RefferalChallenge, RefferalChallengeResult, VoteChallenge, VoteChallengeParticipant, Vote
# Register your models here.
admin.site.register(RefferalChallenge)
admin.site.register(RefferalChallengeResult)
admin.site.register(VoteChallenge)
admin.site.register(VoteChallengeParticipant)
admin.site.register(Vote)