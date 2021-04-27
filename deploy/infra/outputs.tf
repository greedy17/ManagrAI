output "managr_http_app_urls" {
  value = local.http_app_urls
}

output "managr_https_app_urls" {
  value = local.https_app_urls
}



output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "ecs_service_names" {
  value = [for s in aws_ecs_service.main : s.name]
}

output "managr_server_ecr_repo_url" {
  value = aws_ecr_repository.managr["thinknimble/managr/server"].repository_url
}

output "managr_server_scheduled_tasks_ecr_repo_url" {
  value = aws_ecr_repository.managr["thinknimble/managr/server-tasks"].repository_url
}

output "ecs_task_families" {
  value = [for e in var.environments : "managr-app-task-${lower(e.name)}"]
}
