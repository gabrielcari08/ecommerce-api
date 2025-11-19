from django.urls import path
from . import views

urlpatterns = [
    path('get_cart/', views.get_cart, name='get_cart'),
    path('add', views.add_to_cart, name='add_to_cart'),
]