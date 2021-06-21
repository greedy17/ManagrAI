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

resource "aws_cloudwatch_log_group" "managr_log_group_scheduled_task" {
  for_each          = { for st in local.scheduled_tasks : "${st.env.name}.${st.task.name}" => st }
  name              = "/ecs/managr-app/${lower(each.value.env.name)}/${lower(each.value.task.name)}"
  retention_in_days = 30

  tags = {
    "name" = "managr-log-group-${lower(each.value.env.name)}-${lower(each.value.task.name)}"
    "app"  = "managr"
  }
}

resource "aws_cloudwatch_log_stream" "managr_log_stream_scheduled_task" {
  for_each       = { for st in local.scheduled_tasks : "${st.env.name}.${st.task.name}" => st }
  name           = "managr-log-stream-${lower(each.value.env.name)}-${lower(each.value.task.name)}"
  log_group_name = aws_cloudwatch_log_group.managr_log_group_scheduled_task[each.key].name
}

