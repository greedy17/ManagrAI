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
from managr.outreach import views as outreach_views
from managr.hubspot import views as hubspot_views
from managr.crm import views as crm_views
from managr.comms import views as comms_views

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
    path("login-sso/", core_views.UserSSOLoginView.as_view()),
    path("logout/", core_views.UserLogoutView.as_view()),
    path("register/", core_views.UserRegistrationView.as_view()),
    path(
        "users/activation_link/<email>/",
        core_views.ActivationLinkView.as_view(),
        name="get_activation_link",
    ),
    path(
        "users/chat/add-message/",
        core_views.add_message,
        name="add_message",
    ),
    path(
        "users/chat/edit-message/",
        core_views.edit_message,
        name="edit_message",
    ),
    path(
        "users/chat/delete-messages/",
        core_views.delete_all_messages,
        name="delete_mmessages",
    ),
    path(
        "users/chat/submission/",
        core_views.submit_chat_prompt,
        name="submit_chat_prompt",
    ),
    path(
        "users/chat/ask-managr/",
        core_views.ask_managr,
        name="ask_managr",
    ),
    path(
        "users/chat/deal-review/",
        core_views.deal_review,
        name="deal_review",
    ),
    path(
        "users/chat/chat-transcript/",
        core_views.process_transcript,
        name="process_transcript",
    ),
    path(
        "users/comms/generate_content_transcript/",
        core_views.generate_content_transcript,
        name="generate_content_transcript",
    ),
    path(
        "users/chat/follow-up-email/",
        core_views.draft_follow_up,
        name="draft_follow_up",
    ),
    path(
        "users/chat/next-steps/",
        core_views.chat_next_steps,
        name="chat_next_steps",
    ),
    path(
        "users/chat/summary/",
        core_views.get_chat_summary,
        name="get_chat_summary",
    ),
    path(
        "users/chat/submit-chat-meeting/",
        core_views.log_chat_meeting,
        name="log_chat_meeting",
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
        "users/nylas/revoke/",
        core_views.revoke_access_token,
        name="revoke_email_auth",
    ),
    path(
        "users/send-activation-email/",
        core_views.send_activation_email,
        name="send_activation_email",
    ),
    path(
        "users/nylas/reply-to-email/",
        core_views.reply_to_email,
        name="reply_to_email",
    ),
    path("users/zoom/re-direct", zoom_views.redirect_from_zoom, name="redirect-from-zoom"),
    path(
        "users/salesloft/re-direct",
        salesloft_views.redirect_from_salesloft,
        name="redirect-from-salesloft",
    ),
    path(
        "users/gongaccount/re-direct",
        gong_views.redirect_from_gong,
        name="redirect-from-gong",
    ),
    path(
        "users/outreach/re-direct",
        outreach_views.redirect_from_outreach,
        name="redirect-from-outreach",
    ),
    path("users/slack/re-direct", slack_views.redirect_from_slack, name="redirect-from-slack"),
    path(
        "users/twitter/re-direct", comms_views.redirect_from_twitter, name="redirect-from-twitter"
    ),
    path("users/comms/upload-link/", comms_views.upload_link, name="upload-link"),
    path("account-status/", core_views.get_account_status, name="get_account_status"),
    path("task-status/", core_views.get_task_status, name="get-task-status"),
    path("sso-data/", core_views.get_sso_data, name="get-sso-data"),
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
        "users/twitter/authorization",
        comms_views.get_twitter_auth_link,
        name="get_twitter_auth_link",
    ),
    path(
        "users/twitter/authenticate",
        comms_views.get_twitter_authentication,
        name="get_twitter_authentication",
    ),
    path(
        "users/zoom/revoke",
        zoom_views.revoke_zoom_access_token,
        name="revoke_zoom_access_token",
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
        "users/gongaccount/authorization",
        gong_views.get_gong_auth_link,
        name="get-gong-auth-link",
    ),
    path(
        "users/gongaccount/revoke",
        gong_views.revoke_gong_access_token,
        name="revoke-gong-access-token",
    ),
    path(
        "users/outreach/authenticate",
        outreach_views.get_outreach_authentication,
        name="get-outreach-authentication",
    ),
    path(
        "users/outreach/authorization/",
        outreach_views.get_outreach_auth_link,
        name="get-outreach-auth-link",
    ),
    path(
        "users/outreach/revoke",
        outreach_views.revoke_outreach_access_token,
        name="revoke-outreach-access_token",
    ),
    path(
        "zoom/get-meetings",
        zoom_views.get_meetings,
        name="get_meetings",
    ),
    path(
        "zoom/check-for-transcript",
        zoom_views.check_for_transcript,
        name="check_for_transcript",
    ),
    path(
        "zoom/webhooks/deauthorize",
        zoom_views.zoom_deauth_webhook,
        name="zoom_deauth",
    ),
    path(
        "zoom/webhooks/meetings",
        zoom_views.zoom_meetings_webhook,
        name="get_zoom_auth_link",
    ),
    path(
        "zoom/webhooks/recordings",
        zoom_views.zoom_recordings_webhook,
        name="get_zoom_recording",
    ),
    path(
        "stripe/webhooks/session-complete",
        core_views.session_complete_webhook,
        name="session_complete",
    ),
    path("zoom/fake-recording", zoom_views.fake_recording, name="fake-recording"),
    path("users/zoom/schedule-meeting", zoom_views.schedule_zoom_meeting, name="schedule-meeting"),
    path(
        "users/salesforce/authorization",
        sf_views.salesforce_auth_link,
        name="salesforce-authorization",
    ),
    path(
        "users/salesforce/authenticate",
        sf_views.authenticate,
        name="salesforce-authentication",
    ),
    path(
        "users/salesforce/revoke",
        sf_views.revoke,
        name="salesforce-revoke",
    ),
    path(
        "users/hubspot/authorization/",
        hubspot_views.get_hubspot_auth_link,
        name="get-hubspot-auth-link",
    ),
    path(
        "users/hubspot/authenticate",
        hubspot_views.get_hubspot_authentication,
        name="get-hubspot-authentication",
    ),
    path(
        "users/hubspot/re-direct",
        hubspot_views.redirect_from_hubspot,
        name="redirect-from-hubspot",
    ),
    path(
        "users/hubspot/revoke",
        hubspot_views.revoke_hubspot_access_token,
        name="revoke-hubspot-access-token",
    ),
    path(
        "zoom/fake-meeting",
        zoom_views.init_fake_meeting,
        name="init-meeting",
    ),
    path(
        "slack/commands/create-task",
        slack_views.create_task,
        name="create-task",
    ),
    path(
        "slack/commands/add-to-cadence",
        slack_views.add_to_cadence,
        name="add-to-cadence",
    ),
    path(
        "slack/commands/schedule-meeting",
        slack_views.schedule_meeting_command,
        name="schedule-meeting",
    ),
    path(
        "slack/commands/notes",
        slack_views.get_notes_command,
        name="get-notes",
    ),
    path(
        "slack/commands/actions",
        slack_views.launch_action,
        name="launch-action",
    ),
    path(
        "slack/commands/create-resource",
        slack_views.create_resource,
        name="create-resource",
    ),
    path(
        "slack/webhooks/events",
        slack_views.slack_events,
        name="slack-events",
    ),
    path(
        "slack/commands/update-resource",
        slack_views.update_resource,
        name="update-resource",
    ),
    path(
        "slack/commands/list-tasks",
        slack_views.list_tasks,
        name="list-tasks",
    ),
    path(
        "auto/clear-stale-data",
        auto_views.init_clear_stale_data,
        name="clear-stale-data",
    ),
    path(
        "auto/sync-resources",
        auto_views.init_resource_sync,
        name="resource-sync",
    ),
    path(
        "auto/sync-fields",
        auto_views.init_object_field_sync,
        name="object-field-sync",
    ),
    path(
        "auto/trigger-alerts",
        auto_views.init_trigger_alerts,
        name="trigger-alerts",
    ),
    path("shared/<str:encrypted_param>", comms_views.get_shared_summary, "shared"),
    path(
        "users/twitter/authorization",
        comms_views.get_twitter_auth_link,
        name="twitter-authorization",
    ),
    path(
        "users/twitter/authenticate",
        comms_views.get_twitter_authentication,
        name="twitter-authentication",
    ),
    path(
        "users/twitter/re-direct",
        comms_views.redirect_from_twitter,
        name="redirect-twitter",
    ),
    path(
        "users/twitter/request-token/",
        comms_views.get_twitter_request_token,
        name="twitter-request-token",
    ),
    path(
        "users/twitter/revoke-token/",
        comms_views.revoke_twitter_auth,
        name="twitter-revoke-token",
    ),
    path(
        "pr/clips/",
        comms_views.get_clips,
        name="get-clips",
    ),
]

router.register("users/reports", core_views.ReportViewSet, "reports"),
router.register("users/conversations", core_views.ConversationViewSet, "conversations"),
router.register("users/invite", core_views.UserInvitationView, "invite-user")
router.register("users", core_views.UserViewSet, "users")
router.register("note-template", core_views.NoteTemplateViewSet, "note-template")
router.register("organizations", organization_views.OrganizationViewSet, "organizations")
router.register("accounts", organization_views.AccountViewSet, "accounts")
router.register("contacts", organization_views.ContactViewSet, "contacts")
router.register("action-choices", organization_views.ActionChoiceViewSet, "action-choices")
router.register("crm-objects", crm_views.CRMObjectViewSet, "crm-objects")
router.register("crm/fields", crm_views.ObjectFieldViewSet, "crm-fields")
router.register("organization/teams", organization_views.TeamViewSet, "organization-teams")
router.register("salesforce/fields", sf_views.SObjectFieldViewSet, "salesforce-fields")
router.register("salesforce/sobject", sf_views.SalesforceSObjectViewSet, "salesforce-sobject")
router.register(
    "salesforce/meeting-workflows", sf_views.MeetingWorkflowViewSet, "meeting-workflows"
)
router.register("salesforce/public-fields", sf_views.PublicSObjectFieldViewSet, "public-fields")
router.register(
    "salesforce/validations", sf_views.SObjectValidationViewSet, "salesforce-validation"
)
router.register("salesforce/picklists", sf_views.SObjectPicklistViewSet, "salesforce-picklists")

router.register("slack", slack_views.SlackViewSet, "slack")
router.register("slack/forms", slack_views.SlackFormsViewSet, "slack-forms")
router.register("slack/instances", slack_views.SlackFormInstanceViewSet, "slack-form-instances"),
router.register("alerts/templates", alert_views.AlertTemplateViewSet, "alert-templates")
router.register(
    "alerts/message-templates", alert_views.AlertMessageTemplateViewSet, "alert-message-templates"
)
router.register("alerts/operands", alert_views.AlertOperandViewSet, "alert-operands")
router.register("alerts/groups", alert_views.AlertGroupViewSet, "alert-groups")
router.register("alerts/configs", alert_views.AlertConfigViewSet, "alert-configs")
router.register(
    "alerts/real-time-configs", alert_views.RealTimeAlertConfigViewSet, "real-time-alert-configs"
)
router.register("alerts/instances", alert_views.AlertInstanceViewSet, "alert-instance")
router.register("alerts/real-time", alert_views.RealTimeAlertViewSet, "real-time-alerts")
router.register("prsearch", comms_views.PRSearchViewSet, "prsearch")
router.register("pitches", comms_views.PitchViewSet, "pitches")
router.register("email-alerts", comms_views.EmailAlertViewSet, "email-alerts")
router.register("process", comms_views.ProcessViewSet, "process")
urlpatterns += router.urls
