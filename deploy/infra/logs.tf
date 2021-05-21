resource "aws_cloudwatch_log_group" "managr_log_group" {
  for_each          = { for e in var.environments : e.name => e }
  name              = "/ecs/managr-app/${each.key}"
  retention_in_days = 30

  tags = {
    "name" = "managr-log-group-${each.key}"
    "app"  = "managr"
  }
}

resource "aws_cloudwatch_log_stream" "managr_log_stream" {
  for_each       = { for e in var.environments : e.name => e }
  name           = "managr-log-stream-${each.key}"
  log_group_name = aws_cloudwatch_log_group.managr_log_group[each.key].name
}

