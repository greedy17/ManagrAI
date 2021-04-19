output "managr_app_url" {
  value = "http://${aws_alb.main.dns_name}:${var.app_port}"
}

output "managr_app_https_url" {
  value = "https://${aws_alb.main.dns_name}:${var.app_port_https}"
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  value = aws_ecs_service.main.name
}

output "managr_server_ecr_repo_url" {
  value = aws_ecr_repository.managr["thinknimble/managr/server"].repository_url
}

output "managr_server_scheduled_tasks_ecr_repo_url" {
  value = aws_ecr_repository.managr["thinknimble/managr/server-tasks"].repository_url
}
