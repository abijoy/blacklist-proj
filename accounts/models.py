from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    
    USER_TYPES = (
        ('lir', 'Local Internet Registry'),
        ('personal', 'Personal')
    )

    fullname = models.CharField(max_length=30, verbose_name='Full Name')
    user_type = models.CharField(max_length=9, choices=USER_TYPES, default='personal')
    email = models.EmailField(_('email address'), unique=True)
