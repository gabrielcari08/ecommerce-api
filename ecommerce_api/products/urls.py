from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.list_categories, name='list_categories'),
    path('list_products/', views.list_products, name='list_products'),
    path('detail_product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('create_product', views.create_product, name='create_product'),
    path('update_product/<int:product_id>', views.update_product, name='update_product'),
    path('delete_product/<int:product_id>', views.delete_product, name='delete_product'),
]