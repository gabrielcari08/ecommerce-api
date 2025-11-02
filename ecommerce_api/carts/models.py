from django.db import models
from users.models import User
from products.models import Product

# Create your models here.

#This model represents the cart of a user
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) #The user who owns the cart
    #CASCADE:If the user is deleted, the cart is also deleted.
    created_at = models.DateTimeField(auto_now_add=True) #The date and time when the cart was created
    updated_at = models.DateTimeField(auto_now=True) #The date and time when the cart was last updated

#This model represents each product in the cart
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE) #The cart that contains the item
    #CASCADE:If the cart is deleted, the item is also deleted.
    product = models.ForeignKey(Product, on_delete=models.CASCADE) #The product that is in the cart
    #CASCADE:If the product is deleted, it is removed from the cart.
    quantity = models.IntegerField(default=1) #The quantity of the product in the cart

    class Meta:
        unique_together = ('cart', 'product')
        #If the same product is added twice, the quantity will be updated.