from django.urls import path
from . import views

urlpatterns = [
    path('get_cart/', views.get_cart, name='get_cart'),
    path('add', views.add_to_cart, name='add_to_cart'),
    path('summary/', views.cart_summary, name='cart_summary'),
    path('update_item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove_item/<int:item_id>/', views.remove_from_cart, name='remove_cart_item'),
    path('clear/', views.clear_cart, name='clear_cart'),
]