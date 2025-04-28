from django.contrib import admin

from .models import LoyaltyPoint, LoyaltyPointsCategory
# Register your models here.
admin.site.register(LoyaltyPoint)
admin.site.register(LoyaltyPointsCategory)