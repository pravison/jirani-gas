from django.db import models
from django.contrib.auth.models import User
from customers.models import Customer
from businesses.models import Staff, Business
# Create your models here.



class LoyaltyPointsCategory(models.Model):
    category = models.CharField(max_length=100, choices=(('points on purchases made', 'points on purchases made'), ('signup points', 'signup points'), ('points for joining a challenge', 'points for joining a challenge'),('points spent for votes purchase', 'points spent for votes purchase'), ('points on visiting the store', 'points on visiting the store'), ('points from refferal sales', 'points from refferal sales'), ('points on bringing friends to the store', 'points on bringing friends to the store'), ('redeemed', 'redeemed'), ('loaned', 'loaned'), ('borrowed', 'borrowed'), ('repayment of  borrowed points', 'repayment of borrowed points')))
    total_value_for_a_point= models.FloatField(default=10, help_text="what value equals 1 point ex. ksh10 for 1 point")
    updated_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)
    def __str__(self):
        return self.category


# this model keeps track of all model flow from points earned, redemeed, loaned, repayed
class LoyaltyPoint(models.Model):
    customer = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.SET_NULL)
    business = models.ForeignKey(Business, blank=True, null=True, on_delete=models.SET_NULL) # this keeps track of which business customer purchased from
    category = models.ForeignKey(LoyaltyPointsCategory, blank=True, null=True, on_delete=models.SET_NULL)
    purchase_value = models.IntegerField(default=0)
    points_earned = models.IntegerField(default=0)# points in
    points_redeemed = models.IntegerField(default=0) # points out
    added_by = models.CharField(max_length=200)
    payement_refference_code = models.CharField(max_length=200, blank=True, null=True, )
    points_were = models.CharField(max_length=100, default='earned', help_text=" purpose for the points", choices=(('earned', 'earned'), ('redeemed', 'redeemed'), ('loaned', 'loaned'), ('borrowed', 'borrowed'), ('repayment of  borrowed points', 'repayment of  borrowed points')))
    status = models.CharField(max_length=100, default="awaiting approval", choices=(('awaiting approval', 'awaiting approval'), ('approved', 'approved'), ('declined', 'declined')))
    date_added = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.customer.user.first_name} {self.customer.user.first_name} points earned: {self.points_earned}'

# here is how the code will work if customer borrows points we will update 
# the loyalty points as borred then update the BorrowPoint model to keep track of the borrowed points and repayment

class BorrowPoint(models.Model):
    lender = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.SET_NULL, related_name='lender')
    borrower = models.ForeignKey(Customer, blank=True, null=True, on_delete=models.SET_NULL, related_name='borrower')
    points_borrowed = models.IntegerField(default=0)
    points_currently_repaid = models.IntegerField(default=0)
    fully_paid = models.BooleanField(default=False)
    approved = models.BooleanField(default=False, help_text='lender must approve to give loan to borrower')
    def __str__(self):
        return f'{self.borrower.user.first_name} {self.borrower.user.first_name} points borrowed: {self.points_borrowed}'

# here is how the code will work if customer repays borrowed points we will update 
# the loyalty points as borrowed_points_repayment then update the PayBorrowPoint model to keep track of the payment borrowed points
#  and  update the BorrowPoint model 

class PayBorrowedPoint(models.Model):
    borrowed_point = models.ForeignKey(BorrowPoint, on_delete=models.CASCADE)
    points_payed = models.IntegerField(default=0)
    def __str__(self):
        return f'{self.borrowed_point.borrower.user.first_name} {self.borrowed_point.borrower.user.last_name} points payed: {self.points_payed}'

    
    