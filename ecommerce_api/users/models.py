from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Create your models here.

#This model inherits from AbstractUser
class User(AbstractUser):
    #Define two types of users: customer or admin
    USER_TYPE_CHOICES = [
        ('customer', 'Customer'),
        ('admin', 'Admin'),
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer') #The type of user: customer or admin

    #Required fields to fix error: SystemCheckError

    groups = models.ManyToManyField(Group, related_name='custom_user_groups', blank=True)

    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_perms', blank=True,)

    class Meta:
        db_table = 'users' #The name of the table in the database

