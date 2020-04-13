from django.contrib import admin
from django.urls import re_path, path, include
from django.conf import settings
from django.conf.urls.static import static

from managr.core import views as core_views

urlpatterns = [
    path(r'admin/', admin.site.urls),
    #path(r'', include('spotandtango.core.favicon_urls')),
    path(r'api/', include('managr.api.urls', namespace='api')),
]

urlpatterns += [
    re_path(r'^$', core_views.index, name='index'),
    re_path(r'^.*/$', core_views.index, name='index'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
