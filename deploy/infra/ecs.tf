locals {
  app_urls = { for e in var.environments : e.name => {
    http  = "http://${lower(e.name)}.${var.managr_domain}"
    https = "https://${lower(e.name)}.${var.managr_domain}"
    }
  }
}

resource "aws_ecr_repository" "managr" {
  for_each             = var.ecr_repo_names
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
    app_url  = local.app_urls[each.key].http
  }
}

data "template_file" "managr_app" {
  for_each = { for e in var.environments : e.name => e }
  template = file("${path.module}/templates/managr_app.json.tpl")

  vars = {
    nginx_config   = base64encode(data.template_file.nginx_config[each.key].rendered)
    aws_logs_group = aws_cloudwatch_log_group.managr_log_group[each.key].name

    environment               = each.value.environment
    app_image                 = each.value.app_image != "" ? each.value.app_image : "${aws_ecr_repository.managr["thinknimble/managr/server"].repository_url}:latest"
    app_image_scheduled_tasks = each.value.app_image_scheduled_tasks != "" ? each.value.app_image_scheduled_tasks : "${aws_ecr_repository.managr["thinknimble/managr/server-tasks"].repository_url}:latest"
    nginx_image               = "${aws_ecr_repository.managr["thinknimble/managr/nginx"].repository_url}:latest"
    bash_image                = "${aws_ecr_repository.managr["thinknimble/managr/bash"].repository_url}:latest"
    datadog_image             = "${aws_ecr_repository.managr["thinknimble/managr/datadog/agent"].repository_url}:latest"

    fargate_cpu       = var.fargate_cpu
    fargate_memory    = var.fargate_memory
    aws_region        = data.aws_region.current.name
    config_secret_arn = aws_secretsmanager_secret.managr_config[each.key].arn

    allowed_hosts  = each.value.allowed_hosts != "" ? each.value.allowed_hosts : "*"
    current_domain = each.value.current_domain != "" ? each.value.current_domain : aws_alb.main.dns_name
    current_port   = 8000
    debug          = title(each.value.debug)

    use_rollbar = title(each.value.use_rollbar)

    use_custom_smtp            = title(each.value.use_custom_smtp)
    smtp_use_tls               = title(each.value.smtp_use_tls)
    smtp_port                  = each.value.smtp_port
    smtp_valid_testing_domains = each.value.smtp_valid_testing_domains

    aws_location = each.value.s3_bucket_location

    use_nylas      = title(each.value.use_nylas)
    use_twilio     = title(each.value.use_twilio)
    use_zoom       = title(each.value.use_zoom)
    use_slack      = title(each.value.use_slack)
    use_salesforce = title(each.value.use_salesforce)
  }
}

data "template_file" "managr_app_scheduled_tasks" {
  for_each = { for e in var.environments : e.name => e }
  template = file("${path.module}/templates/managr_app_tasks.json.tpl")

  vars = {
    nginx_config   = base64encode(data.template_file.nginx_config[each.key].rendered)
    aws_logs_group = aws_cloudwatch_log_group.managr_log_group[each.key].name

    environment               = each.value.environment
    app_image                 = each.value.app_image != "" ? each.value.app_image : "${aws_ecr_repository.managr["thinknimble/managr/server"].repository_url}:latest"
    app_image_scheduled_tasks = each.value.app_image_scheduled_tasks != "" ? each.value.app_image_scheduled_tasks : "${aws_ecr_repository.managr["thinknimble/managr/server-tasks"].repository_url}:latest"
    nginx_image               = "${aws_ecr_repository.managr["thinknimble/managr/nginx"].repository_url}:latest"
    bash_image                = "${aws_ecr_repository.managr["thinknimble/managr/bash"].repository_url}:latest"
    datadog_image             = "${aws_ecr_repository.managr["thinknimble/managr/datadog/agent"].repository_url}:latest"

    fargate_cpu       = var.fargate_cpu
    fargate_memory    = var.fargate_memory
    aws_region        = data.aws_region.current.name
    config_secret_arn = aws_secretsmanager_secret.managr_config[each.key].arn

    allowed_hosts  = each.value.allowed_hosts != "" ? each.value.allowed_hosts : "*"
    current_domain = each.value.current_domain != "" ? each.value.current_domain : aws_alb.main.dns_name
    current_port   = 8000
    debug          = title(each.value.debug)

    use_rollbar = title(each.value.use_rollbar)

    use_custom_smtp            = title(each.value.use_custom_smtp)
    smtp_use_tls               = title(each.value.smtp_use_tls)
    smtp_port                  = each.value.smtp_port
    smtp_valid_testing_domains = each.value.smtp_valid_testing_domains

    aws_location = each.value.s3_bucket_location

    use_nylas      = title(each.value.use_nylas)
    use_twilio     = title(each.value.use_twilio)
    use_zoom       = title(each.value.use_zoom)
    use_slack      = title(each.value.use_slack)
    use_salesforce = title(each.value.use_salesforce)
  }
}

resource "aws_ecs_task_definition" "app" {
  for_each                 = { for e in var.environments : e.name => e }
  family                   = "managr-app-task-${lower(each.value.name)}"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.fargate_cpu
  memory                   = var.fargate_memory
  container_definitions    = data.template_file.managr_app[each.key].rendered
  task_role_arn            = aws_iam_role.ecs_task_role_ecs_exec.arn
  volume {
    name = "nginx-conf-vol"
  }

  tags = {
    "app" = "managr"
  }
}

resource "aws_ecs_task_definition" "app_scheduled_tasks" {
  for_each                 = { for e in var.environments : e.name => e }
  family                   = "managr-app-scheduled-tasks-${lower(each.value.name)}"
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.fargate_cpu
  memory                   = var.fargate_memory
  container_definitions    = data.template_file.managr_app_scheduled_tasks[each.key].rendered
  task_role_arn            = aws_iam_role.ecs_task_role_ecs_exec.arn
  volume {
    name = "nginx-conf-vol"
  }

  tags = {
    "app" = "managr"
  }
}

resource "aws_ecs_service" "main" {
  for_each               = { for e in var.environments : e.name => e }
  name                   = "managr-service-${lower(each.value.name)}"
  cluster                = aws_ecs_cluster.main.id
  task_definition        = aws_ecs_task_definition.app[each.key].arn
  desired_count          = var.app_count
  launch_type            = "FARGATE"
  platform_version       = "1.4.0"
  propagate_tags         = "SERVICE"
  enable_execute_command = true

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

resource "aws_ecs_service" "main_scheduled_tasks" {
  for_each               = { for e in var.environments : e.name => e }
  name                   = "managr-service-scheduled-tasks-${lower(each.value.name)}"
  cluster                = aws_ecs_cluster.main.id
  task_definition        = aws_ecs_task_definition.app_scheduled_tasks[each.key].arn
  desired_count          = 1
  launch_type            = "FARGATE"
  platform_version       = "1.4.0"
  propagate_tags         = "SERVICE"
  enable_execute_command = true

  # temporary
  force_new_deployment = true

  network_configuration {
    security_groups  = [aws_security_group.ecs_tasks.id]
    subnets          = aws_subnet.private.*.id
    assign_public_ip = true
  }

  depends_on = [aws_alb_listener.front_end, aws_iam_role_policy_attachment.ecs_task_execution_role, aws_db_instance.managrdb, aws_vpc_endpoint.vpc_endpoint, aws_ecs_service.main]

  tags = {
    "app" = "managr"
  }
}

resource "aws_secretsmanager_secret" "managr_config" {
  for_each                = { for e in var.environments : e.name => e }
  name                    = "ManagerConfig-${each.value.name}"
  recovery_window_in_days = 0

  tags = {
    "app" = "managr"
  }
}

resource "aws_secretsmanager_secret_version" "managr_config" {
  for_each  = { for e in var.environments : e.name => e }
  secret_id = aws_secretsmanager_secret.managr_config[each.key].id
  secret_string = jsonencode({
    ddApiKey = var.dd_api_key

    dbHost = aws_db_instance.managrdb[each.key].address
    dbUser = each.value.rds_username
    dbPass = each.value.rds_password
    dbName = each.value.rds_db_name

    superuserEmail    = each.value.superuser_email
    superuserPassword = each.value.superuser_password

    secretKey = each.value.secret_key

    staffEmail = each.value.staff_email

    rollbarAccessToken = each.value.rollbar_access_token

    smtpUser     = each.value.smtp_user
    smtpPassword = each.value.smtp_password
    smtpHost     = each.value.smtp_host

    awsAccessKeyId       = var.s3_bucket_aws_access_key_id
    awsSecretAccessKey   = var.s3_bucket_aws_secret_access_key
    awsStorageBucketName = var.s3_bucket_name

    nylasClientId         = each.value.nylas_client_id
    nylasClientSecret     = each.value.nylas_client_secret
    nylasOauthCallbackUrl = each.value.nylas_oauth_callback_url

    twilioAccountSid      = each.value.twilio_account_sid
    twilioAuthToken       = each.value.twilio_auth_token
    twilioBaseCallbackUrl = each.value.twilio_base_callback_url

    zoomRedirectUri     = each.value.zoom_redirect_uri
    zoomClientId        = each.value.zoom_client_id
    zoomSecret          = each.value.zoom_secret
    zoomWebhookToken    = each.value.zoom_webhook_token
    zoomFakeMeetingUuid = each.value.zoom_fake_meeting_uuid

    slackClientId      = each.value.slack_client_id
    slackSecret        = each.value.slack_secret
    slackSigningSecret = each.value.slack_signing_secret
    slackAppVersion    = each.value.slack_app_version

    salesforceBaseUrl     = each.value.salesforce_base_url
    salesforceConsumerKey = each.value.salesforce_consumer_key
    salesforceSecret      = each.value.salesforce_secret
    salesforceScopes      = join(" ", each.value.salesforce_scopes)
    salesforceRedirectUri = each.value.salesforce_redirect_uri
    salesforceApiVersion  = each.value.salesforce_api_version
  })
}
