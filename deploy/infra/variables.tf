variable "managr_domain" {
  type    = string
  default = "mymanagrapp.com"
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
  default = 1
}

variable "health_check_path" {
  type    = string
  default = "/"
}

variable "fargate_cpu" {
  type    = string
  default = "1024"
}

variable "fargate_memory" {
  type    = string
  default = "2048"
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
  default = ["thinknimble/managr/server", "thinknimble/managr/server-tasks", "thinknimble/managr/nginx"]
}

variable "environments" {
  type = set(object({
    name                      = string
    app_image                 = string
    app_image_scheduled_tasks = string

    s3_bucket_location = string

    allowed_hosts  = string
    current_domain = string

    debug              = bool
    environment        = string
    rds_username       = string
    rds_password       = string
    rds_db_name        = string
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

    use_salesforce          = bool
    salesforce_base_url     = string
    salesforce_consumer_key = string
    salesforce_secret       = string
    salesforce_scopes       = set(string)
    salesforce_redirect_uri = string
    salesforce_api_version  = string
  }))
}
