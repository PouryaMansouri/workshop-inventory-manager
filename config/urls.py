"""
URL configuration for Workshop Tool Inventory System.
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from apps.dashboard.admin import dashboard_admin_site
from apps.dashboard.views import my_tools_view, my_tools_history_view

urlpatterns = [
    path('', RedirectView.as_view(url='/my-tools/', permanent=False), name='root_redirect'),
    path('admin/', dashboard_admin_site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('my-tools/', my_tools_view, name='my_tools'),
    path('my-tools/history/', my_tools_history_view, name='my_tools_history'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
