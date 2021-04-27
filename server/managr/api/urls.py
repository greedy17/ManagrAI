from rest_framework import routers
from django.urls import path
from managr.core import views as core_views
from managr.organization import views as organization_views
from rest_auth import views as rest_auth_views

# from managr.report import views as report_views
from managr.slack import views as slack_views
from managr.zoom import views as zoom_views
from managr.salesforce import views as sf_views

# from . import views


app_name = "api"


router = routers.SimpleRouter()

urlpatterns = [
    path(r"users/password/reset/", core_views.UserPasswordManagmentView.as_view()),
    path(r"users/password/reset/link/", core_views.request_reset_link, name="request-reset-link"),
    path(
        r"password/reset/confirm/",
        rest_auth_views.PasswordResetConfirmView.as_view(),
        # This URL must be named, because django.contrib.auth calls it via a reverse-lookup
        name="password_reset_confirm",
    ),
    path(r"password/reset/", rest_auth_views.PasswordResetView.as_view()),
    path(r"password/change/", rest_auth_views.PasswordChangeView.as_view()),
    path("login/", core_views.UserLoginView.as_view()),
    path("register/", core_views.UserRegistrationView.as_view()),
    path(
        "users/activation_link/<email>/",
        core_views.ActivationLinkView.as_view(),
        name="get_activation_link",
    ),
    path(
        "users/nylas/authorization/",
        core_views.get_email_authorization_link,
        name="get_email_auth_link",
    ),
    path("users/nylas/authenticate/", core_views.email_auth_token, name="get_email_auth_token",),
    path("users/nylas/revoke/", core_views.revoke_access_token, name="revoke_email_auth",),
    path("users/zoom/re-direct", zoom_views.redirect_from_zoom, name="redirect-from-zoom"),
    path("account-status/", core_views.get_account_status, name="get_account_status"),
    path("get-file/<str:file_id>/", core_views.GetFileView.as_view(), name="get_file_from_nylas",),
    path(
        "nylas/callback/accounts",
        core_views.NylasAccountWebhook.as_view(),
        name="nylas_account_webhook",
    ),
    path(
        "users/zoom/authenticate",
        zoom_views.get_zoom_authentication,
        name="get_zoom_authentication",
    ),
    path("users/zoom/authorization", zoom_views.get_zoom_auth_link, name="get_zoom_auth_link",),
    path(
        "users/zoom/revoke", zoom_views.revoke_zoom_access_token, name="revoke_zoom_access_token",
    ),
    path("zoom/webhooks/deauthorize", zoom_views.zoom_deauth_webhook, name="zoom_deauth",),
    path("zoom/webhooks/meetings", zoom_views.zoom_meetings_webhook, name="get_zoom_auth_link",),
    path(
        "users/salesforce/authorization",
        sf_views.salesforce_auth_link,
        name="salesforce-authorization",
    ),
    path("users/salesforce/authenticate", sf_views.authenticate, name="salesforce-authentication",),
    path("users/salesforce/revoke", sf_views.revoke, name="salesforce-revoke",),
    path("zoom/fake-meeting", zoom_views.init_fake_meeting, name="init-meeting",),
    path("slack/commands/create-task", slack_views.create_task, name="create-task",),
    path("slack/commands/update-resource", slack_views.update_resource, name="update-resource",),
    path("slack/commands/list-tasks", slack_views.list_tasks, name="list-tasks",),
    path("zoom/score-meetings", zoom_views.score_meetings, name="score-meetings",),
]


router.register("users/invite", core_views.UserInvitationView, "invite-user")
router.register("users", core_views.UserViewSet, "users")
router.register("organizations", organization_views.OrganizationViewSet, "organizations")
router.register("accounts", organization_views.AccountViewSet, "accounts")
router.register("contacts", organization_views.ContactViewSet, "contacts")
router.register("action-choices", organization_views.ActionChoiceViewSet, "action-choices")
router.register("salesforce/fields", sf_views.SObjectFieldViewSet, "salesforce-fields")
router.register(
    "salesforce/validations", sf_views.SObjectValidationViewSet, "salesforce-validation"
)
router.register("salesforce/picklists", sf_views.SObjectPicklistViewSet, "salesforce-picklists")

router.register("slack", slack_views.SlackViewSet, "slack")
router.register("slack/forms", slack_views.SlackFormsViewSet, "slack-forms")
urlpatterns += router.urls
