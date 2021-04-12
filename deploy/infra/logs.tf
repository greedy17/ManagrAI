resource "aws_cloudwatch_log_group" "managr_log_group" {
  name              = "/ecs/managr-app"
  retention_in_days = 30

  tags = {
    "name" = "managr-log-group"
    "app"  = "managr"
  }
}

resource "aws_cloudwatch_log_stream" "managr_log_stream" {
  name           = "managr-log-stream"
  log_group_name = aws_cloudwatch_log_group.managr_log_group.name
}

