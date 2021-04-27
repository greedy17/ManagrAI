dd_api_key = "25b2181993daf9daab1344619d0cbf6b"
environments = [
  {
    name                      = "prod"
    app_image                 = "986523545926.dkr.ecr.us-east-1.amazonaws.com/thinknimble/managr/server:latest"
    app_image_scheduled_tasks = "986523545926.dkr.ecr.us-east-1.amazonaws.com/thinknimble/managr/server-tasks:latest"
    lb_http_port              = 8000
    lb_https_port             = 8443
  },
  {
    name                      = "staging"
    app_image                 = "986523545926.dkr.ecr.us-east-1.amazonaws.com/thinknimble/managr/server:latest"
    app_image_scheduled_tasks = "986523545926.dkr.ecr.us-east-1.amazonaws.com/thinknimble/managr/server-tasks:latest"
    lb_http_port              = 8001
    lb_https_port             = 8444
  },
  {
    name                      = "demo"
    app_image                 = "986523545926.dkr.ecr.us-east-1.amazonaws.com/thinknimble/managr/server:latest"
    app_image_scheduled_tasks = "986523545926.dkr.ecr.us-east-1.amazonaws.com/thinknimble/managr/server-tasks:latest"
    lb_http_port              = 8002
    lb_https_port             = 8445
  }
]
debug        = true
rds_username = "managr"
rds_password = "managrpass"
rds_db_name  = "managr"
local_ip     = "24.4.215.144"
secret_key   = "46k&m1sfubmvlus-!aygrs)_ls!t95dyl7u6**eatwryjnxig*"
staff_email  = "Pari Baker <pari@thinknimble.com>"
use_custom_smtp            = true
smtp_use_tls               = true
smtp_user                  = "postmaster@mg.managr.ai"
smtp_password              = "73fd031c5646615a7ad9edae87d1d724-77751bfc-d318e6ef"
smtp_host                  = "smtp.mailgun.org"
smtp_valid_testing_domains = "thinknimble.com"
use_rollbar = false
use_aws_storage         = true
aws_access_key_id       = "AKIA6LMLCWFDPMEMHJHU"
aws_secret_access_key   = "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"
aws_storage_bucket_name = "managr-new"
aws_location            = "dev"
aws_location_dev        = "dev"
aws_location_staging    = "dev"
aws_location_prod       = "prod"
use_nylas           = true
nylas_client_id     = "2th0vp5dkvmc1lkcvf41quqkf"
nylas_client_secret = "5jvvtb1zg8vuha4rxgqbqvfjj"
use_twilio               = true
twilio_account_sid       = "AC784182e7011308684b48ae153d9832df"
twilio_auth_token        = "3a4593dd73b2f790974f3a351a56f7cc"
twilio_base_callback_url = "https://thinknimble.ngrok.io"
use_zoom               = true
zoom_redirect_uri      = "https://thinknimble.ngrok.io/api/users/zoom/re-direct"
zoom_client_id         = "_zR_kgeCSISW0xlHfOxGBA"
zoom_secret            = "vmjmrVddDgYiADM0ND8CjyyV2nGOrByK"
zoom_webhook_token     = "hI1tapPUSiyjlM5lr8nh_g"
zoom_fake_meeting_uuid = "nXOYSZYkRoiAFCgv5ySM3w=="
use_slack            = true
slack_client_id      = "3505648522.1501477826485"
slack_secret         = "884a9bebac4020bbcfa129882948b276"
slack_signing_secret = "11307749697310001ace8c873ba1bb97"
slack_app_version    = "v0"
use_salesforce          = true
salesforce_base_url     = "https://login.salesforce.com"
salesforce_consumer_key = "3MVG9fe4g9fhX0E7ef.NWEyu20vDKu7kJQvCmsIXsgvH.Is2HTM197RNxTl25x.GuUhz5.2ihB71mLsjJmJ1K"
salesforce_secret       = "6D02BBDD72587CD5757E13F4584C943282DA1F41F76BBD7166189CD7963B833B"
salesforce_scopes       = ["id", "profile", "email", "address", "phone", "openid", "refresh_token", "web", "api"]
salesforce_redirect_uri = "settings/integrations"
salesforce_api_version  = "50.0"