from django.contrib import admin
from products.models import Product, Category

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name'] #Without 'list_display' in the panel we will see 'Category object (1)'
    search_fields = ['name'] #With 'search_fields' open the browser. We will can search categories by name

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_active', 'created_at'] 
    list_filter = ['is_active', 'created_at'] #Add filters in the sidebar.
    search_fields = ['name', 'description']