"""
Dashboard admin configuration.
"""
from django.contrib import admin

from ..widgets import DashboardWidgets


class DashboardAdminSite(admin.AdminSite):
    """Custom admin site with dashboard."""

    site_header = 'سیستم مدیریت ابزار کارگاه'
    site_title = 'مدیریت ابزار'
    index_title = 'داشبورد مدیریت'

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(DashboardWidgets.get_all_dashboard_data())
        return super().index(request, extra_context)


dashboard_admin_site = DashboardAdminSite(name='dashboard_admin')


def _sync_default_admin_registry() -> None:
    """
    Copy all model registrations from Django's default admin site to the
    dashboard admin site so permissions and model visibility stay identical.
    """
    # Ensure app admin modules are imported and registered on admin.site first.
    import apps.inventory.admin  # noqa: F401
    import apps.transactions.admin  # noqa: F401
    import apps.maintenance.admin  # noqa: F401
    import apps.users.admin  # noqa: F401

    for model, model_admin in admin.site._registry.items():
        model_admin_class = model_admin.__class__
        if model not in dashboard_admin_site._registry:
            dashboard_admin_site.register(model, model_admin_class)


_sync_default_admin_registry()
