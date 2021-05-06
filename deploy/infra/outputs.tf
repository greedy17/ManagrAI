output "managr_app_urls" {
  value = local.app_urls
}

output "managr_load_balancer_dns_name" {
  value = aws_alb.main.dns_name
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "ecs_service_names" {
  value = [for s in aws_ecs_service.main : s.name]
}

output "ecr_config" {
  value = {
    server = {
      image_name   = "thinknimble/managr/server"
      registry_url = split("/", aws_ecr_repository.managr["thinknimble/managr/server"].repository_url)[0]
      ecr_repo_url = aws_ecr_repository.managr["thinknimble/managr/server"].repository_url
    }
    scheduled_tasks = {
      image_name   = "thinknimble/managr/server-tasks"
      registry_url = split("/", aws_ecr_repository.managr["thinknimble/managr/server-tasks"].repository_url)[0]
      ecr_repo_url = aws_ecr_repository.managr["thinknimble/managr/server-tasks"].repository_url
    }
  }
}

output "ecs_task_families" {
  value = [for e in var.environments : "managr-app-task-${lower(e.name)}"]
}
