from django.db import models 

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True) #The name of the category

    def __str__(self):
        return self.name
    
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
    
    def __str__(self):
        return self.name

    class Meta:
        db_table = 'products' #The name of the table in the database
        
class Stock(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='stock')
    #The quantity of the product in stock
    quantity = models.PositiveIntegerField(default=0) 
    #The quantity of the product reserved for orders that are not yet completed. 
    # This field is used to prevent overselling when multiple customers are trying to purchase 
    # the same product at the same time.
    reserved = models.PositiveIntegerField(default=0) 
    
    @property
    def available_stock(self):
        #How many units of the product are available for purchase.
        return self.quantity - self.reserved
    
    def can_satisfy(self, quantity):
        #Check if the stock can satisfy the requested quantity.
        return self.available_stock >= quantity
    
    def reserve(self, quantity):
        #Reserve the specified quantity of the product.
        if self.can_satisfy(quantity):
            self.reserved += quantity
            self.save()
            return True
        return False
    
    def realese(self, quantity):
        #Release the stock reserved
        self.reserved = max(self.reserved - quantity, 0)
        
        self.save()
        
    def deduct(self, quantity):
        #Discount stock (when the order is completed)
        
        #Verify that have enough products.
        if quantity > self.quantity:
            raise ValueError("No hay suficiente stock para completar la orden")
        
        #Take out products from stock
        self.quantity -= quantity
        
        #Realese the reserved stock
        self.realese = max(self.reserved - quantity, 0)
        
        #Save
        self.save()
        
    def add(self, quantity):
        #Add stock (when the order is cancelled or returned)
        self.quantity += quantity
        self.save()
        
class StockMovement(models.Model):
    
    MOVEMENT_TYPES = [
        ('in', 'Stock in'), #When new stock is added to the inventary
        ('out', 'Stock out'), #When the stock is removed from the inventary
        ('reserved', 'Stock reserved'), #When the stock is reserved for an order that is not yet completed
        ('released', 'Stock released'), #When the stock reserved is released (for example, when an order is cancelled)
        ('returned', 'Stock returned'), #When the stock is returned (for example, when an order is returned)
        ('adjustment', 'Stock adjustment'), #When the stock is adjusted manually (for example, to correct an inventory error)
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    #The quantity of the stock movement (positive for stock in, negative for stock out)
    quantity = models.IntegerField() 
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    
    order = models.ForeignKey('orders.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_movements')
    order_item = models.ForeignKey('orders.OrderItem', on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_movements')
    
    created_by = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_movements')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_movements' #The name of the table in the database
        ordering = ['-created_at'] #Order by created_at descending