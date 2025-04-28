from django.db import models

from businesses.models import Staff, Business

# Create your models here.
class ProductCategory(models.Model):
    category_name = models.CharField(max_length=250)
    def __str__(self):
        return self.category_name

class Product(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='product')
    product_name = models.CharField(max_length=250)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='product_category')
    price = models.IntegerField(default=1000, help_text='price you charge for the product')
    earn_points = models.IntegerField(default=0, help_text='point cutomer earns after purchasing this product')
    created_by = models.ForeignKey(Staff, blank=True, null=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return self.product_name