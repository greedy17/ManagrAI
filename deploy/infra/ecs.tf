locals {
  app_url = "http://${aws_alb.main.dns_name}:${var.app_port}"
}

resource "aws_ecs_cluster" "main" {
  name = "managr-cluster"

  tags = {
    "app" = "managr"
  }
}

data "template_file" "managr_app" {
  template = file("${path.module}/templates/managr_app.json.tpl")

  vars = {
    app_image         = var.app_image
    app_port          = var.app_port
    fargate_cpu       = var.fargate_cpu
    fargate_memory    = var.fargate_memory
    aws_region        = var.aws_region
    config_secret_arn = aws_secretsmanager_secret.managr_config.arn
    current_domain    = aws_alb.main.dns_name
    current_port      = var.app_port
    debug             = title(var.debug)

    use_rollbar = title(var.use_rollbar)

    use_custom_smtp            = title(var.use_custom_smtp)
    smtp_use_tls               = title(var.smtp_use_tls)
    smtp_port                  = var.smtp_port
    smtp_valid_testing_domains = var.smtp_valid_testing_domains

    use_aws_storage      = title(var.use_aws_storage)
    aws_location         = var.aws_location
    aws_location_dev     = var.aws_location_dev
    aws_location_staging = var.aws_location_staging
    aws_location_prod    = var.aws_location_prod

    use_nylas      = title(var.use_nylas)
    use_twilio     = title(var.use_twilio)
    use_zoom       = title(var.use_zoom)
    use_slack      = title(var.use_slack)
    test_slack     = title(var.test_slack)
    use_salesforce = title(var.use_salesforce)
  }
}

resource "aws_ecs_task_definition" "app" {
  family                   = "managr-app-task"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.fargate_cpu
  memory                   = var.fargate_memory
  container_definitions    = data.template_file.managr_app.rendered

  tags = {
    "app" = "managr"
  }
}

resource "aws_ecs_service" "main" {
  name             = "managr-service-tf-testing"
  cluster          = aws_ecs_cluster.main.id
  task_definition  = aws_ecs_task_definition.app.arn
  desired_count    = var.app_count
  launch_type      = "FARGATE"
  platform_version = "1.4.0"
  propagate_tags   = "SERVICE"

  # temporary
  force_new_deployment = true

  network_configuration {
    security_groups  = [aws_security_group.ecs_tasks.id]
    subnets          = aws_subnet.private.*.id
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_alb_target_group.app.id
    container_name   = "managr-app"
    container_port   = var.app_port
  }

  depends_on = [aws_alb_listener.front_end, aws_iam_role_policy_attachment.ecs_task_execution_role, aws_db_instance.managrdb, aws_vpc_endpoint.vpc_endpoint]

  tags = {
    "app" = "managr"
  }
}

resource "aws_secretsmanager_secret" "managr_config" {
  name                    = "ManagerConfig"
  recovery_window_in_days = 0

  tags = {
    "app" = "managr"
  }
}

resource "aws_secretsmanager_secret_version" "managr_config" {
  secret_id = aws_secretsmanager_secret.managr_config.id
  secret_string = jsonencode({
    ddApiKey = var.dd_api_key

    dbHost = aws_db_instance.managrdb.address
    dbUser = var.rds_username
    dbPass = var.rds_password
    dbName = var.rds_db_name

    secretKey = var.secret_key

    staffEmail = var.staff_email

    rollbarAccessToken = var.rollbar_access_token

    smtpUser     = var.smtp_user
    smtpPassword = var.smtp_password
    smtpHost     = var.smtp_host

    awsAccessKeyId       = var.aws_access_key_id
    awsSecretAccessKey   = var.aws_secret_access_key
    awsStorageBucketName = var.aws_storage_bucket_name

    nylasClientId         = var.nylas_client_id
    nylasClientSecret     = var.nylas_client_secret
    nylasOauthCallbackUrl = "${local.app_url}/settings/integrations"

    twilioAccountSid      = var.twilio_account_sid
    twilioAuthToken       = var.twilio_auth_token
    twilioBaseCallbackUrl = var.twilio_base_callback_url

    zoomRedirectUri     = var.zoom_redirect_uri
    zoomClientId        = var.zoom_client_id
    zoomSecret          = var.zoom_secret
    zoomWebhookToken    = var.zoom_webhook_token
    zoomFakeMeetingUuid = var.zoom_fake_meeting_uuid

    slackClientId      = var.slack_client_id
    slackSecret        = var.slack_secret
    slackSigningSecret = var.slack_signing_secret
    slackAppVersion    = var.slack_app_version

    slackTestTeamName                        = var.slack_test_team_name
    slackTestTeamId                          = var.slack_test_team_id
    slackTestBotUserId                       = var.slack_test_bot_user_id
    slackTestAccessToken                     = var.slack_test_access_token
    slackTestIncomingWebhookUrl              = var.slack_test_incoming_webhook_url
    slackTestIncomingWebhookChannel          = var.slack_test_incoming_webhook_channel
    slackTestIncomingWebhookChannelId        = var.slack_test_incoming_webhook_channel_id
    slackTestIncomingWebhookConfigurationUrl = var.slack_test_incoming_webhook_configuration_url

    salesforceBaseUrl     = var.salesforce_base_url
    salesforceConsumerKey = var.salesforce_consumer_key
    salesforceSecret      = var.salesforce_secret
    salesforceScopes      = join(" ", var.salesforce_scopes)
    salesforceRedirectUri = var.salesforce_redirect_uri
    salesforceApiVersion  = var.salesforce_api_version
  })
}
