from django.db import models
from django.conf import settings
from rest_framework.authtoken.models import Token as AuthToken

#This model inherits from AuthToken
class Token(AuthToken):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='auth_tokens',
        on_delete=models.CASCADE,
        verbose_name="User"
    )
    
    class Meta:
        db_table = 'authtoken_token'  # The name of the table in the database