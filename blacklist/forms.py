from django.db import models
from django.forms import ModelForm, fields
from blacklist.models import Netblock

class NetblockForm(ModelForm):
    class Meta:
        model = Netblock
        fields = ['ip_addr', 'cidr', 'label']