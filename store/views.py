from django.shortcuts import render, redirect
from django.contrib import messages
from businesses.models import Business, Staff
from .models import Product, ProductCategory, ProductName
from businesses.decorators import team_member_required
from django.contrib.auth.decorators import login_required
# Create your views here.

# all products store

def e_store(request):
    products = Product.objects.all()
    
    context={
        'products':products
    }
    return render(request, 'store/e-store.html', context)

# view for pulic estore of business

def business_store(request, slug):
    business = Business.objects.filter(slug=slug).first()
    products = Product.objects.filter(business=business).all()
    staff = Staff.objects.filter(business=business, user=request.user)
    
    context={
        'business': business,
        'products':products, 
        'staff' : staff
    }
    return render(request, 'store/business-store.html', context)

# model for busineses dashbord
@login_required(login_url="/accounts/login-user/")
@team_member_required
def products(request, slug):
    businesses = Business.objects.filter(owner=request.user)
    business = Business.objects.filter(slug=slug).first()
    products = Product.objects.filter(business=business).all()
    staff = Staff.objects.filter(business=business, user=request.user)
    
    context={
        'businesses': businesses,
        'business': business,
        'products':products, 
        'staff' : staff
    }
    return render(request, 'store/products.html', context)

@login_required(login_url="/accounts/login-user/")
@team_member_required
def add_product(request, slug):
    businesses = Business.objects.filter(owner=request.user)
    business = Business.objects.filter(slug=slug).first()
    product_categories = ProductCategory.objects.all()
    product_names = ProductName.objects.all()
    staff = Staff.objects.filter(business=business, user=request.user)
    if request.method == 'POST':
        category = request.POST.get('category')
        product_name = request.POST.get('product_name')
        price = request.POST.get('price')

        earn_points = int(0.10 * int(price))
        product_category, created= ProductCategory.objects.get_or_create(
            category_name=category
        )# i dont know what happens if category is duplicate will search and update code accordingly

        name, created = ProductName.objects.get_or_create(
            name=product_name
        )#
        Product.objects.create(
            business=business,
            category=product_category,
            name=name,
            price=price,
            earn_points=earn_points,
            created_by=None #update this to take staff and only staff to access this page
        )
        messages.success(request, "product added successfully")
        return redirect('products', slug)
    
        
    context = {
        'businesses': businesses,
        'business': business,
        'product_categories':product_categories, 
        'product_names': product_names,
        'staff' : staff
    }
    return render(request, 'store/add-product.html', context)