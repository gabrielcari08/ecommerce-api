from django.db import models
from users.models import User
from carts.models import Cart
from products.models import Product
import random
import string
from datetime import datetime

# Create your models here.

#This model represents an order placed by a user
class Order(models.Model):

    #This is a tuple of choices for the status field
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('return_requested', 'Return Requested'), #New status
        ('returned', 'Returned'), #New status
        
        #'return_requested': when the user requests a return for the order.
        #'returned': when the order has been returned and the return process is complete.
    )
    
    #The user who placed the order
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #The unique order number
    order_number = models.CharField(unique=True)
    #The status of the order
    status = models.CharField(max_length=20, default='pending', choices=STATUS_CHOICES)

    #The total amount of the order
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    #The subtotal of the order
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    #The tax of the order
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0) 
    #The shipping of the order
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    #The discount of the order
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    #The shipping address of the order
    shipping_address = models.JSONField(default=dict)
    #The billing address of the order
    billing_address = models.JSONField(default=dict)
    
    #The shipping method of the order
    shipping_method = models.CharField(max_length=20, default='standard')
    #The tracking number of the order
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    
    #The date and time when the order was created
    created_at = models.DateTimeField(auto_now_add=True)
    #The date and time when the order was last updated
    updated_at = models.DateTimeField(auto_now=True)
    
    #New field for return reason
    return_reason = models.TextField(blank=True, null=True) 
    #New field for return request date
    return_requested_at = models.DateTimeField(blank=True, null=True)
    #New field for returned date
    returned_at = models.DateTimeField(blank=True, null=True) 
    #New field for refunded date
    refunded_at = models.DateTimeField(blank=True, null=True) 
    #New field for delivery date
    delivered_at = models.DateTimeField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)

    def generate_order_number(self):
        #Get the current date and time
        timestamp = datetime.now().strftime('%Y%m%d')
        #Generate a random string of 6 characters
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        #Combine the timestamp and random string to create a unique order number
        return f"ORD-{timestamp}-{random_str}"

#This model represents an item in an order
class OrderItem(models.Model):
    #The order that contains the item
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    #The product that is in the order
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    #The name of the product
    product_name = models.CharField(max_length=255)
    #The quantity of the product in the order
    quantity = models.PositiveIntegerField()
    #The unit price of the product in the order
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    #The total price of the product in the order
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def save(self, *args, **kwargs):
        if not self.total_price and self.unit_price and self.quantity:
            self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
