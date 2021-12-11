from django.db import models
# importing validationerror
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db.models import constraints
from django.db.models.enums import Choices
from django.db.models.fields import BooleanField
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.utils.html import format_html

# Create your models here.
from datetime import date, datetime, timedelta


# field validators

def check_valid_ip(ip):
    oct_list = ip.split('.')
    if len(oct_list) == 4:
        try:
            _ = list(map(int, oct_list))
            return ip
        except:
            raise ValidationError('Please Enter a valid netblock')
    else:
        raise ValidationError(format_html('Please Enter a <b>valid</b> netblock'))

# get valid netblock
def get_valid_netblock(ip, cidr):

    netmask_arr = {
            '8': [255, 0, 0, 0],
            '16': [255, 255, 0, 0],
            '22': [255, 255, 252, 0],
            '23': [255, 255, 254, 0],
            '24': [255, 255, 255, 0],
            '25': [255, 255, 255, 128],
            '26': [255, 255, 255, 192],
            '27': [255, 255, 255, 224],
            '28': [255, 255, 255, 240],
            '29': [255, 255, 255, 248],
            '30': [255, 255, 255, 252],
            '31': [255, 255, 255, 254],
            '32': [255, 255, 255, 255],
    }

    net_addr = list(map(int, ip.split('.')))
    netmask = netmask_arr[cidr]
    tmp = [netmask[0] & net_addr[0], netmask[1] & net_addr[1], netmask[2] & net_addr[2], netmask[3] & net_addr[3]]
    return '.'.join((map(str, tmp)))



def another_validator(ip, cidr):
    import ipaddress
    netblock = f'{ip}/{cidr}'
    result_str = ''
    try:
        ipaddress.ip_network(netblock)
        return (True, '')
    except ValueError as ve:
        if 'host bits' in str(ve):
            print('########')
            valid_nblock = get_valid_netblock(ip, str(cidr))
            result_str = f'{ve} <br>Maybe add <b><i>{valid_nblock}</i></b> instead ?'
        else:
            print('******')
            result_str = str(ve)
        return (False, result_str)

        



class Netblock(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    class CIDR(models.IntegerChoices):
        SN_32 = 32, '/32'
        SN_31 = 31, '/31'
        SN_30 = 30, '/30'
        SN_29 = 29, '/29'
        SN_28 = 28, '/28'
        SN_27 = 27, '/27'
        SN_26 = 26, '/26'
        SN_25 = 25, '/25'
        SN_24 = 24, '/24'
        SN_23 = 23, '/23'
        SN_22 = 22, '/22'
        SN_21 = 21, '/21'
        SN_20 = 20, '/20'
        SN_19 = 19, '/19'
        SN_18 = 18, '/18'
        SN_16 = 16, '/16'
        SN_8 = 8, '/8'

    ip_addr = models.CharField(
                    max_length=15,
                    verbose_name='IP Address',
                    blank=False,
                    # validators=[check_valid_ip]
                    )
    # cidr = models.CharField(
    #                 max_length=2,
    #                 choices=cidr_choices,
    #                 verbose_name='CIDR',
    #                 default='32',
    #                 )
    cidr = models.PositiveSmallIntegerField(
                    choices=CIDR.choices,
                    default=CIDR.SN_32,
                    help_text='Choose cidr'
                    )


    label = models.CharField(
                    max_length=20,
                    verbose_name='label',
                    blank=True,
                    )
    # splitted or not
    split = models.BooleanField(default = False)

    # created at
    created_at = models.DateTimeField(auto_now_add=True)

    # counter of blocked IP will be update on each scan
    total_listed_ip = models.PositiveIntegerField(default=0)

    # relation with ip statistics table
    # listing = ManyToManyField(IpUpdates, )

    # order by
    class Meta:
        ordering = ['cidr']


    # get total ip addresses
    def get_total_ip(self):
        return 2 ** (32 - int(self.cidr))

    # str representation
    def __str__(self) -> str:
        return f'{self.ip_addr}/{self.cidr}'

    # clean for some validation
    def clean(self):
        res = another_validator(self.ip_addr, self.cidr)
        print(f'---{res}---')
        if not res[0]:
            raise ValidationError(
                format_html(res[1])
            )
    
    # override save method
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)





class IPhistory(models.Model):
    parent = models.ForeignKey(Netblock, on_delete=models.CASCADE)
    ip_addr = models.CharField(
                    max_length=15,
                    verbose_name='IP Address',
                    blank=False
                    )
    listed = models.BooleanField(default=False)
    listed_by = models.CharField(max_length=1000, blank=True)
    check_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-check_datetime']
        indexes = [
            models.Index(fields=['ip_addr', 'check_datetime']),
        ]
    
    def __str__(self):
        return f'{self.ip_addr} | listed ? {self.listed}'



# ip table where all IP's only the updated will stay.
# so this table gonna contain limited rows.

class Iptable(models.Model):
    parent = models.ForeignKey(Netblock, on_delete=models.CASCADE)
    ip_addr = models.CharField(
                max_length=15,
                verbose_name='IP Address',
                blank=False
            )
    
    listed = models.BooleanField(default=False)
    listed_by = models.CharField(max_length=1000, blank=True)
    last_checked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # ordering = ['-check_datetime']
        indexes = [
            models.Index(fields=['ip_addr',]),
        ]
        constraints = [
            models.UniqueConstraint(fields=['parent', 'ip_addr'], name='unique_parent_ip')
        ]
    
    def __str__(self):
        return f'{self.ip_addr} | listed ? {self.listed}'


# table to track IP changes / updates etc.
class IpUpdates(models.Model):
    ip_addr = models.CharField(
                max_length=15,
                verbose_name='IP Address',
                blank=False
            )
    listed = models.BooleanField(default=True)
    parent = models.ForeignKey(Netblock, on_delete=models.CASCADE)
    iphistory = models.OneToOneField(IPhistory, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.iphistory} | UPDATED AT: {self.update_time}'


class TestModel(models.Model):
    name = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
