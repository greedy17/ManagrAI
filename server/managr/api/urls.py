from rest_framework import routers
from django.urls import include, path
from managr.core import views as core_views

from managr.lead import views as lead_views
from managr.polling import views as poll_views
from managr.organization import views as organization_views
from managr.report import views as report_views


app_name = "api"


router = routers.SimpleRouter()

urlpatterns = [
    path("login/", core_views.UserLoginView.as_view()),
    # NRS 5.28.2020 -- I think most of these can be moved to be detail views on the user
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
        "twilio/callback/messages",
        core_views.TwilioMessageWebhook.as_view(),
        name="twilio_messages_webhook",
    ),
    path(
        "twilio/list-available-numbers",
        core_views.list_available_twilio_numbers,
        name="list_available_twilio_numbers",
    ),
    path("twilio/list-messages", core_views.list_twilio_messages, name="list_messages"),
    path(
        "twilio/callback/messages/status",
        core_views.message_status,
        name="twilio_callback_message_status",
    ),
    path(
        "nylas/callback/accounts",
        core_views.NylasAccountWebhook.as_view(),
        name="nylas_account_webhook",
    ),
    path("polling/count", poll_views.list_polling_counts, name="list_polling_counts",),
]

router.register("users/invite", core_views.UserInvitationView, "invite-user")
router.register("users", core_views.UserViewSet, "users")
router.register("email-templates", core_views.EmailTemplateViewset, "email-templates")
router.register(
    "organizations", organization_views.OrganizationViewSet, "organizations"
)
router.register("accounts", organization_views.AccountViewSet, "accounts")
router.register("contacts", organization_views.ContactViewSet, "contacts")
router.register("leads/claim", lead_views.LeadViewSet, "leads-claim")
router.register("leads/un-claim", lead_views.LeadViewSet, "leads-un-claim")
router.register("leads", lead_views.LeadViewSet, "leads")
router.register("lists/add-to-list", lead_views.ListViewSet, "lists-add")
router.register("lists/remove-from-list", lead_views.ListViewSet, "lists-remove")
router.register("lists", lead_views.ListViewSet, "lists")
router.register("notes", lead_views.NoteViewSet, "notes")
router.register("call-notes", lead_views.CallNoteViewSet, "call-notes")
router.register("forecasts", lead_views.ForecastViewSet, "forecast")
router.register("reminders", lead_views.ReminderViewSet, "reminders")
router.register("action-choices", lead_views.ActionChoiceViewSet, "action-choices")
router.register("actions", lead_views.ActionViewSet, "actions")
router.register("lead-activity", lead_views.LeadActivityLogViewSet, "lead-activity")
router.register("story-reports", report_views.StoryReportViewSet, "story-reports")
router.register("performance-reports", report_views.PerformanceReportViewSet, "performance-reports")
router.register("files", lead_views.FileViewSet, "files")
router.register("notifications", lead_views.NotificationViewSet, "notifications")
router.register("stages", organization_views.StageViewSet, "stages")
router.register("lead-messages", lead_views.LeadMessageViewSet, "lead-messages")
router.register(
    "notifications/settings",
    core_views.NotificationSettingsViewSet,
    "notification-settings",
)
urlpatterns += router.urls

