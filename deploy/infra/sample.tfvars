managr_domain                   = "managr.ai"
dd_api_key                      = ""
s3_bucket_name                  = ""
s3_bucket_aws_access_key_id     = ""
s3_bucket_aws_secret_access_key = ""
environments = [
  {
    name                      = "prod"
    app_image                 = ""
    app_image_scheduled_tasks = ""
    lb_http_port              = 8000
    lb_https_port             = 8443

    s3_bucket_location = "prod"

    allowed_hosts  = ""
    current_domain = ""

    debug        = true
    rds_username = ""
    rds_password = ""
    rds_db_name  = ""
    secret_key   = ""
    staff_email  = ""

    use_custom_smtp            = true
    smtp_use_tls               = true
    smtp_user                  = ""
    smtp_password              = ""
    smtp_host                  = ""
    smtp_port                  = "587"
    smtp_valid_testing_domains = ""

    use_rollbar = false

    use_nylas                = true
    nylas_client_id          = ""
    nylas_client_secret      = ""
    nylas_oauth_callback_url = ""

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

    use_salesforce          = true
    salesforce_base_url     = ""
    salesforce_consumer_key = ""
    salesforce_secret       = ""
    salesforce_scopes       = ["id", "profile", "email", "address", "phone", "openid", "refresh_token", "web", "api"]
    salesforce_redirect_uri = ""
    salesforce_api_version  = ""
  },
  {
    name                      = "staging"
    app_image                 = ""
    app_image_scheduled_tasks = ""

    s3_bucket_location = "staging"

    allowed_hosts  = ""
    current_domain = ""

    lb_http_port  = 8001
    lb_https_port = 8444

    debug        = true
    rds_username = ""
    rds_password = ""
    rds_db_name  = ""
    secret_key   = ""
    staff_email  = ""

    use_custom_smtp            = true
    smtp_use_tls               = true
    smtp_user                  = ""
    smtp_password              = ""
    smtp_host                  = ""
    smtp_port                  = "587"
    smtp_valid_testing_domains = ""

    use_rollbar = false

    use_aws_storage                 = true
    s3_bucket_aws_access_key_id     = ""
    s3_bucket_aws_secret_access_key = ""
    s3_bucket_name                  = ""
    s3_bucket_location              = ""
    s3_bucket_location_dev          = ""
    s3_bucket_location_staging      = ""
    s3_bucket_location_prod         = ""

    use_nylas                = true
    nylas_client_id          = ""
    nylas_client_secret      = ""
    nylas_oauth_callback_url = ""

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

    use_salesforce          = true
    salesforce_base_url     = ""
    salesforce_consumer_key = ""
    salesforce_secret       = ""
    salesforce_scopes       = ["id", "profile", "email", "address", "phone", "openid", "refresh_token", "web", "api"]
    salesforce_redirect_uri = ""
    salesforce_api_version  = ""
  },
  {
    name                      = "demo"
    app_image                 = ""
    app_image_scheduled_tasks = ""

    s3_bucket_location = "demo"

    allowed_hosts  = ""
    current_domain = ""

    lb_http_port  = 8002
    lb_https_port = 8445

    debug        = true
    rds_username = ""
    rds_password = ""
    rds_db_name  = ""
    secret_key   = ""
    staff_email  = ""

    use_custom_smtp            = true
    smtp_use_tls               = true
    smtp_user                  = ""
    smtp_password              = ""
    smtp_host                  = ""
    smtp_port                  = "587"
    smtp_valid_testing_domains = ""

    use_rollbar = false

    use_aws_storage                 = true
    s3_bucket_aws_access_key_id     = ""
    s3_bucket_aws_secret_access_key = ""
    s3_bucket_name                  = ""
    s3_bucket_location              = ""
    s3_bucket_location_dev          = ""
    s3_bucket_location_staging      = ""
    s3_bucket_location_prod         = ""

    use_nylas                = true
    nylas_client_id          = ""
    nylas_client_secret      = ""
    nylas_oauth_callback_url = ""

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

    use_salesforce          = true
    salesforce_base_url     = ""
    salesforce_consumer_key = ""
    salesforce_secret       = ""
    salesforce_scopes       = ["id", "profile", "email", "address", "phone", "openid", "refresh_token", "web", "api"]
    salesforce_redirect_uri = ""
    salesforce_api_version  = ""
  }
]
