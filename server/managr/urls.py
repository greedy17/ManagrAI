from django.contrib import admin
from django.urls import re_path, path, include
from django.conf import settings
from django.conf.urls.static import static
from managr.core import views as core_views

urlpatterns = [
    path(r"admin/", admin.site.urls),
    path(r"api/", include("managr.api.urls", namespace="api")),
    *(
        [path(r"", include("managr.core.favicon_urls"))]
        if not settings.IN_CI and not settings.IN_DEV
        else []
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

# These routes should come last, so that the application always falls back
# to the single-page app (SPA).
urlpatterns += [
    re_path(r"^$", core_views.index, name="index"),
    re_path(r"^.*/$", core_views.index, name="index"),
]
