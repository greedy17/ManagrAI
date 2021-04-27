variable "aws_region" {
  default = "us-east-1"
}

variable "ecs_task_execution_role_name" {
  default = "ManagrEcsTaskExecutionRole"
}

variable "az_count" {
  default = "2"
}

variable "app_count" {
  default = 1
}

variable "health_check_path" {
  default = "/"
}

variable "fargate_cpu" {
  default = "1024"
}

variable "fargate_memory" {
  default = "2048"
}

variable "dd_api_key" {
  type      = string
  sensitive = true
}

variable "rds_username" {
  type      = string
  sensitive = true
}

variable "rds_password" {
  type      = string
  sensitive = true
}

variable "rds_db_name" {
  type = string
}

variable "local_ip" {
  type = string
}

variable "secret_key" {
  type      = string
  sensitive = true
}

variable "staff_email" {
  type      = string
  sensitive = true
}

variable "debug" {
  type = bool
}

variable "use_rollbar" {
  type = bool
}

variable "use_custom_smtp" {
  type = bool
}

variable "smtp_use_tls" {
  type = bool
}

variable "rollbar_access_token" {
  type      = string
  default   = ""
  sensitive = true
}

variable "smtp_user" {
  type      = string
  sensitive = true
}

variable "smtp_password" {
  type      = string
  sensitive = true
}

variable "smtp_host" {
  type      = string
  sensitive = true
}

variable "smtp_port" {
  type    = string
  default = "587"
}

variable "smtp_valid_testing_domains" {
  type = string
}

variable "use_aws_storage" {
  type = bool
}

variable "aws_storage_bucket_name" {
  type      = string
  sensitive = true
}

variable "aws_location" {
  type = string
}

variable "aws_location_dev" {
  type = string
}

variable "aws_location_staging" {
  type = string
}

variable "aws_location_prod" {
  type = string
}

variable "use_nylas" {
  type = bool
}

variable "nylas_client_id" {
  type      = string
  sensitive = true
}

variable "nylas_client_secret" {
  type      = string
  sensitive = true
}

variable "use_twilio" {
  type = bool
}

variable "twilio_account_sid" {
  type      = string
  sensitive = true
}

variable "twilio_auth_token" {
  type      = string
  sensitive = true
}

variable "twilio_base_callback_url" {
  type      = string
  sensitive = true
}

variable "use_zoom" {
  type = bool
}

variable "zoom_redirect_uri" {
  type      = string
  sensitive = true
}

variable "zoom_client_id" {
  type      = string
  sensitive = true
}

variable "zoom_secret" {
  type      = string
  sensitive = true
}

variable "zoom_webhook_token" {
  type      = string
  sensitive = true
}

variable "zoom_fake_meeting_uuid" {
  type      = string
  sensitive = true
}

variable "use_slack" {
  type = bool
}

variable "slack_client_id" {
  type      = string
  sensitive = true
}

variable "slack_secret" {
  type      = string
  sensitive = true
}

variable "slack_signing_secret" {
  type      = string
  sensitive = true
}

variable "slack_app_version" {
  type      = string
  sensitive = true
}

variable "use_salesforce" {
  type      = bool
  sensitive = true
}

variable "salesforce_base_url" {
  type      = string
  sensitive = true
}

variable "salesforce_consumer_key" {
  type      = string
  sensitive = true
}

variable "salesforce_secret" {
  type      = string
  sensitive = true
}

variable "salesforce_scopes" {
  type      = list(string)
  sensitive = true
}

variable "salesforce_redirect_uri" {
  type      = string
  sensitive = true
}

variable "salesforce_api_version" {
  type      = string
  sensitive = true
}

variable "aws_access_key_id" {
  type      = string
  sensitive = true
}

variable "aws_secret_access_key" {
  type      = string
  sensitive = true
}

variable "environments" {
  type = set(object({
    name                      = string
    app_image                 = string
    app_image_scheduled_tasks = string
    lb_http_port              = number
    lb_https_port             = number
  }))
}
