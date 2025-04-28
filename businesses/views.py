from django.shortcuts import render, redirect
from django.db.models import Count, Sum, Q, Prefetch, Subquery, OuterRef
import os
from django.conf import settings
from django.http import HttpResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, date, timedelta
from django.contrib.auth.models import User
import uuid
from django.utils.text import slugify
from .models import Business, Staff
from points.models import LoyaltyPointsCategory, LoyaltyPoint
from customers.models import Customer, ScanCount
from store.models import Product
from .decorators import team_member_required

import random
from django.http import JsonResponse
from django.core.mail import send_mail

import qrcode
from PIL import Image, ImageDraw, ImageFont


from io import BytesIO
import base64

# from . forms import EditLoyaltyPointsCategoryForm
# Create your views here.

@login_required(login_url="/accounts/login-user/")
def add_business(request):
    pricing_plan = request.GET.get('pricing_plan') or ''
    if pricing_plan == '':
        messages.success(request, 'Choose Pricing Plan First')
        return redirect('pricing')
    context = {
         'pricing_plan': pricing_plan
    }
    if request.method == "POST":
        business_name = request.POST.get('business_name')
        phone_number = request.POST.get('phone_number')
        county = request.POST.get('county')
        location = request.POST.get('location')
        ward = request.POST.get('ward')
        address = request.POST.get('address')
        description = request.POST.get('description')

        if Business.objects.filter(business_name=business_name).exists():
            messages.success(request, 'Business Name  already exists.')
            messages.success(request, 'Choose another name or add some letters!')
            return redirect('add_business')

        owner =request.user
        slug=slugify(business_name)
        subscription_plan = pricing_plan
        business = Business.objects.create(business_name=business_name, slug=slug, phone_number=phone_number, county=county, location=location, ward=ward, address=address, description=description, owner=owner, subscription_plan=subscription_plan)
        
        # login user
        customer = Customer.objects.filter(user=request.user).first()
        if not customer:
            customer = Customer.objects.create(user=request.user)
        business.customers.add(customer) 
        if not Staff.objects.filter(user=request.user, business=business).exists():
                Staff.objects.create(
                    user=request.user,
                    business=business
                )
        
        messages.success(request, 'Business Account Created Successfuly')  
        return redirect('dashboard', slug)
    
    return render(request, 'business/add-business.html', context)

@login_required(login_url="/accounts/login-user/")
def business(request):
    businesses = Business.objects.filter(owner=request.user)
    if not businesses:
        messages.success("You haven't created any business account. create one !!! by clicking create new business")
        return redirect('profile')
    businesses_count = businesses.count()
    business = businesses.first()
    if businesses_count == 1:
        return redirect('dashboard', business.slug)
    
    staff = Staff.objects.filter(user=request.user, business=business).first()

    
    context = {
        'businesses': businesses,
        'business': business,
        'staff': staff,
    }
    return render(request, 'business/business.html', context)

@login_required(login_url="/accounts/login-user/")
@team_member_required
def dashboard(request, slug):
    today = date.today()
    businesses = Business.objects.filter(owner=request.user)
    business = Business.objects.filter(slug=slug).first()
    staff = Staff.objects.filter(business=business, user=request.user)
    total_customers = Customer.objects.filter(business=business).count()
    context={
        'businesses': businesses,
        'business': business,
        'staff': staff,
        'total_customers' : total_customers
    }
    return render(request, 'business/dashboard.html', context)

@login_required(login_url="/accounts/login-user/")
@team_member_required
def add_staff(request, slug):
    url=f'/register-user/?add_staff_to={slug}'
    return redirect(url)



@login_required(login_url="/accounts/login-user/")
@team_member_required
def customers(request, slug):
    businesses = Business.objects.filter(owner=request.user)
    business = Business.objects.filter(slug=slug).first()
    customers = business.customers.all()
    staff = Staff.objects.filter(business=business, user=request.user)
    
    context={
        'businesses': businesses,
        'business': business,
        'customers':customers, 
        'staff' : staff
    }
    return render(request, 'business/customers.html', context)

def generate_unique_code():
    while True:
        code = uuid.uuid4().hex[:6]
        if not RefferralCode.objects.filter(code=code).exists():
            return code
        

@login_required(login_url="/accounts/login-user/")
def view_coupon(request, slug):
    coupon_id = request.GET.get('coupon_id')
    businesses = Business.objects.filter(owner=request.user)
    business = Business.objects.filter(slug=slug).first()
    coupon = Coupone.objects.filter(id=coupon_id).first()
    staff = Staff.objects.filter(business=business, user=request.user)
    today = date.today()

    # we are quering the latest featured challenge
     # will work on it later 
    challenge = StoreChallenge.objects.filter(
                    business=business,

                    closed=False
                ).last()

    qr_url = f"{request.scheme}://{request.get_host()}/business/add-coupon/?coupone_code={coupon.code}"  # URL to lock the code

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=2.5, border=1)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    # Save QR code to memory
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_code_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    context = {
        # 'company_name': company_name,
        # 'coupon_code': coupon_code,
        # 'coupon_image_name': f"coupons/{coupon_image_name}",
        'qr_code_image': qr_code_image,
        'businesses': businesses,
        'staff': staff,
        'business': business,
        'coupon':coupon,
        'today':today,
        'challenge': challenge
    }
    return render(request, 'business/view_coupon.html', context)


@login_required(login_url="/accounts/login-user/")
@team_member_required
def create_store_challenge(request, slug):
    business = Business.objects.filter(slug=slug).first()
    staff = Staff.objects.filter(user=request.user, business=business).first()
    if staff is None:
        messages.success(request, 'have No permission to create coupones ')
        return redirect('profile')
    if request.method == "POST":
        challenge_type = request.POST.get('challenge_type')
        challenge_name = request.POST.get('challenge_name')
        challenge_reward = request.POST.get('challenge_reward')
        target_winners = request.POST.get('target_winners')
        day_of_the_challenge = request.POST.get('day_of_the_challenge')
            
        StoreChallenge.objects.create(
            business=business,
            challenge_type = challenge_type,
            challenge_name = challenge_name,
            challenge_reward = challenge_reward,
            target_winners = target_winners,
            day_of_the_challenge = day_of_the_challenge,
            created_by=staff
        )
        messages.success(request, 'challenge created successfuly')  
        return redirect('store_challenges', slug)
    context = {
        'business': business,
        'staff': staff
    }
    return render(request, 'business/create-challenge.html', context)

@login_required(login_url="/accounts/login-user/")
@team_member_required
def store_challenges(request, slug):
    update = request.GET.get('update') or ''
    businesses = Business.objects.filter(owner=request.user)
    business = Business.objects.filter(slug=slug).first()
    challenges = StoreChallenge.objects.filter(business=business).order_by('-id')
    staff = Staff.objects.filter(business=business, user=request.user)
    if update != '':
        challenge = StoreChallenge.objects.filter(id=update).first()
        if challenge.closed == False:
            messages.success(request, "NOT allowed to update challenge status")
            # challenge.closed = True
            # challenge.save()
        else:
            messages.success(request, "NOT allowed to update challenge status")
            # challenge.closed = False
            # challenge.save()
        return redirect('store_challenges', slug)
    context={
        'businesses': businesses,
        'business': business,
        'challenges':challenges,
        'staff': staff
    }
    return render(request, 'business/store-challenges.html', context)


@login_required(login_url="/accounts/login-user/")
def view_store_challenge(request, slug):
    challenge_id = request.GET.get('challenge_id')
    select_winners = request.GET.get('select_winners') or ''
    next_url = request.GET.get('next_url') or ''
    businesses = Business.objects.filter(owner=request.user)
    business = Business.objects.filter(slug=slug).first()
    challenge = StoreChallenge.objects.filter(id=challenge_id).first()
    staff = Staff.objects.filter(business=business, user=request.user)

    qr_url = f"{request.scheme}://{request.get_host()}/business/{slug}/stand-a-chance-to-win/?challenge_id={challenge_id}"  # URL to lock the code

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    # Save QR code to memory
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_code_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    if select_winners !='':
        #check if winners already selceted 
        # check if today is greator than challenge date 
        #  randomly select winners from participants
        try:
            # Fetch the challenge
            challenge = StoreChallenge.objects.get(id=challenge_id)
            
            if challenge.closed:
                messages.success(request, "Challenge already closed !!!")
                if next_url !='':
                    return redirect(next_url)
                else:
                    return redirect('store_challenges', slug)

            # Get all participants related to this challenge
            participants = list(challenge.participants.all())
            
            if not participants:
                messages.success(request, "No participants found for this challenge!!!")
                if next_url !='':
                    return redirect(next_url)
                else:
                    return redirect('store_challenges', slug)
            # check if number of participants is less than target winners and return telling owner to add more participants
            if challenge.target_winners > len(participants):
                messages.success(request, "participants are less than target winners !!!")
                messages.success(request, "Add more participants !!!")
                if next_url !='':
                    return redirect(next_url)
                else:
                    return redirect('store_challenges', slug)
            # Determine the number of winners to select
            num_winners = min(challenge.target_winners, len(participants))
            # later on i will come to prevent selecting winners if participants are less than target winners
            # Randomly select winners
            selected_winners = random.sample(participants, num_winners)

            # Add winners to the winners field
            challenge.winners.set(selected_winners)

            # Return the winners' IDs or any other relevant info
            messages.success(request, "Winners Have been Succefully selected !!!")
            # Mark challenge as closed
            challenge.closed = True
            challenge.save()

        except StoreChallenge.DoesNotExist:
            messages.success(request, "Challenge Does not Exists !!!")
        if next_url !='':
            return redirect(next_url)
        else:
            return redirect('store_challenges', slug)

    context={
        'qr_code_image': qr_code_image,
        'businesses': businesses,
        'staff': staff,
        'business': business,
        'challenge':challenge
    }
    return render(request, 'business/view-store-challenges.html', context)

def add_challenge_participant(request, slug):
    challenge_id = request.GET.get('challenge_id')
    # businesses = Business.objects.filter(owner=request.user) or None
    business = Business.objects.filter(slug=slug).first()
    challenge = StoreChallenge.objects.filter(id=challenge_id).first()
    # staff = Staff.objects.filter(business=business, user=request.user) or None
    today = date.today()
    coupon = ''

    if challenge.closed:
        messages.success(request, f"visit {business.business_name} @ {business.address} for More Information!!!")
    else:
        coupones = Coupone.objects.filter(business=business, used=False).order_by('-id')
        valid_coupons = [c for c in coupones if c.expiry_date >= datetime.now().date()]

        existing_participants = set(challenge.participants.all())  # Convert to set for fast lookup
        available_coupons = [c for c in valid_coupons if c not in existing_participants]

        if not available_coupons:
            messages.success(request, f"Visit {business.business_name} @ {business.address} for more information!")
        else:
            # Randomly select a coupon that is not already a participant
            coupon = random.choice(available_coupons)
            challenge.participants.add(coupon)  # Add the selected coupon to participants

    context={
        # 'businesses': businesses,
        # 'staff': staff,
        'today': today,
        'business': business,
        'challenge':challenge,
        'coupon': coupon
    }
    return render(request, 'business/add-challenge-participant.html', context)

def generate_unique_refferal_code():
    while True:
        code = uuid.uuid4().hex[:4]
        if not RefferralCode.objects.filter(code=code).exists():
            return code
        

@login_required(login_url="/accounts/login-user/")
def create_refferal_code(request, slug):
    business = Business.objects.filter(slug=slug).first()
    customer = Customer.objects.filter(user=request.user).first()
    next_url = request.GET.get('next_url') or ''
    if business is None:
        messages.success(request, 'There was an error generating your refferal please try again!!! ')
        if next_url !='':
            return redirect(next_url)
        return redirect('profile')

    if customer is None:
        customer = Customer.objects.create(user=request.user)
        if customer not in business.customers.all():
            business.customers.add(customer)
        refferal_code = RefferralCode.objects.create(
            customer=customer,
            business = business,
            code = generate_unique_refferal_code()
        )
        messages.success(request, 'Refferal Code Generated Succesfully!!! ')
        messages.success(request, f'your refferal code is {refferal_code.code}!!! ') 
    else:
        if customer not in business.customers.all():
            business.customers.add(customer)
        if not RefferralCode.objects.filter(customer=customer, business=business).exists():
            refferal_code = RefferralCode.objects.create(
            customer=customer,
            business = business,
            code = generate_unique_refferal_code()
            )
            messages.success(request, 'Refferal Code Generated Succesfully!!! ')
            messages.success(request, f'your refferal code is {refferal_code.code}!!! ') 
        else:
            messages.success(request, 'already have a refferal code!!! ')
    if next_url !='':
        return redirect(next_url)
    return redirect('profile')

@login_required(login_url="/accounts/login-user/")
@team_member_required
def loyalty_points_category(request, slug):
    businesses = Business.objects.filter(owner=request.user)
    business = Business.objects.filter(slug=slug).first()
    staff = Staff.objects.filter(business=business, user=request.user)
    loyalty_categories = LoyaltyPointsCategory.objects.filter(business=business)
    context={
        'businesses': businesses,
        'business': business,
        'staff': staff,
        'loyalty_categories': loyalty_categories
    }
    return render(request, 'business/loyalty-points-category.html', context)



@login_required(login_url="/accounts/login-user/")
@team_member_required
def edit_loyalty_category(request, slug):
    id = request.GET.get('id') or ''
    if id == '':
        messages.success(request, "There was error editing loyalty category please reselect and try again")
        return ('loyalty_points_category', business.slug)
    businesses = Business.objects.filter(owner=request.user)
    business = Business.objects.filter(slug=slug).first()
    staff = Staff.objects.filter(business=business, user=request.user).first()
    loyalty_category = LoyaltyPointsCategory.objects.filter(id=id).first()
    if request.method == 'POST':
        # form = EditLoyaltyPointsCategoryForm(request.POST, instance=loyalty_category)
        if form.is_valid():
            instance=form.save(commit=False)
            instance.edited_by= staff
            instance.save()
            messages.success(request, "Editted succesfully")
            return redirect('loyalty_points_category', slug)
            
    else:
        # form = EditLoyaltyPointsCategoryForm(instance=loyalty_category)
        context = {
            'businesses': businesses,
            'business': business,
            'staff': staff,
            # 'form': form,
            'loyalty_category':loyalty_category
        }
        return render(request, 'business/edit-loyalty-category.html', context)
    
@login_required(login_url="/accounts/login-user/")
@team_member_required
def add_loyalty_points_to_customer(request, slug):
    businesses = Business.objects.filter(owner=request.user)
    business = Business.objects.filter(slug=slug).first()
    staff = Staff.objects.filter(business=business, user=request.user).first()
    loyalty_categories = LoyaltyPointsCategory.objects.filter(business=business)
    if request.method == 'POST':
        category_name = request.POST.get('category')
        purchase_value = request.POST.get('purchase_value')
        phone_number = request.POST.get('phone_number')

        loyalty_category = LoyaltyPointsCategory.objects.filter(business=business, category=category_name).first()
        earned_points = int(int(purchase_value)/int(loyalty_category.total_value_for_a_point))

        phone_number =str(254)+str(phone_number)
        phone_number = int(phone_number)
        customer = Customer.objects.filter(phone_number=phone_number).first()
        if customer:
            business_customer = BusinessCustomer.objects.filter(business=business, customer=customer).first()
            if business_customer is None:
                business_customer = BusinessCustomer.objects.create(business=business, customer = customer)
            
            if customer not in business.customers.all():
                business.customers.add(customer)
            business.customers.add(customer)
            LoyaltyPoint.objects.create(
                business=business,
                customer = customer,
                category=loyalty_category,
                purchase_value=purchase_value,
                points_earned=earned_points,
                added_by = f'{request.user.first_name} {request.user.last_name}' 
            )

            if business_customer.reffered_by is not None:
                customer_reffery = Customer.objects.filter(user=business_customer.reffered_by).first()
                if customer_reffery:
                    points_category = LoyaltyPointsCategory.objects.filter(business=business, category='points from refferal sales').first()
                    if not points_category:
                        points_category = LoyaltyPointsCategory.objects.create(
                            business = business,
                            category = 'points from refferal sales',
                            total_value_for_a_point = int(1),
                            )
                    LoyaltyPoint.objects.create(
                        business=business,
                        customer = customer_reffery,
                        category=points_category,
                        purchase_value=int(0),
                        points_earned=int(50), # will rewrite the code to make these part dynamic
                        added_by = f'{customer.user.first_name} {customer.user.last_name}' 
                    )
            messages.success(request, "points added succesfully")
            return redirect('loyalty_points', slug)
        else:
            messages.success(request, "customer does not exists")
            messages.success(request, "add customer to the database first before adding points or countercheck if phone number is correct")
            return redirect('add_loyalty_points_to_customer', slug)
    
        

    context = {
        'businesses': businesses,
        'business': business,
        'staff': staff,
        'loyalty_categories':loyalty_categories
    }
    return render(request, 'business/add-loyalty-points.html', context)