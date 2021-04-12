dd_api_key = ""
environments = [
  {
    name                      = "staging"
    app_image                 = "529218094138.dkr.ecr.us-east-2.amazonaws.com/thinknimble/managr/server:latest"
    app_image_scheduled_tasks = "529218094138.dkr.ecr.us-east-2.amazonaws.com/thinknimble/managr/server:latest"
    lb_http_port              = 8001
    lb_https_port             = 8444
  },
  {
    name                      = "prod"
    app_image                 = "529218094138.dkr.ecr.us-east-2.amazonaws.com/thinknimble/managr/server:latest"
    app_image_scheduled_tasks = "529218094138.dkr.ecr.us-east-2.amazonaws.com/thinknimble/managr/server:latest"
    lb_http_port              = 8000
    lb_https_port             = 8443
  }
]
debug        = true
rds_username = ""
rds_password = ""
rds_db_name  = ""
local_ip     = ""
secret_key   = ""
staff_email  = ""

use_custom_smtp            = true
smtp_use_tls               = true
smtp_user                  = ""
smtp_password              = ""
smtp_host                  = ""
smtp_valid_testing_domains = ""

use_rollbar = false

use_aws_storage         = true
aws_access_key_id       = ""
aws_secret_access_key   = ""
aws_storage_bucket_name = ""
aws_location            = ""
aws_location_dev        = ""
aws_location_staging    = ""
aws_location_prod       = ""

use_nylas           = true
nylas_client_id     = ""
nylas_client_secret = ""

use_twilio               = true
twilio_account_sid       = ""
twilio_auth_token        = ""
twilio_base_callback_url = ""

use_zoom               = true
zoom_redirect_uri      = ""
zoom_client_id         = ""
zoom_secret            = ""
zoom_webhook_token     = ""
zoom_fake_meeting_uuid = ""

use_slack            = true
slack_client_id      = ""
slack_secret         = ""
slack_signing_secret = ""
slack_app_version    = ""

test_slack                                    = false
slack_test_team_name                          = ""
slack_test_team_id                            = ""
slack_test_bot_user_id                        = ""
slack_test_access_token                       = ""
slack_test_incoming_webhook_url               = ""
slack_test_incoming_webhook_channel           = ""
slack_test_incoming_webhook_channel_id        = ""
slack_test_incoming_webhook_configuration_url = ""

use_salesforce          = true
salesforce_base_url     = ""
salesforce_consumer_key = ""
salesforce_secret       = ""
salesforce_scopes       = ["id", "profile", "email", "address", "phone", "openid", "refresh_token", "web", "api"]
salesforce_redirect_uri = ""
salesforce_api_version  = ""
