from django.contrib import admin
from users.models import User

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email'] #Without "list_display" in the panel admin will see "User Object (1)"
