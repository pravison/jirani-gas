from django.shortcuts import render, redirect
from django.db.models import Count, Q
from django.utils.timezone import now
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db import transaction
from datetime import date
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
    
    last_day = challenge.end_date  # example
    current_time = now()
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
        'participating': participating ,
        'current_time': current_time,
        'last_day': last_day
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
    #curent date and time
    last_day = challenge.end_date  # example
    current_time = now()
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
        'participating': participating,
        'current_time': current_time,
        'last_day': last_day
    }
    return render(request, 'challenges/view-vote-challenge.html', context)


from django.views.decorators.http import require_POST
import io
import os
import json
from django.http import JsonResponse
from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Upload image to Google Drive
def upload_image_to_google_drive(image_file):
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    creds_json = os.environ.get("GOOGLE_DRIVE_CREDS_JSON")
    if not creds_json:
        raise Exception("GOOGLE_DRIVE_CREDS_JSON not found in environment variables")

    credentials = service_account.Credentials.from_service_account_info(
        json.loads(creds_json),
        scopes=SCOPES
    )
    # Load credentials from settings (already defined in .env or settings.py)
    # credentials = service_account.Credentials.from_service_account_file(
    # settings.GOOGLE_DRIVE_CREDENTIALS_FILE,
    # scopes=SCOPES
    # )

    # Build the Drive API client
    drive_service = build('drive', 'v3', credentials=credentials)

    # Optional: add your folder ID here if you want to upload into a specific folder
    folder_id = getattr(settings, 'GOOGLE_DRIVE_FOLDER_ID', None)

    file_metadata = {
        'name': image_file.name,
    }
    if folder_id:
        file_metadata['parents'] = [folder_id]

    # Upload the image
    media = MediaIoBaseUpload(io.BytesIO(image_file.read()), mimetype=image_file.content_type)
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    # Make file public
    drive_service.permissions().create(
        fileId=file.get('id'),
        body={'role': 'reader', 'type': 'anyone'},
    ).execute()

    # Return the public URL of the uploaded file
    file_url = f"https://drive.google.com/uc?export=view&id={file.get('id')}"
    return file_url



# Join challenge
@login_required(login_url="/accounts/login-user/")
@require_POST
def join_vote_challenge(request, id):
    challenge = VoteChallenge.objects.filter(id=id).first()
    if not challenge:
        return JsonResponse({'error': 'Challenge not found'}, status=404)

    customer = Customer.objects.filter(user=request.user).first()
    if not customer:
        customer = Customer.objects.create(
            user=request.user,
            phone_number=request.user.username,
            refferal_code=generate_unique_refferal_code()
        )

    if VoteChallengeParticipant.objects.filter(challenge=challenge, participant=customer).exists():
        return JsonResponse({'error': 'You already joined this challenge'}, status=400)

    image_file = request.FILES.get('entry_image')
    text_results = request.FILES.get('entry_text') or ''
    if  challenge.type_of_results == 'image':
        if not image_file:
            return JsonResponse({'error': 'No image uploaded'}, status=400)
    else:
        if not text_results:
            return JsonResponse({'error': 'No text submitted'}, status=400)
    try:
        image_url = upload_image_to_google_drive(image_file)
        joining = VoteChallengeParticipant.objects.create(
            challenge=challenge,
            participant=customer,
            results_image_url=image_url,
            results_text = text_results,
            received_reward=f'{challenge.participating_reward} points'
        )

        category, _ = LoyaltyPointsCategory.objects.get_or_create(
            category='points for joining a challenge'
        )
        LoyaltyPoint.objects.create(
            customer=customer,
            category=category,
            points_earned=challenge.participating_reward,
            points_were='earned',
            added_by='automatically during joining a challenge'
        )

        return JsonResponse({
            'success': True,
            'redirect_url': f'/challenges/view-vote-challenge-participant/{joining.id}/'
        })

    except Exception as e:
        import traceback
        traceback.print_exc()  # Logs to console/logs
        return JsonResponse({'error': str(e)}, status=500)


def view_vote_challenge_participant(request, id):
    participant = VoteChallengeParticipant.objects.filter(id=id).first()
    if not participant:
        return redirect('vote_challenge_opportunities')
    #check if user is participating in the challenge
    customer = None
    if request.user.is_authenticated:
        customer = Customer.objects.filter(user=request.user).first()
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
        type_of_results = request.POST['type_of_results']
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
            type_of_results = type_of_results,
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
    challenge_patners = VoteChallengePartner.objects.filter(challenge=challenge)
    if not challenge:
        return redirect('business_vote_challenges', business_slug)
    if patner_id !='':
        patner = all_businesses.filter(id=patner_id).first()
        if not patner:
            messages.success(request, "Business patner does not exist reselect again")
        else:
            if challenge_patners.filter(partner=patner).exists():
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
    challenge_partner_id = request.GET.get('challenge_partner_id', '')
    staff = None
    if business:
        staff = Staff.objects.filter(business=business, user=request.user).first()
    partner_challenges = VoteChallengePartner.objects.filter(
        Q(partner=business) | Q(challenge__challenge_owner=business)
    )
    if challenge_partner_id !='':
        challenge_patner = partner_challenges.filter(id=challenge_partner_id).first()
        if challenge_patner:
            challenge_patner.accepted = True
            challenge_patner.date_accepted = date.today()
            challenge_patner.save()
    context= {
        'business': business,
        'partner_challenges': partner_challenges,
        'staff': staff
        }
    return render(request, 'challenges/challenge-patnership-invite.html',  context)

# Join challenge


# Assuming these models are defined in your models.py
# from .models import Customer, VoteChallenge, VoteChallengeParticipant, LoyaltyPointsCategory, LoyaltyPoint

# Assuming generate_unique_refferal_code and upload_image_to_google_drive are defined elsewhere
# from .utils import generate_unique_refferal_code, upload_image_to_google_drive

# --- NEW VIEW FOR CASTING VOTES ---

@login_required(login_url="/accounts/login-user/")
@require_POST
def cast_vote_for_participant(request, id):
    """
    Handles the logic for casting votes for a specific participant in a vote challenge.

    Arguments:
        request: The HttpRequest object.
        id: The ID of the VoteChallengeParticipant.

    Expected POST data:
        - 'number_of_votes': The integer number of votes the customer wants to cast.
        - 'participant_id': The ID of the VoteChallengeParticipant being voted for.
    """
    # 1. Retrieve Challenge and Customer
    challenge_participant = get_object_or_404(VoteChallengeParticipant, id=id)
    customer = Customer.objects.filter(user=request.user).first()

    # If customer profile doesn't exist for a logged-in user, create one.
    if not customer:
        customer = Customer.objects.create(
            user=request.user,
            phone_number=request.user.username,
            refferal_code=generate_unique_refferal_code() # Ensure this utility function exists
        )

    # 2. Get and Validate Input from POST data
    number_of_votes_str = request.POST.get('number_of_votes')
    participant_id_str = request.POST.get('participant_id')

    if not number_of_votes_str or not participant_id_str:
        return JsonResponse({'error': 'Number of votes and participant ID are required.'}, status=400)

    try:
        number_of_votes = int(number_of_votes_str)
        participant_pk = int(participant_id_str)
        participant_pk == id
    except ValueError:
        return JsonResponse({'error': 'Invalid number of votes or participant ID.'}, status=400)

    if number_of_votes <= 0:
        return JsonResponse({'error': 'Number of votes must be a positive number.'}, status=400)

    # 3. Server-Side Validation: Check if customer has enough votes
    if customer.total_available_votes < number_of_votes:
        return JsonResponse(
            {'error': f'You only have {customer.total_available_votes} votes available. You cannot cast {number_of_votes} votes.'},
            status=400
        )

    # 5. Perform Atomic Transaction to Update Votes
    try:
        with transaction.atomic():
            # Deduct votes from the casting customer's available votes
            customer.total_available_votes -= number_of_votes
            customer.save()

            # Add the cast votes to the target participant's vote count
            challenge_participant.total_votes += number_of_votes
            challenge_participant.save()

            # Optional: You might want to record this voting transaction for auditing
            Vote.objects.create(
            challenge_participant = challenge_participant,
            voter = customer,
            number_of_votes = number_of_votes,
            date_voted = date.today()
            )
            
            messages.success(request, f"Thanks for supporting {challenge_participant.participant}")
            messages.success(request, "You can also participate in challenges and win bountiful rewards")
            return JsonResponse({
                'success': True,
                'message': f'Successfully cast {number_of_votes} votes for {challenge_participant.participant}!',
                # Redirect back to the challenge detail page or a success page
                'redirect_url': f'/challenges/vote-challenge-opportunities/'
            })

    except Exception as e:
        # Log the exception for debugging purposes
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': 'An internal server error occurred while processing your vote.'}, status=500)
    
@login_required(login_url="/accounts/login-user/")
@require_POST
def purchase_votes(request):
    """
    Handles the logic for purchasing votes using customer loyalty points.

    Expects 'votes_to_purchase' in the POST data.
    """
    # Define the conversion rate
    POINTS_PER_VOTE = 10 

    customer = Customer.objects.filter(user=request.user).first()

    # If customer profile doesn't exist for a logged-in user, create one.
    # This scenario is less common for purchasing, as they'd typically have a profile
    # if they have loyalty points. But it's good for robustness.
    if not customer:
        customer = Customer.objects.create(
            user=request.user,
            phone_number=request.user.username,
            refferal_code=generate_unique_refferal_code() # Ensure this utility function exists
        )

    # 1. Get and Validate Input from POST data (votes to purchase)
    votes_to_purchase_str = request.POST.get('votes_to_purchase') # Expecting 'votes_to_purchase' from frontend

    if not votes_to_purchase_str:
        return JsonResponse({'success': False, 'error': 'Number of votes to purchase is required.'}, status=400)

    try:
        votes_to_purchase = int(votes_to_purchase_str)
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid number of votes.'}, status=400)

    if votes_to_purchase <= 0:
        return JsonResponse({'success': False, 'error': 'Number of votes must be a positive number.'}, status=400)

    # Calculate points required for the purchase
    points_required = votes_to_purchase * POINTS_PER_VOTE

    # 2. Server-Side Validation: Check if customer has enough loyalty points
    if customer.total_loyalty_points < points_required:
        return JsonResponse(
            {
                'success': False,
                'error': f'Insufficient loyalty points. You need {points_required} points to purchase {votes_to_purchase} votes, but you only have {customer.total_loyalty_points} points.'
            },
            status=400
        )

    # 3. Perform Atomic Transaction to update customer's points and votes
    try:
        with transaction.atomic():
            # Deduct loyalty points from the customer
            customer.total_loyalty_points -= points_required
            
            # Add the purchased votes to the customer's available votes
            customer.total_available_votes += votes_to_purchase
            customer.save()

            # Optional: Log the loyalty points transaction (if you have a LoyaltyPoint model)
            # Make sure your LoyaltyPoint model has a 'points_spent' field or similar for deductions
            category, _ = LoyaltyPointsCategory.objects.get_or_create(
                category='points spent for votes purchase'
            )
            LoyaltyPoint.objects.create(
                customer=customer,
                category=category,
                points_redeemed=points_required, # Assuming this field exists and tracks deductions
                points_were='redeemed',
                added_by='automatically during vote purchase'
            )
            
            # Add Django messages for user feedback (optional, if you're using messages framework)
            messages.success(request, f"Successfully purchased {votes_to_purchase} votes for {points_required} points!")
            messages.info(request, f"You now have {customer.total_available_votes} votes available and {customer.total_loyalty_points} loyalty points remaining.")
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully purchased {votes_to_purchase} votes for {points_required} points!',
                'new_loyalty_points': customer.total_loyalty_points, # Send updated points back to frontend
                'new_available_votes': customer.total_available_votes, # Send updated votes back to frontend# Redirect back or to a suitable page
            })

    except Exception as e:
        # Log the exception for debugging purposes
        import traceback
        traceback.print_exc()
        # Return a generic error message to the client
        return JsonResponse({'success': False, 'error': 'An internal server error occurred while processing your purchase.'}, status=500)


# Q & A challenge view
from .models import Topic, Subtopic, Question, Choice, QuestionandAnswerChallenge, Group, GroupMembership, Participant, Answer, Result
# def join_challenge(request, challenge_id):
#     challenge = get_object_or_404(QuestionandAnswerChallenge, id=challenge_id)
#     customer = request.user.customer

#     # Check if already participating
#     if Participant.objects.filter(challenge=challenge, customer=customer).exists():
#         return Response({'message': 'Already joined'}, status=400)

#     # Check group requirement
#     if challenge.requires_group:
#         return Response({'message': 'This challenge requires a group. Join or create one first.'}, status=400)

#     participant = Participant.objects.create(
#         customer=customer,
#         challenge=challenge,
#         session_token=uuid.uuid4().hex
#     )

#     return Response({'message': 'Joined challenge', 'token': participant.session_token})

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def join_group(request, challenge_id, group_id):
#     challenge = get_object_or_404(QuestionandAnswerChallenge, id=challenge_id)
#     group = get_object_or_404(Group, id=group_id, challenge=challenge)
#     customer = request.user.customer

#     # Check if already in group
#     if GroupMembership.objects.filter(group=group, customer=customer).exists():
#         return Response({'message': 'Already in group'}, status=400)

#     if customer.points < 50:
#         return Response({'message': 'Not enough points to join group'}, status=400)

#     # Deduct fee and join
#     customer.points -= 50
#     customer.save()

#     GroupMembership.objects.create(group=group, customer=customer, paid_fee=True)

#     return Response({'message': f'Joined group {group.name}'})

@login_required(login_url="/accounts/login-user/")
def create_qna_challenge(request):
    business_id = request.GET.get('business_id', '')
    business = Business.objects.filter(id=business_id).first()
    staff = None
    if business:
        staff = Staff.objects.filter(business=business, user=request.user).first()

    subtopics = Subtopic.objects.prefetch_related('questions').all()

    if request.method == 'POST':
        title = request.POST['title']
        subtopic_id = request.POST['subtopic']
        duration_seconds = request.POST['duration_seconds']
        type = request.POST['type']
        requires_group = 'requires_group' in request.POST
        challenge_reward = request.POST['challenge_reward']
        challenge_reward_monetary_value = request.POST['challenge_reward_monetary_value']
        challenge_brief = request.POST['challenge_brief']
        challenge_guidelines = request.POST['challenge_guidelines']
        target_winners = request.POST['target_winners']
        end_date = request.POST['end_date']
        start_time = request.POST.get('start_time')

        challenge = QuestionandAnswerChallenge.objects.create(
            business=business,
            subtopic_id=subtopic_id,
            title=title,
            duration_seconds=duration_seconds,
            type=type,
            requires_group=requires_group,
            challenge_reward=challenge_reward,
            challenge_reward_monetary_value=challenge_reward_monetary_value,
            challenge_brief=challenge_brief,
            challenge_guidelines=challenge_guidelines,
            target_winners=target_winners,
            end_date=end_date,
            start_time=start_time if type == 'live' else None
        )

        messages.success(request, "Challenge created successfully.")
        return redirect('view_qna_challenge', challenge.id)

    context = {
        'business': business,
        'subtopics': subtopics,
    }
    return render(request, 'challenges/create-qna-challenge.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import QuestionandAnswerChallenge, Participant, Result, Group, GroupMembership, Customer

# List all QnA challenges
def qna_challenge_list(request):
    now = timezone.now()

    # Get only challenges that are not closed and still ongoing
    challenges = QuestionandAnswerChallenge.objects.filter(
        closed=False,
        end_date__gt=now
    ).order_by('-created_at')

    context = {
        'challenges': challenges,
        'now': now,
    }
    return render(request, 'challenges/qna_challenge_list.html', context)

# View specific challenge with details
@login_required
def view_qna_challenge(request, challenge_id):
    challenge = get_object_or_404(QuestionandAnswerChallenge, pk=challenge_id)

    customer = request.user.customer
    participant = Participant.objects.filter(customer=customer, challenge=challenge).first()
    participants = Participant.objects.filter(challenge=challenge).select_related('customer')

    winners = Result.objects.filter(
        participant__challenge=challenge
    ).order_by('-total_score')[:challenge.target_winners]

    context = {
        'challenge': challenge,
        'participants': participants,
        'participating': participant,
        'customer': customer,
        'winners': winners,
    }

    return render(request, 'challenges/view_qna_challenge.html', context)


# Join challenge view
@login_required
def join_qna_challenge(request, challenge_id):
    challenge = get_object_or_404(QuestionandAnswerChallenge, pk=challenge_id)
    customer = request.user.customer

    # Ensure customer hasn't already joined
    if Participant.objects.filter(customer=customer, challenge=challenge).exists():
        return redirect('view_qna_challenge', challenge_id=challenge.id)

    # Optionally handle group logic here
    participant = Participant.objects.create(
        customer=customer,
        challenge=challenge,
        session_token=f"{customer.id}-{timezone.now().timestamp()}"
    )
    return redirect('view_qna_challenge', challenge_id=challenge.id)


# View individual participant performance
@login_required
def view_qna_participant(request, participant_id):
    participant = get_object_or_404(Participant, pk=participant_id)
    result = Result.objects.filter(participant=participant).first()
    answers = participant.answer_set.select_related('question', 'choice')

    return render(request, 'challenges/view_qna_participant.html', {
        'participant': participant,
        'result': result,
        'answers': answers,
    })
