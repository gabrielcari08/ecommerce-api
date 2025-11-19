from django.db import models
from users.models import User
from products.models import Product
from django.db.models import Sum

# Create your models here.

#This model represents the cart of a user
class Cart(models.Model):
    #Cart status options.
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('abandoned', 'Abandoned'),
        ('converted', 'Converted'), #When it is converted to an order
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE) #The user who owns the cart
    #CASCADE:If the user is deleted, the cart is also deleted.
    #OneToOneField:Each user has only one cart.
    created_at = models.DateTimeField(auto_now_add=True) #The date and time when the cart was created
    updated_at = models.DateTimeField(auto_now=True) #The date and time when the cart was last updated
    #The current status of the cart
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    
    #Calculate the total number of items in the cart
    @property
    def total_items(self):
        return self.cartitem_set.aggregate(
            total=Sum('quantity')
        )['total'] or 0

    #Calculate the total price of the cart
    @property
    def total_price(self):
        total = 0
        for item in self.cartitem_set.all():
            total += item.quantity * item.price
        return total

#This model represents each product in the cart
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE) #The cart that contains the item
    #CASCADE:If the cart is deleted, the item is also deleted.
    product = models.ForeignKey(Product, on_delete=models.CASCADE) #The product that is in the cart
    #CASCADE:If the product is deleted, it is removed from the cart.
    quantity = models.IntegerField(default=1) #The quantity of the product in the cart
    price = models.DecimalField(max_digits=10, decimal_places=2) #The price of the product at the time it was added to the cart
    
    class Meta:
        unique_together = ('cart', 'product')
        #If the same product is added twice, the quantity will be updated.