from django.db import models 

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255) #The name of the category

    class Meta:
        db_table = 'categories' #The name of the table in the database
        verbose_name = 'Categories' #The name of the category in the admin panel. 

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True) #True: if the product is avaible, False: if the product is not avaible
    created_at = models.DateTimeField(auto_now_add=True) 
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    #on_delete=models.SET_NULL: when the category is deleted, the field become NULL.

    class Meta:
        db_table = 'products' #The name of the table in the database

