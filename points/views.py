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
from businesses.models import Business, Staff
from .models import LoyaltyPointsCategory, LoyaltyPoint, BorrowPoint, PayBorrowedPoint
from customers.models import Customer, ScanCount
from store.models import Product
from businesses.decorators import team_member_required

import random
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

from django.core.mail import send_mail

import qrcode
from PIL import Image, ImageDraw, ImageFont


from io import BytesIO
import base64
today = date.today()
# Create your views here.

# will get rid of this functions points can only be added by staff or automatically programmed

@login_required(login_url="/accounts/login-user/")
def customer_adding_loyalty_points(request, slug):
    businesses = Business.objects.filter(owner=request.user)
    business = Business.objects.filter(slug=slug).first()
    staff = Staff.objects.filter(business=business, user=request.user).first()
    loyalty_categories = LoyaltyPointsCategory.objects.filter(business=business)
    if request.method == 'POST':
        category_name = request.POST.get('category')
        purchase_value = request.POST.get('purchase_value')
        customer_email = request.POST.get('customer_email')

        loyalty_category = LoyaltyPointsCategory.objects.filter(business=business, category=category_name).first()
        earned_points = int(int(purchase_value)/int(loyalty_category.total_value_for_a_point))

        user = User.objects.filter(email=customer_email).first()
        if user :
            customer = Customer.objects.filter(user=user).first()
            if customer is not None:
                business_customer = BusinessCustomer.objects.filter(business=business, customer=customer).first()
                if business_customer is None:
                    business_customer = BusinessCustomer.objects.create(business=business, customer = customer)
                if business.customers.filter(user=user).exists():
                    LoyaltyPoint.objects.create(
                        business=business,
                        customer = customer,
                        category=loyalty_category,
                        purchase_value=purchase_value,
                        points_earned=earned_points,
                        added_by = f'{request.user.first_name} {request.user.last_name}' 
                    )
                    business_customer.total_loyal_points += earned_points
                    business_customer.save()
                    messages.success(request, "points added succesfully")
                else:
                    business.customers.add(customer)
                    LoyaltyPoint.objects.create(
                        business=business,
                        customer = customer,
                        category=loyalty_category,
                        purchase_value=purchase_value,
                        points_earned=earned_points,
                        added_by = f'{request.user.first_name} {request.user.last_name}' 
                    )
                    business_customer.total_loyal_points += earned_points
                    business_customer.save()
                    messages.success(request, "points added succesfully")
            else:
                customer = Customer.objects.create(user=user)
                business.customers.add(customer)
                business_customer = BusinessCustomer.objects.create(business=business, customer=customer)
                LoyaltyPoint.objects.create(
                    business=business,
                    customer = customer,
                    category=loyalty_category,
                    purchase_value=purchase_value,
                    points_earned=earned_points,
                    added_by = f'automatically added' 
                )
                business_customer.total_loyal_points += earned_points
                business_customer.save()
                messages.success(request, "points added succesfully")
        else:
            messages.success(request, "Customer does not exist send them a link to register first")
        
        return redirect('loyalty_points', slug)

    context = {
        'businesses': businesses,
        'business': business,
        'staff': staff,
        'loyalty_categories':loyalty_categories
    }
    return render(request, 'business/customer-adding-loyalty-points.html', context)

@login_required(login_url="/accounts/login-user/")
@team_member_required
def loyalty_points(request, slug):
    approve_point_id = request.GET.get('approve_point_id') or ''
    businesses = Business.objects.filter(owner=request.user)
    business = Business.objects.filter(slug=slug).first()


    # a quering the first product
    # will update code to query products dynamically
    products = Product.objects.filter(business=business).first()
    staff = Staff.objects.filter(business=business, user=request.user)
    loyalty_points = LoyaltyPoint.objects.filter(business=business)

    if approve_point_id !='':
        loyalty_point = loyalty_points.filter(id=approve_point_id).first()
        loyalty_point.status = 'approved'
        loyalty_point.save()
    

    qr_url = f"{request.scheme}://{request.get_host()}/points/loyalty-membership/"  # URL to lock the code

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
    context={
        'businesses': businesses,
        'business': business,
        'staff': staff,
        'loyalty_points': loyalty_points,
        'qr_code_image': qr_code_image,
        'products': products
    }
    return render(request, 'business/loyalty-points.html', context)

def loyalty_qr_code(request):
    code_reffered = request.GET.get('referral_code') or '' #code that reffered request.user
    stored_refferal_code= request.session.get('stored_refferal_code') or ''
    if code_reffered !='' and stored_refferal_code=='':
        request.session['stored_refferal_code'] = code_reffered
    
    # a quering the first product
    # will update code to query products dynamically
    # products = Product.objects.filter(business=business).first()
    qr_url = f"{request.scheme}://{request.get_host()}/points/loyalty-membership/?referral_code={code_reffered}"  # URL to lock the code

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
    context={
        'qr_code_image': qr_code_image,
        'code_reffered': code_reffered
    }
    return render(request, 'business/loyalty-qr-code.html', context)


def get_next_number():
    """
    atomically generate next number in sequence, skipping multiples of 20 """
    with transaction.atomic():
        # business = Business.objects.filter(id=id).first()
        sequence = ScanCount.objects.filter(date_scanned=today).last()
        if sequence is None:
            sequence= ScanCount.objects.create(
            number=9
            )
        next_number=sequence.number +1 
        if next_number % 20 == 0:
            next_number += 1
        return next_number
    
def loyalty_membership(request): 
    code_reffered = request.GET.get('referral_code') or '' #code that reffered request.user
    stored_refferal_code= request.session.get('stored_refferal_code') or ''
    if code_reffered !='' and stored_refferal_code=='':
        request.session['stored_refferal_code'] = code_reffered

    customer_scan_count= request.session.get('customer_scan_count')
    
    # a quering the first product
    # will update code to query products dynamically
    # products = Product.objects.filter(business=business).first()

    total_points = 0,
    remaining_points = 0,
    percentage_points = 0,
    refferal_code = ''#request.user refferal code
    customer = None
    if request.user.is_authenticated:
        customer = Customer.objects.filter(user=request.user).first()
    if customer:
        refferal_code = customer.refferal_code
        total_points = customer.total_loyalty_points
        remaining_points = 1000 - total_points
        percentage_points = (total_points/1000)*100
        if total_points > 1000:
            remaining_points = total_points - 1000
    
    
    if not customer_scan_count:
        scan_count = ScanCount.objects.create(
            customer = customer or None,
            number = get_next_number()
        )
        request.session['customer_scan_count'] = scan_count.number
        customer_scan_count = scan_count.number
   
    
    context={
        # 'business': business,
        # 'products': products,
        'customer': customer,
        'customer_scan_count': customer_scan_count,
        'total_points': total_points,
        'remaining_points': remaining_points,
        'percentage_points': percentage_points,
        'code_reffered': code_reffered
    }
    return render(request, 'business/loyalty-membership.html', context)


@login_required(login_url="/accounts/login-user/")
@team_member_required
def redeemed_loyalty_points(request, slug):
    businesses = Business.objects.filter(owner=request.user)
    business = Business.objects.filter(slug=slug).first()
    staff = Staff.objects.filter(business=business, user=request.user)
    business_customer = None
    customer_email = request.GET.get('customer_email') or ''

    if customer_email != '':
        user = User.objects.filter(email=customer_email).first()
        if user is None:
            messages.success(request, "user with that email does not exists")
        else:
            customer = Customer.objects.filter(user=user).first()
            if customer is None:
                messages.success(request, "customer does not exists")
                customer = None
            else:
                business_customer = BusinessCustomer.objects.filter(customer=customer, business=business).first()
                if business_customer is None:
                    messages.success(request, "customer has not yet registered for loyalty points")
                    customer = None

    context={
        'businesses': businesses,
        'business': business,
        'staff': staff,
        'business_customer': business_customer,
    }
    return render(request, 'business/redeeme-points.html', context)


@csrf_exempt  # or better use CSRF token as shown above
def borrow_points_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        customer_id = data.get('customer_id')
        points_requested = data.get('points_requested')

        # Your logic to process the borrowed points here
        borrower = request.user.customer
        print(borrower)
        lender = Customer.objects.filter(id=customer_id).first()
        BorrowPoint.objects.create(
            borrower=borrower,
            lender=lender,
            points_borrowed = points_requested
        )
        
        return JsonResponse({'message': 'Points borrowed successfully.'})

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt  # Only needed if you're not using the CSRF token from frontend
def repay_points_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        lender_id = data.get('lender_id')
        point_to_repay = int(data.get('point_to_repay', 0))
        borrowed_point_id = data.get('borrowed_point_id')

        borrower = request.user.customer
        lender = Customer.objects.filter(id=lender_id).first()
        borrow_point = BorrowPoint.objects.filter(id=borrowed_point_id).first()

        if not lender or not borrow_point:
            return JsonResponse({'error': 'Lender or borrow point not found.'}, status=404)

        total_points_borrowed = borrow_point.points_borrowed
        total_points_repaid = borrow_point.points_currently_repaid or 0

        # Check if repay exceeds borrowed
        if total_points_repaid + point_to_repay > total_points_borrowed:
            return JsonResponse({'error': 'Repay amount exceeds borrowed total.'}, status=400)

        # Update repayment
        total_points_repaid += point_to_repay
        borrow_point.points_currently_repaid = total_points_repaid
        borrow_point.fully_paid = total_points_repaid >= total_points_borrowed
        borrow_point.save()

        # Record repayment
        PayBorrowedPoint.objects.create(
            borrowed_point=borrow_point,
            points_payed=point_to_repay
        )

        # Get or create the category
        points_category, _ = LoyaltyPointsCategory.objects.get_or_create(
            category='repayment of borrowed points'
        )

        # Update lender points
        LoyaltyPoint.objects.create(
            customer=lender,
            category=points_category,
            points_earned=point_to_repay,
            points_were='repayment of borrowed points',
            added_by=f'automatically added after {borrower} repaid borrowed points',
            status='approved'
        )
        lender.total_loyalty_points += point_to_repay
        lender.save()

        # Update borrower points
        LoyaltyPoint.objects.create(
            customer=borrower,
            category=points_category,
            points_redeemed=point_to_repay,
            points_were='repayment of borrowed points',
            added_by=f'automatically added after {borrower} repaid borrowed points',
            status='approved'
        )
        borrower_total_points = borrower.total_loyalty_points #previous total points 
        borrower_total_points = borrower_total_points - point_to_repay # substracting points repayed
        borrower.total_loyalty_points = borrower_total_points # updating current total ponts
        borrower.save()

        return JsonResponse({'message': 'Points repaid successfully.'})

    return JsonResponse({'error': 'Invalid request method'}, status=400)
