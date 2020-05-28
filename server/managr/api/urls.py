from django.conf.urls import url
from rest_framework import routers
from django.urls import include, path
from managr.core import views as core_views

from managr.lead import views as lead_views
from managr.organization import views as organization_views


app_name = 'api'


router = routers.SimpleRouter()

urlpatterns = [
    path(r'login/', core_views.UserLoginView.as_view()),
    path(
        'users/activation_link/<email>/',
        core_views.ActivationLinkView.as_view(),
        name="get_activation_link",
    ),
    url(
        r'users/email-auth-link/',
        core_views.get_email_authorization_link,
        name="get_email_auth_link",
    ),
    url(r'users/email-auth-token/', core_views.email_auth_token, name="get_email_auth_token"),
    url(r'users/revoke-email-auth', core_views.revoke_access_token, name="revoke_email_auth"),
    url(r'account-status/', core_views.get_account_status, name='get_account_status'),
]

router.register(r'users/invite', core_views.UserInvitationView, 'invite-user')
router.register(r'users', core_views.UserViewSet, 'users')
router.register(r'organizations', organization_views.OrganizationViewSet, 'organizations')
router.register(r'accounts', organization_views.AccountViewSet, 'accounts')
router.register(r'contacts', organization_views.ContactViewSet, 'contacts')
router.register(r'leads/claim', lead_views.LeadViewSet, 'leads-claim')
router.register(r'leads/un-claim', lead_views.LeadViewSet, 'leads-un-claim')
router.register(r'leads', lead_views.LeadViewSet, 'leads')
router.register(r'lists/add-to-list', lead_views.ListViewSet, 'lists-add')
router.register(r'lists/remove-from-list', lead_views.ListViewSet, 'lists-remove')
router.register(r'lists', lead_views.ListViewSet, 'lists')
router.register(r'notes', lead_views.NoteViewSet, 'notes')
router.register(r'call-notes', lead_views.CallNoteViewSet, 'call-notes')
router.register(r'forecasts', lead_views.ForecastViewSet, 'forecast')
router.register(r'reminders', lead_views.ReminderViewSet, 'reminders')
router.register(r'actionchoices', lead_views.ActionChoiceViewSet, 'actionchoices')
router.register(r'actions', lead_views.ActionViewSet, 'actions')

router.register(r'action-choices', lead_views.ActionChoiceViewSet, 'action-choices')
router.register(r'actions', lead_views.ActionViewSet, 'actions')
router.register(r'files', lead_views.FileViewSet, 'files')


urlpatterns += router.urls
