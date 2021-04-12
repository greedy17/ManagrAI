variable "aws_region" {
  default = "us-east-2"
}

variable "ecs_task_execution_role_name" {
  default = "ManagrEcsTaskExecutionRole"
}

variable "az_count" {
  default = "2"
}

variable "app_image" {
  type = string
}

variable "app_port" {
  default = 8000
}

variable "app_count" {
  default = 3
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
