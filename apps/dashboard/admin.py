"""
Custom admin site with dashboard.
"""
from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from .widgets import DashboardWidgets


class DashboardAdminSite(admin.AdminSite):
    """Custom admin site with dashboard."""
    
    site_header = 'سیستم مدیریت ابزار کارگاه'
    site_title = 'مدیریت ابزار'
    index_title = 'داشبورد مدیریت'
    
    def index(self, request, extra_context=None):
        """
        Display custom dashboard on admin index page.
        """
        extra_context = extra_context or {}
        
        # Get dashboard data
        dashboard_data = DashboardWidgets.get_all_dashboard_data()
        extra_context.update(dashboard_data)
        
        return super().index(request, extra_context)


# Create custom admin site instance
dashboard_admin_site = DashboardAdminSite(name='dashboard_admin')
