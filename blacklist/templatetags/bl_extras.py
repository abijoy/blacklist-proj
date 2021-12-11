from django import template

register = template.Library()


# count total IP addresses of a netblock

@register.filter(is_safe=True)
def total_ip(cidr):
    return 2 ** cidr
