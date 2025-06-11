from django.contrib import admin
from .models import RefferalChallenge, RefferalChallengeResult, VoteChallenge, VoteChallengeParticipant, Vote, VoteChallengePartner
from .models import Topic, Subtopic, Question, Choice, QuestionandAnswerChallenge, Group, GroupMembership, Participant, Answer, Result

# Register your models here.
admin.site.register(RefferalChallenge)
admin.site.register(RefferalChallengeResult)
admin.site.register(VoteChallenge)
admin.site.register(VoteChallengeParticipant)
admin.site.register(Vote)
admin.site.register(VoteChallengePartner)

admin.site.register(Topic)
admin.site.register(Subtopic)
admin.site.register(Question)
admin.site.register(QuestionandAnswerChallenge)
admin.site.register(Choice)
admin.site.register(Group)
admin.site.register(GroupMembership)
admin.site.register(Participant)
admin.site.register(Answer)
admin.site.register(Result)