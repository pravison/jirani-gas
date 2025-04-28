from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
# Create your views here.
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from django.core.mail import send_mail
from .models import PasswordResetCode
from .forms import RequestResetCodeForm, PasswordResetCodeForm
from django.contrib.auth.models import User
from points.models import LoyaltyPointsCategory, LoyaltyPoint
from customers.models import Customer

from businesses.models import Business, Staff
import uuid

def generate_unique_refferal_code():
    while True:
        refferal_code = uuid.uuid4().hex[:4]
        if not Customer.objects.filter(refferal_code=refferal_code).exists():
            return refferal_code
        



def request_reset_code(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)      
            # Generate or update the reset code
            reset_code, created = PasswordResetCode.objects.get_or_create(user=user)
            reset_code.code = str(uuid.uuid4().hex[:6])
            reset_code.is_valid = True
            reset_code.save()
            
            # Send email
            send_mail(
                'Your Password Reset Code',
                f'Your reset code is: {reset_code.code}',
                'noreply@example.com',
                [email],
            )
            messages.success(request, 'A reset code has been sent to your email and expires in ten minutes.')
            return redirect('verify_reset_code')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email.')
    else:
        form = RequestResetCodeForm()
    return render(request, 'home/request_reset_code.html')


def verify_reset_code(request):
    if request.method == 'POST':
        form = PasswordResetCodeForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'Error assessing your data counter check and try again')
            return redirect('verify_reset_code')
        code = form.cleaned_data['code']
        try:
            reset_code = PasswordResetCode.objects.filter(code=code, is_valid=True).order_by('created_at').last()
            if reset_code is None:
                messages.error(request, 'Counter check your code seems its incorrect')
                return redirect('verify_reset_code')
            if reset_code.is_expired():
                reset_code.is_valid = False
                reset_code.save()
                messages.error(request, 'This code has expired.')
                return redirect('request_reset_code')
            else:
                # Invalidate the code
                reset_code.is_valid = False
                reset_code.save()
                # Redirect to password reset form
                request.session['password_reset_user_id'] = reset_code.user.id
                return redirect('reset_password')
        except PasswordResetCode.DoesNotExist:
            messages.error(request, 'Counter check your code seems its incorrect')
            return redirect('verify_reset_code')
    form = PasswordResetCodeForm()
    return render(request, 'home/verify_reset_code.html', {'form': form} )

def reset_password(request):
    user_id = request.session.get('password_reset_user_id')
    if not user_id:
        messages.error(request, 'There was an error proccessing your application, try again')
        return redirect('request_reset_code')
    
    user = User.objects.get(id=user_id)
    try:
        reset_code = PasswordResetCode.objects.filter(user=user).order_by('-created_at').first()
        if reset_code is None:
            messages.error(request, 'There was an error proccessing your application, try again')
            return redirect('request_reset_code')
        if reset_code.is_expired():
            # If the code is expired or invalid, redirect to request a new one
            reset_code.is_valid = False
            reset_code.save()
            messages.error(request, 'Your reset code has expired. Please request a new code.')
            return redirect('request_reset_code')
    except (User.DoesNotExist, PasswordResetCode.DoesNotExist):
        # If the user or reset code is not found, redirect to the request page
        messages.error(request, 'Invalid reset request. Please try again.')
        return redirect('request_reset_code')
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            # Keep the user logged in after password change
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been successfully reset.')
            return redirect('login_user')
    else:
        form = SetPasswordForm(user)
    return render(request, 'home/reset_password.html', {'form': form})

# Create your views here.
def register_user(request):
    next_url = request.GET.get('next', '')
    pricing_plan = request.GET.get('pricing_plan') or ''
    add_staff_to = request.GET.get('add_staff_to') or ''
    refferal_code = request.GET.get('refferal_code') or ''
    add_customer_to = request.GET.get('add_customer_to') or ''
    stored_refferal_code= request.session.get('stored_refferal_code') or '' #  we get both refferal code plus business slug         
    context = {
        'add_staff_to': add_staff_to,
        'add_customer_to': add_customer_to,
        'pricing_plan': pricing_plan,
        'add_customer_to': add_customer_to,
        'next_url': next_url,
    }
    if refferal_code !='':
        request.session['stored_refferal_code'] = refferal_code

    if stored_refferal_code !='':
        refferal_code = stored_refferal_code

    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')  # will install phonenumber and check if number is valid and convert it to international format
        password = request.POST.get('password')

        username =str(254)+str(phone_number)
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            messages.success(request, 'Phone Number already exists.')
            messages.success(request, 'Please login and if forgot password click forgot password')
            return render(request, 'accounts/register.html', context)
        
        # Create user
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password)
        customer = Customer.objects.filter(phone_number=username).first()
        if  customer is None:
            customer = Customer.objects.create(
                phone_number=username,# username is the phone number
                total_loyalty_points = int(200), # 200 point welcome points
                refferal_code = generate_unique_refferal_code()
                )
            points_category = LoyaltyPointsCategory.objects.filter(category='signup points').first()
            if not points_category:
                points_category = LoyaltyPointsCategory.objects.create(
                    category = 'signup points'
                    )

            LoyaltyPoint.objects.create(
                customer = customer,
                category = points_category or None,
                points_earned = int(200),#have assummed every business will give 200 signupp bonus will correct to add what each business want to offer
                points_were = 'earned',
                added_by = 'automaticaly during signup',
                status = 'approved'
                )
            messages.success(request, 'Congrats You have Received 200 points ***Welcome Bonus *** ')

            if refferal_code != '':
                refferer = Customer.objects.filter(refferal_code=refferal_code).first()
                if refferer:
                    customer.reffered_by = refferer.user
                    customer.save()
        
        customer.user = user
        customer.save()
        
        if pricing_plan != '':
            user = authenticate(username=username, password=password)
            login(request, user)
            url = f'/business/add-business/?pricing_plan={pricing_plan}'
            return redirect(url)

        # Add staff logic
        if add_staff_to !='':
            business = Business.objects.filter(slug=add_staff_to).first()
            if business:
                if not Staff.objects.filter(user=user, business=business).exists():
                    Staff.objects.create(user=user, business=business)
                    messages.success(request, 'Staff added successfully')
                    messages.success(request, 'Share email and password for them to log in')

                # Add customer if it does not exist in business customers 
                if customer not in business.customers.all():
                    business.customers.add(customer)
            
            return redirect('dashboard', add_staff_to)
        
        if add_customer_to !='':
            business = Business.objects.filter(slug=add_customer_to).first()
            if business:
                if customer not in business.customers.all():
                    business.customers.add(customer)
        # Handle redirect for "next_url" parameter
        if next_url != '':
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect(next_url)

        # Default redirect after registration
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect('profile')
    
    
    
    return render(request, 'home/register.html', context)

def login_user(request):
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

    return render(request, 'home/login.html', {'next': next_url})

def logout_user(request):
    logout(request)
    messages.success(request, "You Have Been Logged Out...")
    return redirect('login_user')