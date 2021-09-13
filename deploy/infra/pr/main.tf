locals {
  env            = "pr-${var.pr_number}"
  pr_url         = "${local.env}.${var.managr_domain}"
  listener_ports = toset(["80", "443"])
  pr_urls = {
    http  = "http://${local.pr_url}"
    https = "https://${local.pr_url}"
  }
}

data "aws_region" "current" {}

data "aws_alb" "main" {
  name = "managr-load-balancer"
}

data "aws_vpc" "main" {
  id = var.vpc_id
}

data "aws_ecs_cluster" "main" {
  cluster_name = "managr-cluster"
}

data "aws_alb_listener" "front_end" {
  for_each          = local.listener_ports
  load_balancer_arn = data.aws_alb.main.arn
  port              = tonumber(each.value)
}

resource "aws_lb_listener_rule" "rule" {
  for_each     = local.listener_ports
  listener_arn = data.aws_alb_listener.front_end[each.key].arn
  priority     = 100 + index(tolist(local.listener_ports), each.value)

  action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.app.id
  }

  condition {
    host_header {
      values = [local.pr_url]
    }
  }
}

resource "random_string" "alb_prefix" {
  length  = 4
  upper   = false
  special = false
}

resource "aws_alb_target_group" "app" {
  name        = "managr-target-group-${local.env}-${random_string.alb_prefix.result}"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.main.id
  target_type = "ip"

  health_check {
    healthy_threshold   = "3"
    interval            = "30"
    protocol            = "HTTP"
    matcher             = "200"
    timeout             = "3"
    path                = var.health_check_path
    unhealthy_threshold = "2"
  }

  deregistration_delay = 0

  tags = {
    "app" = "managr"
  }

  lifecycle {
    create_before_destroy = true
  }
}


data "template_file" "nginx_config" {
  template = file("${path.module}/../templates/nginx.conf.tpl")

  vars = {
    dns_name = data.aws_alb.main.dns_name
    app_url  = local.pr_urls.http
  }
}

data "template_file" "managr_app" {
  template = file("${path.module}/../templates/managr_app.json.tpl")

  vars = {
    nginx_config = base64encode(data.template_file.nginx_config.rendered)

    environment               = local.env
    app_image                 = var.app_config.app_image
    nginx_image               = var.app_config.nginx_image
    app_image_scheduled_tasks = var.app_config.app_image_scheduled_tasks
    aws_logs_group            = aws_cloudwatch_log_group.managr_log_group.name
    fargate_cpu               = var.fargate_cpu
    fargate_memory            = var.fargate_memory
    aws_region                = data.aws_region.current.name
    config_secret_arn         = aws_secretsmanager_secret.managr_config.arn

    allowed_hosts  = var.app_config.allowed_hosts != "" ? var.app_config.allowed_hosts : "*"
    current_domain = var.app_config.current_domain != "" ? var.app_config.current_domain : data.aws_alb.main.dns_name
    current_port   = 8000
    debug          = title(var.app_config.debug)

    use_rollbar = title(var.app_config.use_rollbar)

    use_custom_smtp            = title(var.app_config.use_custom_smtp)
    smtp_use_tls               = title(var.app_config.smtp_use_tls)
    smtp_port                  = var.app_config.smtp_port
    smtp_valid_testing_domains = var.app_config.smtp_valid_testing_domains

    aws_location = var.app_config.s3_bucket_location

    use_nylas      = title(var.app_config.use_nylas)
    use_twilio     = title(var.app_config.use_twilio)
    use_zoom       = title(var.app_config.use_zoom)
    use_slack      = title(var.app_config.use_slack)
    use_salesforce = title(var.app_config.use_salesforce)
    use_salesloft  = title(var.app_config.use_salesloft)
  }
}

data "aws_iam_role" "ecs_task_execution_role" {
  name = var.ecs_task_execution_role_name
}

resource "aws_ecs_task_definition" "app" {
  family                   = "managr-app-task-${local.env}"
  execution_role_arn       = data.aws_iam_role.ecs_task_execution_role.arn
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.fargate_cpu
  memory                   = var.fargate_memory
  container_definitions    = data.template_file.managr_app.rendered
  volume {
    name = "nginx-conf-vol"
  }

  tags = {
    "app" = "managr"
  }
}

data "aws_security_group" "ecs_tasks" {
  name = "managr-ecs-tasks-security-group"
}

data "aws_subnet_ids" "private" {
  vpc_id = var.vpc_id

  tags = {
    "subnet" = "private"
  }
}

resource "aws_ecs_service" "main" {
  name             = "managr-service-${local.env}"
  cluster          = data.aws_ecs_cluster.main.id
  task_definition  = aws_ecs_task_definition.app.arn
  desired_count    = var.app_count
  launch_type      = "FARGATE"
  platform_version = "1.4.0"
  propagate_tags   = "SERVICE"

  # temporary
  force_new_deployment = true

  network_configuration {
    security_groups  = [data.aws_security_group.ecs_tasks.id]
    subnets          = data.aws_subnet_ids.private.ids
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_alb_target_group.app.id
    container_name   = "managr-app-proxy"
    container_port   = 80
  }

  depends_on = [aws_db_instance.managrdb]

  tags = {
    "app" = "managr"
  }
}


data "aws_db_subnet_group" "managrdb" {
  name = "managrdb"
}

data "aws_security_group" "managr_db" {
  name = "managrdb-security-group"
}

resource "aws_db_instance" "managrdb" {
  identifier                 = "${var.app_config.rds_db_name}-${local.env}"
  allocated_storage          = 20
  engine                     = "postgres"
  engine_version             = "12.5"
  instance_class             = "db.t2.micro"
  name                       = var.app_config.rds_db_name
  username                   = var.app_config.rds_username
  password                   = var.app_config.rds_password
  storage_type               = "gp2"
  skip_final_snapshot        = true
  port                       = 5432
  db_subnet_group_name       = data.aws_db_subnet_group.managrdb.id
  vpc_security_group_ids     = [data.aws_security_group.managr_db.id]
  publicly_accessible        = false
  auto_minor_version_upgrade = true

  tags = {
    "app" = "managr"
  }
}


resource "aws_secretsmanager_secret" "managr_config" {
  name                    = "ManagerConfig-${local.env}"
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
    dbUser = var.app_config.rds_username
    dbPass = var.app_config.rds_password
    dbName = var.app_config.rds_db_name

    secretKey = var.app_config.secret_key

    staffEmail = var.app_config.staff_email

    rollbarAccessToken = var.app_config.rollbar_access_token

    smtpUser     = var.app_config.smtp_user
    smtpPassword = var.app_config.smtp_password
    smtpHost     = var.app_config.smtp_host

    awsAccessKeyId       = var.s3_bucket_aws_access_key_id
    awsSecretAccessKey   = var.s3_bucket_aws_secret_access_key
    awsStorageBucketName = var.s3_bucket_name

    nylasClientId         = var.app_config.nylas_client_id
    nylasClientSecret     = var.app_config.nylas_client_secret
    nylasOauthCallbackUrl = var.app_config.nylas_oauth_callback_url

    twilioAccountSid      = var.app_config.twilio_account_sid
    twilioAuthToken       = var.app_config.twilio_auth_token
    twilioBaseCallbackUrl = var.app_config.twilio_base_callback_url

    zoomRedirectUri     = var.app_config.zoom_redirect_uri
    zoomClientId        = var.app_config.zoom_client_id
    zoomSecret          = var.app_config.zoom_secret
    zoomWebhookToken    = var.app_config.zoom_webhook_token
    zoomFakeMeetingUuid = var.app_config.zoom_fake_meeting_uuid

    slackClientId      = var.app_config.slack_client_id
    slackSecret        = var.app_config.slack_secret
    slackSigningSecret = var.app_config.slack_signing_secret
    slackAppVersion    = var.app_config.slack_app_version

    salesforceBaseUrl     = var.app_config.salesforce_base_url
    salesforceConsumerKey = var.app_config.salesforce_consumer_key
    salesforceSecret      = var.app_config.salesforce_secret
    salesforceScopes      = join(" ", var.app_config.salesforce_scopes)
    salesforceRedirectUri = var.app_config.salesforce_redirect_uri
    salesforceApiVersion  = var.app_config.salesforce_api_version

    salesloftBaseUrl      = var.app_config.salesloft_base_url
    salesloftClientId     = var.app_config.salesloft_client_id
    salesloftSecret       = var.app_config.salesloft_secret
    salesloftRedirectUri  = var.app_config.salesloft_redirect_uri
  })
}

resource "aws_cloudwatch_log_group" "managr_log_group" {
  name              = "/ecs/managr-app/${local.env}"
  retention_in_days = 30

  tags = {
    "name" = "managr-log-group-${local.env}"
    "app"  = "managr"
  }
}

resource "aws_cloudwatch_log_stream" "managr_log_stream" {
  name           = "managr-log-stream-${local.env}"
  log_group_name = aws_cloudwatch_log_group.managr_log_group.name
}
