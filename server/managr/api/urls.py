from rest_framework import routers
from django.urls import path
from managr.core import views as core_views
from managr.organization import views as organization_views

# from managr.report import views as report_views
from managr.slack import views as slack_views
from managr.zoom import views as zoom_views
from managr.salesforce import views as sf_views


app_name = "api"


router = routers.SimpleRouter()

urlpatterns = [
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
    path(
        "users/nylas/authenticate/",
        core_views.email_auth_token,
        name="get_email_auth_token",
    ),
    path(
        "users/nylas/revoke-email-auth/",
        core_views.revoke_access_token,
        name="revoke_email_auth",
    ),
    path(
        "users/zoom/re-direct", zoom_views.redirect_from_zoom, name="redirect-from-zoom"
    ),
    path("account-status/", core_views.get_account_status, name="get_account_status"),
    path(
        "get-file/<str:file_id>/",
        core_views.GetFileView.as_view(),
        name="get_file_from_nylas",
    ),
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
    path(
        "users/zoom/authorization",
        zoom_views.get_zoom_auth_link,
        name="get_zoom_auth_link",
    ),
    path(
        "users/zoom/revoke",
        zoom_views.revoke_zoom_access_token,
        name="revoke_zoom_access_token",
    ),
    path(
        "zoom/webhooks/meetings",
        zoom_views.zoom_meetings_webhook,
        name="get_zoom_auth_link",
    ),
    path(
        "salesforce/authorization",
        sf_views.salesforce_auth_link,
        name="salesforce-authorization",
    ),
    path(
        "salesforce/authenticate",
        sf_views.authenticate,
        name="salesforce-authentication",
    ),
]


router.register("users/invite", core_views.UserInvitationView, "invite-user")
router.register("users", core_views.UserViewSet, "users")
router.register(
    "organizations", organization_views.OrganizationViewSet, "organizations"
)
router.register("accounts", organization_views.AccountViewSet, "accounts")
router.register("contacts", organization_views.ContactViewSet, "contacts")

""" router.register("story-reports", report_views.StoryReportViewSet, "story-reports")
router.register(
    "performance-reports", report_views.PerformanceReportViewSet, "performance-reports"
)
router.register(
    "notifications/settings",
    core_views.NotificationSettingsViewSet,
    "notification-settings",
)
"""


router.register("zoom/meetings", zoom_views.ZoomMeetingViewSet, "zoom-meetings")

router.register("slack", slack_views.SlackViewSet, "slack")
urlpatterns += router.urls
