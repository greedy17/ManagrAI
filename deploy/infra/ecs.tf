locals {
  http_app_urls      = { for e in var.environments : e.name => "http://${aws_alb.main.dns_name}:${e.lb_http_port}" }
  https_app_urls     = { for e in var.environments : e.name => "http://${aws_alb.main.dns_name}:${e.lb_https_port}" }
  nylas_callback_url = "http://${aws_alb.main.dns_name}:${tolist(var.environments)[0].lb_http_port}"
  ecr_repos          = toset(["thinknimble/managr/server", "thinknimble/managr/server-tasks"])
}

resource "aws_ecr_repository" "managr" {
  for_each             = local.ecr_repos
  name                 = each.value
  image_tag_mutability = "MUTABLE"

  tags = {
    "app" = "managr"
  }
}

resource "aws_ecs_cluster" "main" {
  name = "managr-cluster"
  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    "app" = "managr"
  }
}

data "template_file" "nginx_config" {
  for_each = { for e in var.environments : e.name => e }
  template = file("${path.module}/templates/nginx.conf.tpl")

  vars = {
    dns_name = aws_alb.main.dns_name
    app_url  = local.http_app_urls[each.key]
  }
}

data "template_file" "managr_app" {
  for_each = { for e in var.environments : e.name => e }
  template = file("${path.module}/templates/managr_app.json.tpl")

  vars = {
    nginx_config = base64encode(data.template_file.nginx_config[each.key].rendered)

    app_image                 = each.value["app_image"]
    app_image_scheduled_tasks = each.value["app_image_scheduled_tasks"]
    fargate_cpu               = var.fargate_cpu
    fargate_memory            = var.fargate_memory
    aws_region                = var.aws_region
    config_secret_arn         = aws_secretsmanager_secret.managr_config.arn
    current_domain            = aws_alb.main.dns_name
    current_port              = 8000
    debug                     = title(var.debug)

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
  for_each                 = { for e in var.environments : e.name => e }
  family                   = "managr-app-task-${lower(each.value["name"])}"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.fargate_cpu
  memory                   = var.fargate_memory
  container_definitions    = data.template_file.managr_app[each.key].rendered
  volume {
    name = "nginx-conf-vol"
  }

  tags = {
    "app" = "managr"
  }
}

resource "aws_ecs_service" "main" {
  for_each         = { for e in var.environments : e.name => e }
  name             = "managr-service-${lower(each.value["name"])}"
  cluster          = aws_ecs_cluster.main.id
  task_definition  = aws_ecs_task_definition.app[each.key].arn
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
    target_group_arn = aws_alb_target_group.app[each.key].id
    container_name   = "managr-app-proxy"
    container_port   = 80
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
    nylasOauthCallbackUrl = "${local.nylas_callback_url}/settings/integrations"

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
