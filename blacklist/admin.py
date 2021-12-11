from django.contrib import admin

# Register your models here.
from .models import Netblock, IPhistory

admin.site.register(Netblock)
admin.site.register(IPhistory)