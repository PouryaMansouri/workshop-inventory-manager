"""
URL configuration for Workshop Tool Inventory System.
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

# Customize admin site
admin.site.site_header = 'سیستم مدیریت ابزار کارگاه'
admin.site.site_title = 'مدیریت ابزار'
admin.site.index_title = 'داشبورد مدیریت'

# Override admin index template
admin.site.index_template = 'admin/index.html'

urlpatterns = [
    path('admin/', admin.site.urls),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
