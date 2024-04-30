variable "managr_domain" {
  type    = string
  default = "managr.ai"
}

variable "ecs_task_role_name" {
  default = "ManagrEcsTaskRole"
}

variable "ecs_task_execution_role_name" {
  default = "ManagrEcsTaskExecutionRole"
}

variable "az_count" {
  type    = number
  default = 2
}

variable "app_count" {
  type    = number
  default = 2
}

variable "health_check_path" {
  type    = string
  default = "/"
}

variable "fargate_cpu" {
  type    = string
  default = "2048"
}

variable "fargate_memory" {
  type    = string
  default = "4096"
}

variable "dd_api_key" {
  type      = string
  sensitive = true
  default   = ""
}

variable "s3_bucket_name" {
  type    = string
  default = ""
}

variable "s3_bucket_aws_access_key_id" {
  type    = string
  default = ""
}

variable "s3_bucket_aws_secret_access_key" {
  type = string
}

variable "ecr_repo_names" {
  type    = set(string)
  default = ["thinknimble/managr/server", "thinknimble/managr/server-tasks", "thinknimble/managr/nginx", "thinknimble/managr/bash", "thinknimble/managr/datadog/agent"]
}

variable "environments" {
  type = set(object({
    name                      = string
    app_image                 = string
    app_image_scheduled_tasks = string

    use_aws_storage    = bool
    s3_bucket_location = string

    allowed_hosts  = string
    current_domain = string

    debug              = bool
    environment        = string
    rds_username       = string
    rds_password       = string
    rds_instance_name  = string
    rds_db_name        = string
    rds_db_snapshot_id = string
    secret_key         = string
    staff_email        = string
    superuser_email    = string
    superuser_password = string

    use_custom_smtp            = bool
    smtp_use_tls               = bool
    smtp_user                  = string
    smtp_password              = string
    smtp_host                  = string
    smtp_port                  = string
    smtp_valid_testing_domains = string

    use_rollbar          = bool
    rollbar_access_token = string

    use_nylas                = bool
    nylas_client_id          = string
    nylas_client_secret      = string
    nylas_oauth_callback_url = string

    use_twilio               = bool
    twilio_account_sid       = string
    twilio_auth_token        = string
    twilio_base_callback_url = string

    use_zoom               = bool
    zoom_redirect_uri      = string
    zoom_client_id         = string
    zoom_secret            = string
    zoom_webhook_token     = string
    zoom_fake_meeting_uuid = string

    use_slack            = bool
    slack_client_id      = string
    slack_secret         = string
    slack_signing_secret = string
    slack_app_version    = string
    slack_error_webhook  = string

    use_salesforce          = bool
    salesforce_base_url     = string
    salesforce_consumer_key = string
    salesforce_secret       = string
    salesforce_scopes       = set(string)
    salesforce_redirect_uri = string
    salesforce_api_version  = string

    use_salesloft           = bool
    salesloft_base_url      = string
    salesloft_client_id     = string
    salesloft_secret        = string
    salesloft_redirect_uri  = string
    
    use_gong                = bool
    gong_base_url           = string
    gong_client_id          = string
    gong_secret             = string
    gong_redirect_uri       = string

    use_outreach            = bool
    outreach_base_url       = string
    outreach_client_id      = string
    outreach_secret         = string
    outreach_redirect_uri   = string

    use_hubspot            = bool
    hubspot_base_url       = string
    hubspot_client_id      = string
    hubspot_secret         = string
    hubspot_redirect_uri   = string

    use_open_ai            = bool
    open_ai_secret         = string

    use_sso                = bool
    microsoft_secret_key   = string
    google_client_id       = string
    google_login_uri       = string

    use_news_api           = bool
    news_api_key           = string

    use_twitter_api        = bool
    twitter_api_key        = string
    twitter_api_secret     = string
    twitter_client_id      = string
    twitter_redirect_uri   = string
    twitter_access_token   = string

    stripe_api_key         = string
    stripe_price_id        = string

    use_instagram_api      = bool
    instagram_app_key      = string
    instagram_app_secret   = string
    instagram_redirect_uri = string
  }))
}

variable "scheduled_tasks" {
  type = list(object({
    name       = string
    command    = string
    cron       = string
    task_count = number
  }))

  default = [
    {
      name       = "processalltasks"
      command    = "process_tasks --duration 3600"
      cron       = "cron(*/10 * * * ? *)"
      task_count = 1
    },
    {
      name       = "processsyncqueues"
      command    = "process_tasks --queue SALESFORCE_RESOURCE_SYNC --duration 3600"
      cron       = "cron(0 */11 * * ? *)"
      task_count = 1
    },
    {
      name       = "syncresourcedata"
      command    = "initresourcesync"
      cron       = "cron(0 */11 * * ? *)"
      task_count = 1
    },
    {
      name       = "syncresourcefields"
      command    = "initobjectfieldsync"
      cron       = "cron(0 */12 * * ? *)"
      task_count = 1
    },
    {
      name       = "clearsfstaledata"
      command    = "clearsfstaledata 1440"
      cron       = "cron(0 22 * * ? *)"
      task_count = 1
    },
    {
      name       = "batchspiders"
      command    = "batch_spiders"
      cron       = "cron(0 2 * * ? *)"
      task_count = 1
    },
    {
      name       = "runalerts"
      command    = "triggeralerts"
      cron       = "cron(0 8 ? * MON-FRI *)"
      task_count = 1
    },
    {
      name       = "spiderstatus"
      command    = "spider_status"
      cron       = "cron(*/30 2-8 * * ? *)"
      task_count = 1
    },
  ]
}

variable "db_snapshot_id" {
  type    = string
  default = ""
}
