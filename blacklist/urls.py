from django.urls import path
from django.urls.conf import include
from . import views

app_name = 'blacklist'

urlpatterns = [
    path('', views.index, name='index'),
    path('myip', views.my_ip_addresses, name='my_ip_addresses'),
    path('myip/add', views.add_netblock, name='add_netblock'),
    path('myip/split/<str:parent_ip>/<str:cidr>/', views.split_parent, name='split_parent'),
    path('myip/history/<str:ip_addr>/<str:cidr>/', views.blacklist_check, name='blacklist_check'),
    path('myip/entires/all/<str:status>/<int:parent_id>/', views.entries_total, name='entries_total'),
    path('myip/hist/ip/<str:ip_addr>/', views.hist_single_ip, name='hist_single_ip'),
    path('myip/entries/last_7_days/<str:status>/<str:parent_id>/', views.list_delist_entries_last_x_days, name='entries_list_delist_x_days'),
    # path('myip/entries/last_7_days/<str:delisted>/<str:parent_id>/', views.delisted_entries_last_x_days, name='entries_delisted_x_days'),


]