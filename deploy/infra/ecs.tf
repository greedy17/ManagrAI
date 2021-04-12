resource "aws_ecs_cluster" "main" {
  name = "managr-cluster"

  tags = {
    "app" = "managr"
  }
}

data "template_file" "managr_app" {
  template = file("${path.module}/templates/managr_app.json.tpl")

  vars = {
    dd_api_key            = var.dd_api_key
    app_image             = var.app_image
    app_port              = var.app_port
    fargate_cpu           = var.fargate_cpu
    fargate_memory        = var.fargate_memory
    aws_region            = var.aws_region
    db_host_secret_arn    = aws_secretsmanager_secret.managrdb_host.arn
    db_user_secret_arn    = aws_secretsmanager_secret.managrdb_user.arn
    db_pass_secret_arn    = aws_secretsmanager_secret.managrdb_pass.arn
    db_name_secret_arn    = aws_secretsmanager_secret.managrdb_name.arn
    dd_api_key_secret_arn = aws_secretsmanager_secret.dd_api_key.arn
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
  name             = "managr-service"
  cluster          = aws_ecs_cluster.main.id
  task_definition  = aws_ecs_task_definition.app.arn
  desired_count    = var.app_count
  launch_type      = "FARGATE"
  platform_version = "1.4.0"

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

resource "aws_secretsmanager_secret" "dd_api_key" {
  name                    = "ddapikey"
  recovery_window_in_days = 0

  tags = {
    "app" = "managr"
  }
}

resource "aws_secretsmanager_secret_version" "dd_api_key" {
  secret_id     = aws_secretsmanager_secret.dd_api_key.id
  secret_string = var.dd_api_key
}
