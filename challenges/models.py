from django.db import models
from django.utils import timezone
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
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
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
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
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
        challenge_owner = self.challenge.challenge_owner if self.challenge.challenge_owner else 'jirani mall'
        return f'{challenge_owner}, {self.challenge}, {self.partner}'
    
class VoteChallengeParticipant(models.Model):
    challenge = models.ForeignKey(VoteChallenge, on_delete=models.CASCADE, related_name="vote_challenges")
    participant = models.ForeignKey(Customer, on_delete=models.CASCADE)
    results_image_url = models.URLField(max_length=500, null=True, blank=True)
    total_voters = models.IntegerField(default=0)
    total_votes = models.IntegerField(default=0)
    received_reward = models.CharField(max_length=200, null=True, blank=True)
    date_joined = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)

    def __str__(self):

        return f'{self.participant} total votes: {self.total_votes}'
    
class Vote(models.Model):
    challenge_participant = models.ForeignKey(VoteChallengeParticipant, on_delete=models.CASCADE, related_name="challenge_participant")
    voter = models.ForeignKey(Customer, on_delete=models.CASCADE)
    number_of_votes = models.IntegerField(default=0)
    date_voted = models.DateField(auto_now_add=True)

    def __str__(self):

        return f'{self.voter} voted {self.number_of_votes} for {self.challenge_participant}'


# Q and A challenge
# topic and questions
class Topic(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Subtopic(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.topic.name} - {self.name}"


class Question(models.Model):
    subtopic = models.ForeignKey(Subtopic, on_delete=models.CASCADE)
    text = models.TextField()
    order = models.PositiveIntegerField()

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

# challenge logic 
class QuestionandAnswerChallenge(models.Model):
    CHALLENGE_TYPES = [
        ('live', 'Live'),
        ('instant', 'Instant'),
    ]
    type = models.CharField(max_length=20, choices=CHALLENGE_TYPES, default='instant')
    business = models.ForeignKey(Business, blank=True, null=True, on_delete=models.SET_NULL)
    subtopic = models.ForeignKey(Subtopic, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    duration_seconds = models.IntegerField(default=20)
    requires_group = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)  # only for live
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title

# participation and results

class Group(models.Model):
    challenge = models.ForeignKey(QuestionandAnswerChallenge, on_delete=models.CASCADE, related_name="groups")
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.challenge.title}"

class GroupMembership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="memberships")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    paid_fee = models.BooleanField(default=False)

    class Meta:
        unique_together = ('group', 'customer')

class Participant(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    challenge = models.ForeignKey(QuestionandAnswerChallenge, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    nickname = models.CharField(max_length=50, null=True, blank=True)
    session_token = models.CharField(max_length=100, unique=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} in {self.challenge.title}"


class Answer(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField()
    answered_at = models.DateTimeField(default=timezone.now)
    time_taken = models.FloatField(help_text="Time in seconds")
    is_correct = models.BooleanField()
    total_score = models.FloatField(help_text="Total reward percentage")

    def __str__(self):
        return f"{self.participant.user.username} - {self.question.text}"

class Result(models.Model):
    participant = models.OneToOneField(Participant, on_delete=models.CASCADE)
    total_questions = models.IntegerField()
    correct_answers = models.IntegerField()
    total_score = models.FloatField(help_text="Total reward percentage") #cumulative

    def __str__(self):
        return f"{self.participant.user.username} - {self.total_score}%"
