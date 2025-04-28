from django.db import models
from django.utils.timezone import now
from datetime import datetime, date , timedelta
from django.contrib.auth.models import User
from customers.models import Customer
import uuid

# Create your models here.
class Business(models.Model):
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    business_name = models.CharField(max_length=250, unique=True)
    slug = models.CharField(max_length=250, unique=True)
    phone_number = models.CharField(max_length=25)
    country = models.CharField(max_length=250, default='Kenya')
    county = models.CharField(max_length=250)
    location = models.CharField(max_length=250)
    ward = models.CharField(max_length=250)
    address = models.TextField(max_length=1000)
    description = models.TextField(blank=True, help_text='describe what you do')
    subscription_plan = models.CharField(max_length=250, blank=True)
    customers = models.ManyToManyField(Customer, blank=True)
    date_joined = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.business_name
    
class  Staff(models.Model):
    user = models.ForeignKey(User, on_delete= models.CASCADE, related_name='staff')
    business = models.ForeignKey(Business, on_delete= models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add = True)
    def __str__(self):
        return f'{self.user.first_name} - {self.business.business_name}'


    

# class BusinessSetting(models.Model):
#     business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='settings')
#     points_redemed_at_how_much_per_point = models.FloatField(default=0.50) # at what price to redeem points
#     def __str__(self):
#         return self.business.business_name
