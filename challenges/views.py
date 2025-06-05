from django.shortcuts import render, redirect
from django.db.models import Count, Q

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import RefferalChallenge, RefferalChallengeResult, Vote, VoteChallengeParticipant, VoteChallenge, VoteChallengePartner
from points.models import LoyaltyPoint,  LoyaltyPointsCategory
from customers.models import Customer
from businesses.models import Business, Staff
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

@login_required(login_url="/accounts/login-user/")
def create_vote_challenge(request):
    business_id = request.GET.get('business_id', '')

    business = Business.objects.filter(id=business_id).first()
    staff = None
    if business:
        staff = Staff.objects.filter(business=business, user=request.user).first()
    if request.method == 'POST':
        challenge_name = request.POST['challenge_name'] # will install phonenumber and check if number is valid and convert it to international format
        participating_reward = request.POST['participating_reward']
        challenge_reward = request.POST['challenge_reward']
        challenge_reward_monetary_value = request.POST['challenge_reward_monetary_value']
        challenge_brief = request.POST['challenge_brief']
        challenge_guidelines = request.POST['challenge_guidelines']
        target_winners = request.POST['target_winners']
        end_date = request.POST['end_date']
        
        challenge=VoteChallenge.objects.create(
            challenge_owner=business, 
            created_by=staff, 
            challenge_name=challenge_name, 
            participating_reward=participating_reward, 
            challenge_reward=challenge_reward, 
            challenge_reward_monetary_value=challenge_reward_monetary_value, 
            challenge_brief=challenge_brief, 
            challenge_guidelines=challenge_guidelines, 
            target_winners=target_winners, 
            end_date=end_date
            )
        
        
        messages.error(request, "Challenge created successfuly.")
        messages.success(request, "create a poster promoting the challenge")
        messages.success(request, "invite others businesses to patner and promote this challenge in their stores")
        return redirect('view_vote_challenge', challenge.id)
    context= {
        'business': business,
        }
    return render(request, 'challenges/create-vote-challenge.html',  context)

@login_required(login_url="/accounts/login-user/")
def business_vote_challenges(request, slug):
    business = Business.objects.filter(slug=slug).first()
    staff = None
    if business:
        staff = Staff.objects.filter(business=business, user=request.user).first()
    challenges = VoteChallenge.objects.filter(challenge_owner=business).annotate(total_applications=Count('vote_challenges'))
    context= {
        'business': business,
        'challenges': challenges,
        'staff': staff
        }
    return render(request, 'challenges/business-vote-challenge.html',  context)

@login_required(login_url="/accounts/login-user/")
def invite_vote_challenge_patners(request):
    business_slug = request.GET.get('business_slug', '')
    challenge_id = request.GET.get('challenge_id', '')
    patner_id = request.GET.get('patner_id', '')

    if business_slug == '':
        return redirect('profile')
    if challenge_id == '':
        return redirect('business_vote_challenges', business_slug)
    
    businesses = Business.objects.filter(owner=request.user)
    business = businesses.filter(slug=business_slug).first()
    if not business:
        return redirect('profile')

    all_businesses = Business.objects.all().exclude(slug=business_slug)
    staff = Staff.objects.filter(business=business, user=request.user).first()
    if not staff:
        return redirect('profile')
    challenge = VoteChallenge.objects.filter(id=challenge_id, challenge_owner=business).first()
    if not challenge:
        return redirect('business_vote_challenges', business_slug)
    if patner_id !='':
        patner = all_businesses.filter(id=patner_id).first()
        if not patner:
            messages.success(request, "Business patner does not exist reselect again")
        else:
            if VoteChallengePartner.objects.filter(partner=patner).exists():
                messages.success(request, "Partner Already invited")
            else:
                VoteChallengePartner.objects.create(
                    challenge = challenge,
                    partner = patner
                )
                challenge.challenge_patners.add(patner)
                challenge.save()
                messages.success(request, "Initation has been successfull sent")
                messages.success(request, "Awaiting patner to accept")


    context= {
        'all_businesses': all_businesses,
        'businesses': businesses,
        'business': business,
        'challenge': challenge,
        'staff': staff
        }
    return render(request, 'challenges/patners-page.html',  context)


@login_required(login_url="/accounts/login-user/")
def challenge_patnership_invite(request, slug):
    business = Business.objects.filter(slug=slug).first()
    staff = None
    if business:
        staff = Staff.objects.filter(business=business, user=request.user).first()
    partner_challenges = VoteChallengePartner.objects.filter(
        Q(partner=business) | Q(challenge__challenge_owner=business)
    )
    context= {
        'business': business,
        'partner_challenges': partner_challenges,
        'staff': staff
        }
    return render(request, 'challenges/challenge-patnership-invite.html',  context)