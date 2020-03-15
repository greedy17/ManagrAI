from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path, path, include

from rest_framework import routers
from rest_auth import views as rest_auth_views

from . import views

router = routers.DefaultRouter()
router.register('users', views.UserViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/login/', views.UserLoginView.as_view()),
    path(r'api/password/reset/confirm/',
         rest_auth_views.PasswordResetConfirmView.as_view(),
         # This URL must be named, because django.contrib.auth calls it via a reverse-lookup
         name='password_reset_confirm'),
    path(r'api/password/reset/',
         rest_auth_views.PasswordResetView.as_view()),
    path(r'api/password/change/',
         rest_auth_views.PasswordChangeView.as_view()),
    re_path(r'^$', views.index, name='index'),
    re_path(r'^.*/$', views.index, name='index'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
