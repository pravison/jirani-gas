from django.shortcuts import render, redirect
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import RefferalChallenge, RefferalChallengeResult, Vote, VoteChallengeParticipant, VoteChallenge
from points.models import LoyaltyPoint,  LoyaltyPointsCategory
from customers.models import Customer
from accounts.views import generate_unique_refferal_code
# Create your views here.
def refferal_challenge_opportunities(request):
    vote_challenge = False
    challenges = RefferalChallenge.objects.all().annotate(total_applications=Count('refferal_challenges'))
    context = {
        'challenges': challenges,
        'vote_challenge': vote_challenge
    }
    return render(request, 'challenges/challenge-opportunities.html', context)

def view_refferal_challenge(request, id):
    challenge = RefferalChallenge.objects.filter(id=id).first()
    if not challenge:
        messages.success(request, 'challenge was not found reselect again')
        return redirect('refferal_challenge_opportunities')
    
    participants = RefferalChallengeResult.objects.filter(challenge=challenge).order_by('-total_refferals')
    winners = participants

    #check if user is participating in the challenge
    participating = None
    customer = None
    if request.user.is_authenticated:
        customer = Customer.objects.filter(user=request.user).first()
        
        if not customer:
            customer = Customer.objects.create(
                user=request.user,
                phone_number=request.user.username,  # username is the phone number
                referral_code=generate_unique_refferal_code()  # spelling fixed
            )

        participating = RefferalChallengeResult.objects.filter(customer=customer).first()

    context = {
        'challenge': challenge,
        'customer': customer,
        'participants': participants,
        'winners': winners, 
        'participating': participating 
    }
    return render(request, 'challenges/view-refferal-challenge.html', context)


@login_required(login_url="/accounts/login-user/")
def join_refferal_challenge(request, id):
    challenge = RefferalChallenge.objects.filter(id=id).first()
    if not challenge:
        messages.success(request, 'challenge was not found reselect again')
        return redirect('refferal_challenge_opportunities')

    customer = Customer.objects.filter(user=request.user).first()
    if not customer:
        customer = Customer.objects.create(
            user=request.user,
            phone_number=request.user.username,# username is the phone number
            refferal_code = generate_unique_refferal_code()
        )
    
    if RefferalChallengeResult.objects.filter(customer = customer).exists():
        messages.success(request, 'you are already participating in this challenge, try out another challenge')
    else:
        joining = RefferalChallengeResult.objects.create(
            challenge = challenge,
            customer = customer,
            received_reward = f'{challenge.participating_reward} points',
            updated_by = 'automatically updated'
        )
        points_category = LoyaltyPointsCategory.objects.filter(category='points for joining a challenge').first()
        if not points_category:
            points_category = LoyaltyPointsCategory.objects.create(
                category = 'points for joining a challenge'
                )

        LoyaltyPoint.objects.create(
            customer = customer,
            category = points_category or None,
            points_earned = challenge.participating_reward, 
            points_were = 'earned',
            added_by = 'automaticaly during joining a challenge'
            )
        messages.success(request, f'Congrats You have Received {challenge.participating_reward} points *** for participating in a challenge*** ')
        messages.success(request, f'your points will be approved after your first invite is confirmed')
    
    return redirect('view_refferal_challenge', id)

def vote_challenge_opportunities(request):
    vote_challenge = True
    challenges = VoteChallenge.objects.all().annotate(total_applications=Count('vote_challenges'))
    context = {
        'challenges': challenges,
        'vote_challenge': vote_challenge
    }
    return render(request, 'challenges/challenge-opportunities.html', context)

def view_vote_challenge(request, id):
    challenge = VoteChallenge.objects.filter(id=id).first()
    if not challenge:
        messages.success(request, 'challenge was not found reselect again')
        return redirect('vote_challenge_opportunities')
    
    participants = VoteChallengeParticipant.objects.filter(challenge=challenge).order_by('-total_votes')
    winners = participants

    #check if user is participating in the challenge
    participating = None
    customer = None
    if request.user.is_authenticated:
        customer = Customer.objects.filter(user=request.user).first()
        
        if not customer:
            customer = Customer.objects.create(
                user=request.user,
                phone_number=request.user.username,  # username is the phone number
                referral_code=generate_unique_refferal_code()  # spelling fixed
            )

        participating = participants.filter(participant=customer).first()

    context = {
        'challenge': challenge,
        'customer': customer,
        'participants': participants,
        'winners': winners, 
        'participating': participating 
    }
    return render(request, 'challenges/view-vote-challenge.html', context)


#joining vote challenge
@login_required(login_url="/accounts/login-user/")
def join_vote_challenge(request, id):
    challenge = VoteChallenge.objects.filter(id=id).first()
    if not challenge:
        messages.success(request, 'challenge was not found reselect again')
        return redirect('vote_challenge_opportunities')

    customer = Customer.objects.filter(user=request.user).first()
    if not customer:
        customer = Customer.objects.create(
            user=request.user,
            phone_number=request.user.username,# username is the phone number
            refferal_code = generate_unique_refferal_code()
        )
    
    if VoteChallengeParticipant.objects.filter(participant = customer).exists():
        messages.success(request, 'you are already participating in this challenge, try out another challenge')
    else:
        joining = VoteChallengeParticipant.objects.create(
            challenge = challenge,
            participant = customer,
            received_reward = f'{challenge.participating_reward} points'
        )
        points_category = LoyaltyPointsCategory.objects.filter(category='points for joining a challenge').first()
        if not points_category:
            points_category = LoyaltyPointsCategory.objects.create(
                category = 'points for joining a challenge'
                )

        LoyaltyPoint.objects.create(
            customer = customer,
            category = points_category or None,
            points_earned = challenge.participating_reward, 
            points_were = 'earned',
            added_by = 'automaticaly during joining a challenge'
            )
        messages.success(request, f'Congrats You have Received {challenge.participating_reward} points *** for participating in a challenge*** ')
        messages.success(request, f'your points will be approved after your first invite is confirmed')
        return redirect('view_vote_challenge_participant', joining.id)
    return redirect('vote_challenge_opportunities', id)



def view_vote_challenge_participant(request, id):
    participant = VoteChallengeParticipant.objects.filter(id=id).first()
    if not participating:
        return redirect('vote_challenge_opportunities')
    #check if user is participating in the challenge
    participating = None
    customer = None
    

    context = {
        'customer': customer,
        'participant': participant
    }
    return render(request, 'challenges/view-vote-challenge-participant.html', context)

#create vote challenge

def create_vote_challenge(request):
    next_url = request.GET.get('next', '')
    
    if request.method == 'POST':
        phone_number = request.POST['phone_number'] # will install phonenumber and check if number is valid and convert it to international format
        password = request.POST['password']
        
        username =str(254)+str(phone_number)
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)

            messages.success(request, 'Welcome, you have been logged in!')
            return redirect(next_url or 'profile')
     
        messages.error(request, "There was an error logging in. Please try again.")
        messages.success(request, "makesure you enter the correct phone number you signed up with")
        return redirect('login_user')

    return render(request, 'challenges/create-vote-challenge.html', {'next': next_url})
