from django.http.response import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth import get_user_model, login

# to calcuate perfomance
import time
from datetime import datetime, timedelta

# for pagination
from django.core.paginator import Paginator


from django.contrib import messages

from .forms import NetblockForm
from .models import Netblock, IPhistory, Iptable, IpUpdates
from django.db.models import F

import ipaddress
import json
from bg_tasks.temp import dnsbl_checklist



# function to get IPv4adresses from a cidr netblock
def get_single_ip_range(nblock):
    return [ip.compressed for ip in ipaddress.IPv4Network(nblock)]

@login_required
def index(request):
    return render(request, 'blacklist/index.html')


@login_required
def my_ip_addresses(request):
    if request.user.is_authenticated:
        netblocks = Netblock.objects.filter(owner=request.user)
        # num_bl_ip = IPhistory.objects.ge
        # listing_dict = []
        nblock_list_delist_dict = {}
        for n in netblocks:
            total_lists = Iptable.objects.filter(listed=True, parent=n, updated_at__gte=datetime.now()-timedelta(days=7)).count()

            total_delists = Iptable.objects.filter(listed=False, parent=n, updated_at__gte=datetime.now()-timedelta(days=7)).count()
            nblock_list_delist_dict[n] = (total_lists, total_delists)
            # list_delist_dict

        return render(request, 'blacklist/my_ip_addresses.html', {'netblocks': nblock_list_delist_dict})
    # else:
    #     return redirect_to_login(request.path)

@login_required
def add_netblock(request):
    if request.method == 'POST':
        form = NetblockForm(request.POST)
        if form.is_valid():
            print(form)
            nblock = form.save(commit=False)
            print('######', request.user)
            # print(get_user_model())
            nblock.owner = request.user
            print('######', request.user)
            print(nblock.ip_addr)
            ip_cidr = f'{nblock.ip_addr}/{nblock.cidr}'
            try:
                _ = Netblock.objects.get(ip_addr=nblock.ip_addr, cidr=nblock.cidr, owner=request.user)
                messages.add_message(request, messages.INFO,
                    f'{ip_cidr} already added to your list')
                return redirect(reverse('blacklist:add_netblock'))
            except:
                nblock.save()
                # adding bg task to update iphistory of this block
                dnsbl_checklist.delay(nblock.id, get_single_ip_range(ip_cidr))
                print('######', request.user)
                messages.add_message(request, messages.INFO,
                    f'<< {ip_cidr} >> is added!')
                # print('Im done here')
                return redirect('/myip')
    else:
        form = NetblockForm()
    return render(request, 'blacklist/add_netblock.html', {'form': form})


@login_required
def blacklist_check(request, ip_addr, cidr):
    print(f'IP: {ip_addr} / {cidr}')
    _nblock = get_object_or_404(Netblock, owner=request.user, ip_addr=ip_addr, cidr=cidr)
    nblock = f'{_nblock.ip_addr}/{_nblock.cidr}'
    # ip_list = get_single_ip_range(f'{ip_addr}/{cidr}')
    ip_list = get_single_ip_range(nblock)
    # get total ip under a subnet
    total = 2 ** (32 - int(cidr))
    hist_qset = Iptable.objects.filter(parent=_nblock).order_by('-last_checked_at').order_by('id')

    page_number = request.GET.get('page', 1)

    # print(f'{page_number= }')
    per_page = 128
    paginator = Paginator(hist_qset, per_page)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'parent_id': _nblock.id,
        'ip_addr': ip_addr,
        'cidr': cidr
    }
    
    return render(request, 'blacklist/blacklist_check.html', context=context)

@login_required
def split_parent(request, parent_ip, cidr):

    if cidr == '32':
        messages.add_message(request, messages.INFO,
        f'You cannot split a single(/32) IP addr.')
        return redirect(reverse('blacklist:my_ip_addresses'))
    context = {
        'parent_ip': parent_ip,
        'cidr': cidr,
    }
    return render(request, 'blacklist/split_parent.html', context=context)



@login_required
def entries_total(request, parent_id, status):
    _nblock = get_object_or_404(Netblock, id=parent_id, owner=request.user)
    if _nblock:
        total_entries = Iptable.objects.filter(listed=True, parent_id=_nblock.id).order_by('id')
        # total_entries = _nblock.ipupdates_set.filter(listed=True).distinct('ip_addr', 'parent_id')

        print(total_entries.count())
        page_number = request.GET.get('page', 1)

        # print(f'{page_number= }')
        per_page = 128
        paginator = Paginator(total_entries, per_page)
        page_obj = paginator.get_page(page_number)

        context = {
            'status': 'total ' + status,
            'since': '',
            'page_obj': page_obj,
            'parent_id': _nblock.id,
            'ip_addr': _nblock.ip_addr,
            'cidr': _nblock.cidr
        }

        return render(request, 'blacklist/entries_total.html', context=context)
    else:
        return Http404


@login_required
def list_delist_entries_last_x_days(request, status, parent_id):
    _nblock = get_object_or_404(Netblock, id=parent_id, owner=request.user)
    if _nblock:
        total_lists = ''
        if status == 'listed':
            total_lists = Iptable.objects.filter(listed=True, parent=_nblock, updated_at__gte=datetime.now()-timedelta(days=7)).distinct('ip_addr', 'parent_id')
            status = status + ' on '
        if status == 'delisted':
            total_lists = Iptable.objects.filter(listed=False, parent=_nblock, updated_at__gte=datetime.now()-timedelta(days=7)).distinct('ip_addr', 'parent_id')
            status = status + ' from '
        page_number = request.GET.get('page', 1)

        # print(f'{page_number= }')
        per_page = 128
        paginator = Paginator(total_lists, per_page)
        page_obj = paginator.get_page(page_number)

        context = {
            'status': 'got ' + status,
            'since': 'in last 7 days',
            'page_obj': page_obj,
            'parent_id': _nblock.id,
            'ip_addr': _nblock.ip_addr,
            'cidr': _nblock.cidr
        }

        return render(request, 'blacklist/entries_total.html', context=context)
    else:
        return Http404



@login_required
def hist_single_ip(request, ip_addr):
    obj = IPhistory.objects.filter(ip_addr=ip_addr)
    return render(request, 'blacklist/history_single_ip.html', {'obj': obj})
