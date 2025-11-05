from django.urls import path, re_path
from . import views

urlpatterns=[
    path('login', views.login),
    path('register/', views.register),
    path('profile/', views.profile)
]