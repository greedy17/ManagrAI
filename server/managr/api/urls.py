from rest_framework import routers
from django.urls import path
from managr.core import views as core_views
from managr.organization import views as organization_views
from rest_auth import views as rest_auth_views

# from managr.report import views as report_views
from managr.slack import views as slack_views
from managr.zoom import views as zoom_views
from managr.salesforce import views as sf_views
from managr.alerts import views as alert_views
from managr.autonomous import views as auto_views
from managr.salesloft import views as salesloft_views
from managr.gong import views as gong_views

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
    path(
        "users/salesloft/re-direct",
        salesloft_views.redirect_from_salesloft,
        name="redirect-from-salesloft",
    ),
    path("users/gongaccount/re-direct", gong_views.redirect_from_gong, name="redirect-from-gong",),
    path("users/slack/re-direct", slack_views.redirect_from_slack, name="redirect-from-slack"),
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
    path(
        "users/salesloft/authenticate",
        salesloft_views.get_salesloft_authentication,
        name="get_salesloft_authentication",
    ),
    path(
        "users/salesloft/authorization",
        salesloft_views.get_salesloft_auth_link,
        name="get_salesloft_auth_link",
    ),
    path(
        "users/salesloft/revoke",
        salesloft_views.revoke_salesloft_access_token,
        name="revoke_salesloft_access_token",
    ),
    path(
        "users/gongaccount/authenticate",
        gong_views.get_gong_authentication,
        name="get-gong-authentication",
    ),
    path(
        "users/gongaccount/authorization", gong_views.get_gong_auth_link, name="get-gong-auth-link",
    ),
    path(
        "users/gongaccount/revoke",
        gong_views.revoke_gong_access_token,
        name="revoke-gong-access-token",
    ),
    path("zoom/webhooks/deauthorize", zoom_views.zoom_deauth_webhook, name="zoom_deauth",),
    path("zoom/webhooks/meetings", zoom_views.zoom_meetings_webhook, name="get_zoom_auth_link",),
    path(
        "zoom/webhooks/recordings", zoom_views.zoom_recordings_webhook, name="get_zoom_recording",
    ),
    path("zoom/fake-recording", zoom_views.fake_recording, name="fake-recording"),
    path(
        "users/salesforce/authorization",
        sf_views.salesforce_auth_link,
        name="salesforce-authorization",
    ),
    path("users/salesforce/authenticate", sf_views.authenticate, name="salesforce-authentication",),
    path("users/salesforce/revoke", sf_views.revoke, name="salesforce-revoke",),
    path("zoom/fake-meeting", zoom_views.init_fake_meeting, name="init-meeting",),
    path("slack/commands/create-task", slack_views.create_task, name="create-task",),
    path("slack/commands/add-to-cadence", slack_views.add_to_cadence, name="add-to-cadence",),
    path(
        "slack/commands/schedule-meeting",
        slack_views.schedule_meeting_command,
        name="schedule-meeting",
    ),
    path("slack/commands/notes", slack_views.get_notes_command, name="get-notes",),
    path("slack/list-public-channels", slack_views.create_task, name="list-public-channels",),
    path("slack/commands/create-resource", slack_views.create_resource, name="create-resource",),
    path("slack/webhooks/events", slack_views.slack_events, name="slack-events",),
    path("slack/commands/update-resource", slack_views.update_resource, name="update-resource",),
    path("slack/commands/list-tasks", slack_views.list_tasks, name="list-tasks",),
    path("auto/clear-stale-data", auto_views.init_clear_stale_data, name="clear-stale-data",),
    path("auto/sync-resources", auto_views.init_resource_sync, name="resource-sync",),
    path("auto/sync-fields", auto_views.init_object_field_sync, name="object-field-sync",),
    path("auto/trigger-alerts", auto_views.init_trigger_alerts, name="trigger-alerts",),
]


router.register("users/invite", core_views.UserInvitationView, "invite-user")
router.register("users", core_views.UserViewSet, "users")
router.register("organizations", organization_views.OrganizationViewSet, "organizations")
router.register("accounts", organization_views.AccountViewSet, "accounts")
router.register("contacts", organization_views.ContactViewSet, "contacts")
router.register("action-choices", organization_views.ActionChoiceViewSet, "action-choices")
router.register("salesforce/fields", sf_views.SObjectFieldViewSet, "salesforce-fields")
router.register("salesforce/public-fields", sf_views.PublicSObjectFieldViewSet, "public-fields")
router.register(
    "salesforce/validations", sf_views.SObjectValidationViewSet, "salesforce-validation"
)
router.register("salesforce/picklists", sf_views.SObjectPicklistViewSet, "salesforce-picklists")

router.register("slack", slack_views.SlackViewSet, "slack")
router.register("slack/forms", slack_views.SlackFormsViewSet, "slack-forms")
router.register("alerts/templates", alert_views.AlertTemplateViewSet, "alert-templates")
router.register(
    "alerts/message-templates", alert_views.AlertMessageTemplateViewSet, "alert-message-templates"
)
router.register("alerts/operands", alert_views.AlertOperandViewSet, "alert-operands")
router.register("alerts/groups", alert_views.AlertGroupViewSet, "alert-groups")
router.register("alerts/configs", alert_views.AlertConfigViewSet, "alert-configs")
urlpatterns += router.urls
