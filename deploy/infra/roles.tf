# ECS task execution role data
data "aws_iam_policy_document" "ecs_task_execution_role" {
  version = "2012-10-17"
  statement {
    sid     = ""
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

# CloudWatch Events Role
data "aws_iam_policy_document" "cloud_watch_events_role" {
  version = "2012-10-17"
  statement {
    sid     = ""
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_task_role_ecs_exec" {
  name               = var.ecs_task_role_name
  assume_role_policy = data.aws_iam_policy_document.ecs_task_execution_role.json

  inline_policy {
    name = "ecs_exec"

    policy = jsonencode({

      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : [
            "ssmmessages:CreateControlChannel",
            "ssmmessages:CreateDataChannel",
            "ssmmessages:OpenControlChannel",
            "ssmmessages:OpenDataChannel"
          ],
          "Resource" : "*"
        }
      ]
    })
  }
}

resource "aws_iam_role" "ecs_scheduled_tasks_cloud_watch" {
  name               = "ScheduledTasksCloudWatchRole"
  assume_role_policy = data.aws_iam_policy_document.cloud_watch_events_role.json

  inline_policy {
    name = "ecs_exec"

    policy = jsonencode({

      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : [
            "ecs:RunTask",
            "iam:ListInstanceProfiles",
            "iam:ListRoles",
            "iam:PassRole"
          ],
          "Resource" : "*"
        }
      ]
    })
  }
}

# ECS task execution role
resource "aws_iam_role" "ecs_task_execution_role" {
  name               = var.ecs_task_execution_role_name
  assume_role_policy = data.aws_iam_policy_document.ecs_task_execution_role.json

  inline_policy {
    name = "env_secrets"

    policy = jsonencode({
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Effect" : "Allow",
          "Action" : [
            "secretsmanager:GetSecretValue"
          ],
          "Resource" : [
            "*"
          ]
        }
      ]
    })
  }

  tags = {
    "app" = "managr"
  }
}

# ECS task execution role policy attachment
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}


resource "aws_iam_role" "batch_job_definition_role" {
  name = "batch_job_definition_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "batch.amazonaws.com"
        },
        Action: "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "batch_job_definition_policy" {
  name   = "batch_job_definition_policy"
  role   = aws_iam_role.batch_job_definition_role.id
  policy = jsonencode({
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "batch:CreateJobDefinition",
        "batch:RegisterJobDefinition",
        "batch:DescribeJobDefinitions"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "iam:PassRole"
      ],
      "Resource": "*"
    }
  ]
  })
}
