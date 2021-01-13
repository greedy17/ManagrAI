from rest_framework import routers
from django.urls import include, path
from managr.core import views as core_views
from managr.opportunity import views as opp_views
from managr.organization import views as organization_views
from managr.report import views as report_views
from managr.slack import views as slack_views
from managr.zoom import views as zoom_views
from managr.demo import views as demo_views


app_name = "api"


router = routers.SimpleRouter()

urlpatterns = [
    path("login/", core_views.UserLoginView.as_view()),
    # NRS 5.28.2020 -- I think most of these can be moved to be detail views on the user
    path(
        "demo/trigger-inactive/", demo_views.clear_activity_log, name="trigger-inactive"
    ),
    path("demo/trigger-stalled/", demo_views.stalled_in_stage, name="trigger-stalled"),
    path(
        "demo/trigger-late/", demo_views.past_expected_close_date, name="trigger-stage"
    ),
    path("demo/close-opp/", demo_views.close_lead, name="close-opp",),
    path(
        "demo/delete-meeting/", demo_views.delete_demo_meeting, name="delete-meeting",
    ),
    path(
        "demo/generate-meeting-scores/",
        demo_views.demo_generate_meeting_score,
        name="generate-meeting-scores",
    ),
    path(
        "users/activation_link/<email>/",
        core_views.ActivationLinkView.as_view(),
        name="get_activation_link",
    ),
    path(
        "users/email-auth-link/",
        core_views.get_email_authorization_link,
        name="get_email_auth_link",
    ),
    path(
        "users/email-auth-token/",
        core_views.email_auth_token,
        name="get_email_auth_token",
    ),
    path(
        "users/revoke-email-auth/",
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
        "nylas/callback/messages",
        core_views.NylasMessageWebhook.as_view(),
        name="nylas_message_webhook",
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
]


router.register("users/invite", core_views.UserInvitationView, "invite-user")
router.register("users", core_views.UserViewSet, "users")
router.register(
    "organizations", organization_views.OrganizationViewSet, "organizations"
)
router.register("accounts", organization_views.AccountViewSet, "accounts")
router.register("contacts", organization_views.ContactViewSet, "contacts")
router.register("story-reports", report_views.StoryReportViewSet, "story-reports")
router.register(
    "performance-reports", report_views.PerformanceReportViewSet, "performance-reports"
)



router.register(
    "notifications/settings",
    core_views.NotificationSettingsViewSet,
    "notification-settings",
)
router.register("zoom/meetings", zoom_views.ZoomMeetingViewSet, "zoom-meetings")

router.register("slack", slack_views.SlackViewSet, "slack")
urlpatterns += router.urls

