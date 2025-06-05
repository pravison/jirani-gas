from django.db import models
from django.contrib.auth.models import User
from customers.models import Customer
from businesses.models import Business, Staff


class RefferalChallenge(models.Model):
    challenge_type = models.CharField(max_length=100, choices=(('today', 'today'), ('this week', 'this week'), ('this month', 'this month'), ('this year', 'this year'), ('upto date', 'upto date')))
    challenge_name = models.CharField(max_length=200)
    participating_reward = models.IntegerField(default=0, help_text='points awarded to customers for participating')
    # challenge_reward_type = models.CharField(max_length=100, choices=(('points', 'points'), ('this week', 'this week'), ('this month', 'this month'), ('this year', 'this year'), ('upto date', 'upto date'))) 
    challenge_reward = models.CharField(max_length=500, help_text='whats the reward for the challenge')
    challenge_reward_monetary_value = models.IntegerField(default=0)
    challenge_brief = models.TextField(max_length=1500, blank=True, help_text='share a brief about the challenge')
    challenge_guidelines = models.TextField(max_length=1500, blank=True, help_text='share a brief about the challenge')
    target_winners = models.IntegerField(help_text='how many winners do you want for this challenge')
    closed = models.BooleanField(default=False)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    created_by = models.ForeignKey(Staff, blank=True, null=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return self.challenge_name

class RefferalChallengeResult(models.Model):
    challenge = models.ForeignKey(RefferalChallenge, on_delete=models.CASCADE, related_name="refferal_challenges")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    total_refferals = models.IntegerField(default=0)
    received_reward = models.CharField(max_length=200, null=True, blank=True)
    updated_by = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):

        return f'{self.customer} total refferal: {self.total_refferals}'


class VoteChallenge(models.Model):
    challenge_owner = models.ForeignKey(Business, blank=True, null=True, on_delete=models.SET_NULL, help_text='one who creates the challenge and responsible for distributing rewards', related_name="challenge_owner")# if null means our own company created the challenge and will be responsible for rewarding winners
    challenge_patners = models.ManyToManyField(Business, blank=True, help_text='business patners', related_name="challenge_patners")# businesses patnering in the challenge
    challenge_name = models.CharField(max_length=200)
    participating_reward = models.IntegerField(default=0, help_text='points awarded to customers for participating')
    challenge_reward = models.CharField(max_length=500, help_text='whats the reward for the challenge')
    challenge_reward_monetary_value = models.IntegerField(default=0)
    challenge_brief = models.TextField(max_length=1500, blank=True, help_text='share a brief about the challenge')
    challenge_guidelines = models.TextField(max_length=1500, blank=True, help_text='share a brief about the challenge')
    target_winners = models.IntegerField(help_text='how many winners do you want for this challenge')
    closed = models.BooleanField(default=False)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    created_by = models.ForeignKey(Staff, blank=True, null=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return self.challenge_name


class VoteChallengePartner(models.Model):
    challenge = models.ForeignKey(VoteChallenge, on_delete=models.CASCADE, related_name="vote_challenges_patners")
    partner = models.ForeignKey(Business, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    date_invited = models.DateField(auto_now_add=True)
    date_accepted = models.DateField(auto_now_add=True)

    def __str__(self):
        challenge_owner = self.challenge_owner if self.challenge_owner else 'jirani mall'
        return f'{challenge_owner}, {self.challenge}, {self.partner}'
    
class VoteChallengeParticipant(models.Model):
    challenge = models.ForeignKey(VoteChallenge, on_delete=models.CASCADE, related_name="vote_challenges")
    participant = models.ForeignKey(Customer, on_delete=models.CASCADE)
    total_voters = models.IntegerField(default=0)
    total_votes = models.IntegerField(default=0)
    received_reward = models.CharField(max_length=200, null=True, blank=True)
    date_joined = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):

        return f'{self.customer} total votes: {self.total_votes}'
    
class Vote(models.Model):
    challenge_participant = models.ForeignKey(VoteChallengeParticipant, on_delete=models.CASCADE, related_name="challenge_participant")
    voter = models.ForeignKey(Customer, on_delete=models.CASCADE)
    number_of_votes = models.IntegerField(default=0)
    date_voted = models.DateField(auto_now_add=True)

    def __str__(self):

        return f'{self.voter} voted {self.number_of_votes} for {self.challenge_participant}'
