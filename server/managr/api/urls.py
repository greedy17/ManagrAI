from django.conf.urls import url
from rest_framework import routers
from django.urls import include, path
from managr.core import views as core_views
from managr.api import views as api_views

app_name = 'api'


router = routers.SimpleRouter()


router.register(r'users/invite', core_views.UserInvitationView, 'invite-user')
router.register(r'users', core_views.UserViewSet, 'users')
router.register(r'organizations',
                api_views.OrganizationViewSet, 'organizations')
router.register(r'accounts', api_views.AccountViewSet, 'accounts')
router.register(r'contacts', api_views.ContactViewSet, 'contacts')


urlpatterns = [
    path(r'login/', core_views.UserLoginView.as_view())

]
urlpatterns += router.urls
print(urlpatterns)
