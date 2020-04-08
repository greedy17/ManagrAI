from django.conf.urls import url
from rest_framework import routers
from django.urls import include, path
from managr.core import views as core_views

app_name = 'api'


router = routers.SimpleRouter()
router.register(r'users', core_views.UserViewSet, 'users')
router.register(r'users/invite', core_views.UserInvitationView, 'invite-user')

urlpatterns = [
    path(r'login/', core_views.UserLoginView.as_view())

]
urlpatterns += router.urls
