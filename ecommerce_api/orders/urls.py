from django.urls import path
from . import views

urlpatterns = [
    path('create_order/', views.create_order_from_cart, name='create_order_from_cart'),
    path('get_orders/', views.get_orders, name='get_orders'),
    path('get_order_detail/<int:order_id>/', views.get_order_detail, name='get_order_detail'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('summary/', views.order_summary, name='order_summary'),
    path('update_order_status/<int:order_id>/', views.update_order_status, name='update_order_status'),
]