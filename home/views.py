from django.shortcuts import render, redirect
from django.db.models import Count, Sum, Q, Prefetch, Subquery, OuterRef, IntegerField
from django.db.models.functions import Coalesce
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date
from datetime import date
from businesses.models import Business, Staff
from points.models import LoyaltyPoint,  BorrowPoint, LoyaltyPointsCategory
from customers.models import Customer, ScanCount
from store.models import Product

today = date.today()
# Create your views here.


# Create your views here.
def index(request):
    return redirect('loyalty_qr_code')

def pricing(request):
    return render(request, 'home/pricing.html')



@login_required(login_url="/accounts/login-user/")
def profile(request):
    
    customer = Customer.objects.filter(user=request.user).first()
    if not Customer.objects.filter(user=request.user).exists():
        customer = Customer.objects.create(user=request.user)
    
    approve_id = request.GET.get('approve_id') or ''
    if approve_id !='':
        lent_point = BorrowPoint.objects.filter(id=approve_id, lender=customer).first()
        if lent_point:
            customer_total_points = customer.total_loyalty_points
            point_to_lend = customer_total_points-200
            if point_to_lend < lent_point.points_borrowed:
                messages.success(request, f"You dont have sufficient points to lend")
                messages.success(request, f"Your account must have a minimum of 200 points after lending")
                messages.success(request, f"Continue refilling your gas with us to earn more points")
                return redirect('profile')
            #deduct borrowed point from customers total points
            customer_current_points = customer_total_points - lent_point.points_borrowed
            customer.total_loyalty_points = customer_current_points
            customer.save()
            #create loyalty points for the above trnasactions
            points_category = LoyaltyPointsCategory.objects.filter(category='loaned').first()
            if not points_category:
                points_category = LoyaltyPointsCategory.objects.create(
                    category = 'loaned'
                    )

            LoyaltyPoint.objects.create(
                customer = customer,
                category = points_category or None,
                points_redeemed = lent_point.points_borrowed,#have assummed every business will give 200 signupp bonus will correct to add what each business want to offer
                points_were = 'loaned',
                added_by = f'automaticaly added after approval from {customer}',
                status = 'approved'
                )
            
            # add borrowed points to borrower total points plus update loyalty points
            total_borrower_points = lent_point.borrower.total_loyalty_points + lent_point.points_borrowed
            lent_point.borrower.total_loyalty_points = total_borrower_points
            lent_point.borrower.save()
            #create loyalty points for the above trnasactions
            points_category = LoyaltyPointsCategory.objects.filter(category='borrowed').first()
            if not points_category:
                points_category = LoyaltyPointsCategory.objects.create(
                    category = 'borrowed'
                    )

            LoyaltyPoint.objects.create(
                customer = lent_point.borrower,
                category = points_category or None,
                points_earned = lent_point.points_borrowed,#have assummed every business will give 200 signupp bonus will correct to add what each business want to offer
                points_were = 'borrowed',
                added_by = f'automaticaly added after approval from {customer}',
                status = 'approved'
                )
            
            #lets end by approving the lend points
            lent_point.approved = True
            lent_point.save()
            messages.success(request, f"{lent_point.points_borrowed} points lent succesfully to {lent_point.borrower}")
        return redirect('profile')
    today = date.today()
    #checking if request.user is a staff in any business account
    staff_businesses = Staff.objects.filter(user=request.user)
    #checking if request.user has business account and quering tem
    businesses = Business.objects.filter(owner=request.user)

    all_points = LoyaltyPoint.objects.all()
    points= all_points.filter(customer=customer)
    total_points = points.exclude(status='declined').aggregate(total_earned=Sum('points_earned'), total_redeemed=Sum('points_redeemed')) 
    total_points = (total_points['total_earned'] or 0) - (total_points['total_redeemed'] or 0)
    
    total_approved_points = points.filter(status='approved').aggregate(total_earned=Sum('points_earned'), total_redeemed=Sum('points_redeemed'))
    total_approved_points = (total_approved_points['total_earned'] or 0) - (total_approved_points['total_redeemed'] or 0)

    total_points_awaiting_approval = points.filter(status='awaiting approval').aggregate(Sum('points_earned'))['points_earned__sum'] or 0
    
    refferals_points = all_points.filter(category__category='points on purchases made', status='approved')

    # Subquery to count loyalty points per customer
    loyalty_points_count_subquery = refferals_points.filter(
        customer=OuterRef('pk')  # match Customer.pk
    ).values('customer').annotate(
        count=Count('id')  # count loyalty points
    ).values('count')[:1]

    # Final query for referred customers
    refferd_customers = Customer.objects.filter(
            reffered_by=request.user
        ).annotate(
            loyalty_point_count=Coalesce(
                Subquery(loyalty_points_count_subquery, output_field=IntegerField()),
                0
            )
        )
    loaned_points = BorrowPoint.objects.filter(lender=customer).order_by('-id') # querying points to be lended out
    borrowed_points = BorrowPoint.objects.filter(borrower=customer).order_by('-id') # querying points points needed to be repayed

    context = {
        'businesses': businesses,
        'customer': customer,
        'staff_businesses': staff_businesses,
        'points': points,
        'total_points': total_points,
        'total_approved_points': total_approved_points,
        'total_points_awaiting_approval':total_points_awaiting_approval,
        'refferd_customers': refferd_customers,
        'borrowed_points': borrowed_points,
        'loaned_points': loaned_points


    }
    return render(request, 'home/profile.html', context)


# admin section
@login_required(login_url="/accounts/login-user/")
def all_customers(request):
    if not request.user.is_staff:
        messages.success(request, "You dont have permission to access the page")
        return redirect('profile')
    customers = Customer.objects.all().order_by('-date_updated')
    
    context={
        'customers':customers
    }
    return render(request, 'admin/customers.html', context)
