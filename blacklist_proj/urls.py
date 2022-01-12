from django.contrib import admin
from django.urls import path
from django.urls.conf import include

from accounts.views import profile

# app_name = 'accounts'

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('login/', LoginView.as_view(), name='login'),
    # path('register/', RegisterView.as_view(), name='register'),
    path('accounts/profile/', profile, name='profile'),
    path('accounts/', include('allauth.urls')),
    path('', include('blacklist.urls')),
]
