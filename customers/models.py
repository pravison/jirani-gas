from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Inquiries(models.Model):
    website_url = models.URLField(blank=True, null=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=25)
    plan = models.CharField(max_length=25)
    

    def __str__(self):
        return self.name

class Customer(models.Model):
    user = models.OneToOneField(User, blank=True, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=250, default='customer')
    phone_number = models.CharField(max_length=25, null=True, blank=True)
    total_loyalty_points = models.IntegerField(default=0)
    refferal_code = models.CharField(max_length=8, unique=True)
    reffered_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, help_text='user who reffered customer', related_name='reffer')
    date_joined = models.DateTimeField(auto_now_add = True)
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}' 
    
class ScanCount(models.Model):
    customer = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.SET_NULL)
    number = models.IntegerField()
    date_scanned = models.DateField(auto_now_add=True)
    def __str__(self):
        return f'{self.business} - {self.number}'
    
