from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import InquiriesForm
from .models import Customer
from accounts.views import generate_unique_refferal_code
from points.models import LoyaltyPointsCategory, LoyaltyPoint
from businesses.models import Business

# Create your views here.
def inquire(request):
    plan = request.GET.get('plan')
    if request.method == 'POST':
        form = InquiriesForm(request.POST)
        if form.is_valid():
            instance= form.save(commit=False)
            instance.plan=plan
            instance.save()
            messages.success(request, "Your request has been received you will receive your web analysis report within 24 hours ")
        return redirect('index')
    else:
        form = InquiriesForm()
        context = {
            'form': form,
            'plan': plan
        }
        return render(request, 'home/inquire.html', context)

def add_customer(request):
    refferal_code = request.GET.get('refferal_code') or ''
    reffered_customer_number = request.GET.get('reffered_customer_number') or ''
    bussiness_slug = request.GET.get('bussiness_slug') or ''

    if request.method == 'POST':
        name = request.POST['name'] # will install phonenumber and check if number is valid and convert it to international format
        phone_number = request.POST['phone_number'] 
        refferal_code = request.POST['refferal_code'] or ''
        
        #lets get customer with the above reffral code 
        user_who_reffered = None
        if refferal_code !='':
            customer_with_the_code = Customer.objects.filter(refferal_code=refferal_code).first()
            if customer_with_the_code:
                # lets check if customer object has user field 
                if customer_with_the_code.user:
                    user_who_reffered = customer_with_the_code.user

        # lets save neigbor record to the database
        # first check if customer with the number already exists
        # lets create loyalty points record for the welcome bonus to the customer
        url = f'/customers/invite-a-neighbor/?refferal_code={refferal_code}&bussiness_slug={bussiness_slug}'
        phone_number = str(254)+str(phone_number)
        customer = Customer.objects.filter(phone_number=phone_number).first()
        if  customer:
            if bussiness_slug !='':
                messages.success(request, 'Unfoortunately customer with that phone number already exists')
            else:
                messages.success(request, 'Unfoortunately Neighbor already been added by someone else')
            return redirect(url)
        else:
            customer = Customer.objects.create(
                name = name,
                phone_number=phone_number,
                total_loyalty_points = int(200), # 200 point welcome points
                refferal_code = generate_unique_refferal_code(),
                reffered_by = user_who_reffered
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
            # lets add customer to a business that added him
            notify1="Congrats Your Neighbor has Received 200 points ***Welcome Bonus *** "
            notify2="Neighbor added succesfuly to your lists of refferals"
            if bussiness_slug !='':
                business = Business.objects.filter(slug=bussiness_slug).first()
                if business:
                    if customer not in business.customers.all():
                        business.customers.add(customer)
                        notify1="Congrats Your Customer has Received 200 points ***Welcome Bonus *** "
                        notify2="Customer added succesfuly to your lists of customers"
            messages.success(request, notify1)
            messages.success(request, notify2)
            url = f'/customers/invite-a-neighbor/?refferal_code={refferal_code}&reffered_customer_number={phone_number}&bussiness_slug={bussiness_slug}'
            
            
            
            
            return redirect(url)
        
       
    context = {
        'refferal_code': refferal_code,
        'reffered_customer_number': reffered_customer_number,
        'bussiness_slug': bussiness_slug
    }
    return render(request, 'customers/add-customer.html', context)