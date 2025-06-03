from django.db import models
from django.contrib.auth.models import User
from customers.models import Customer
from businesses.models import Staff


class RefferalChallenge(models.Model):
    challenge_type = models.CharField(max_length=100, choices=(('today', 'today'), ('this week', 'this week'), ('this month', 'this month'), ('this year', 'this year'), ('upto date', 'upto date')))
    challenge_name = models.CharField(max_length=200)
    participating_reward = models.IntegerField(default=0, help_text='points awarded to customers for participating')
    # challenge_reward_type = models.CharField(max_length=100, choices=(('points', 'points'), ('this week', 'this week'), ('this month', 'this month'), ('this year', 'this year'), ('upto date', 'upto date'))) 
    challenge_reward = models.CharField(max_length=500, help_text='whats the reward for the challenge')
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
