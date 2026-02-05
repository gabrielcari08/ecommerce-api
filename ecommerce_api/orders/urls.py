from django.urls import path
from . import views

urlpatterns = [
    path('create_order/', views.create_order_from_cart, name='create_order_from_cart'),
]