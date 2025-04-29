from django.contrib import admin

from .models import Product, ProductCategory, ProductName
# Register your models here.

admin.site.register(Product)
admin.site.register(ProductName)
admin.site.register(ProductCategory)