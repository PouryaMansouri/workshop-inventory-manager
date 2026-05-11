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
from apps.dashboard.views import (
    home_view,
    logout_view,
    my_tools_view,
    my_tools_history_view,
    assigned_items_report_view,
    assigned_items_report_export_xlsx,
    holder_tools_lookup_view,
)

urlpatterns = [
    path('', RedirectView.as_view(url='/home/', permanent=False), name='root_redirect'),
    path('home/', home_view, name='home'),
    path('admin/', dashboard_admin_site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', logout_view, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('my-tools/', my_tools_view, name='my_tools'),
    path('my-tools/history/', my_tools_history_view, name='my_tools_history'),
    path('reports/assigned-items/', assigned_items_report_view, name='assigned_items_report'),
    path('reports/assigned-items/export.xlsx', assigned_items_report_export_xlsx, name='assigned_items_report_export_xlsx'),
    path('reports/holder-tools/', holder_tools_lookup_view, name='holder_tools_lookup'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
