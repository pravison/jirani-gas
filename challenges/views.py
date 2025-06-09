from django.shortcuts import render, redirect
from django.db.models import Count, Q
from django.utils.timezone import now
from datetime import datetime, date
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
    file_url = f"https://drive.google.com/uc?id={file.get('id')}"
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
    if not image_file:
        return JsonResponse({'error': 'No image uploaded'}, status=400)

    try:
        image_url = upload_image_to_google_drive(image_file)
        joining = VoteChallengeParticipant.objects.create(
            challenge=challenge,
            participant=customer,
            results_image_url=image_url,
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
            'redirect_url': f'/challenges/vote-challenge-participant/{joining.id}/'
        })

    except Exception as e:
        import traceback
        traceback.print_exc()  # Logs to console/logs
        return JsonResponse({'error': str(e)}, status=500)


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