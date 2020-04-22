from django.conf.urls import url
from rest_framework import routers
from django.urls import include, path
from managr.core import views as core_views
from managr.api import views as api_views
from managr.lead import views as lead_views

app_name = 'api'


router = routers.SimpleRouter()


router.register(r'users/invite', core_views.UserInvitationView, 'invite-user')
router.register(r'users', core_views.UserViewSet, 'users')
router.register(r'organizations',
                api_views.OrganizationViewSet, 'organizations')
router.register(r'accounts', api_views.AccountViewSet, 'accounts')
router.register(r'contacts', api_views.ContactViewSet, 'contacts')
router.register(r'leads/claim', lead_views.LeadViewSet, 'leads-claim')
router.register(r'leads/un-claim', lead_views.LeadViewSet, 'leads-un-claim')
router.register(r'leads', lead_views.LeadViewSet, 'leads')
router.register(r'lists/add-to-list', lead_views.ListViewSet, 'lists-add')
router.register(r'lists/remove-from-list',
                lead_views.ListViewSet, 'lists-remove')
router.register(r'lists', lead_views.ListViewSet, 'lists')
router.register(r'notes', lead_views.NoteViewSet, 'notes')
router.register(r'forecasts', lead_views.ForecastViewSet, 'forecast')
router.register(r'reminders', lead_views.ReminderViewSet, 'reminders')
router.register(r'actionchoices',
                lead_views.ActionChoiceViewSet, 'actionchoices')
router.register(r'actions', lead_views.ActionViewSet, 'actions')

urlpatterns = [
    path(r'login/', core_views.UserLoginView.as_view()),
    url(r'account-status/', core_views.get_account_status,
        name='get_account_status')

]
urlpatterns += router.urls
print(urlpatterns)
