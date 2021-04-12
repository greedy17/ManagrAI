[
  {
    "name": "managr-app",
    "image": "${app_image}",
    "cpu": ${fargate_cpu},
    "memory": ${fargate_memory},
    "networkMode": "awsvpc",
    "environment": [
      { "name": "ALLOWED_HOSTS", "value": "*" },
      { "name": "DD_SERVICE", "value": "managr-server" },
      { "name": "DD_ENV", "value": "fargate" },
      { "name": "DD_PROFILING_ENABLED", "value": "true" }
    ],
    "secrets": [
      {
        "name": "DB_HOST",
        "valueFrom": "${db_host_secret_arn}"
      },
      {
        "name": "DB_USER",
        "valueFrom": "${db_user_secret_arn}"
      },
      {
        "name": "DB_PASS",
        "valueFrom": "${db_pass_secret_arn}"
      },
      {
        "name": "DB_NAME",
        "valueFrom": "${db_name_secret_arn}"
      }
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/managr-app",
        "awslogs-region": "${aws_region}",
        "awslogs-stream-prefix": "ecs"
      }
    },
    "portMappings": [
      {
        "containerPort": ${app_port},
        "hostPort": ${app_port}
      }
    ]
  },
  {
    "name": "managr-app-worker",
    "dependsOn": [
      {
        "containerName": "managr-app",
        "condition": "START"
      }
    ],
    "image": "${app_image}",
    "entryPoint": ["ddtrace-run", "python3", "server/manage.py", "process_tasks"],
    "networkMode": "awsvpc",
    "environment": [
      { "name": "ALLOWED_HOSTS", "value": "*" },
      { "name": "DD_SERVICE", "value": "managr-server-worker" },
      { "name": "DD_ENV", "value": "fargate" },
      { "name": "DD_PROFILING_ENABLED", "value": "true" }
    ],
    "secrets": [
      {
        "name": "DB_HOST",
        "valueFrom": "${db_host_secret_arn}"
      },
      {
        "name": "DB_USER",
        "valueFrom": "${db_user_secret_arn}"
      },
      {
        "name": "DB_PASS",
        "valueFrom": "${db_pass_secret_arn}"
      },
      {
        "name": "DB_NAME",
        "valueFrom": "${db_name_secret_arn}"
      }
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/managr-app",
        "awslogs-region": "${aws_region}",
        "awslogs-stream-prefix": "ecs"
      }
    }
  },
  {
    "name": "datadog-agent",
    "image": "datadog/agent:latest",
    "secrets": [
      {
        "name": "DD_API_KEY",
        "valueFrom": "${dd_api_key_secret_arn}"
      }
    ],
    "environment": [
      {
        "name": "ECS_FARGATE",
        "value": "true"
      },
      {
        "name": "DD_TAGS",
        "value": "env:fargate"
      },
      {
        "name": "DD_APM_ENABLED",
        "value": "true"
      },
      {
        "name": "DD_APM_NON_LOCAL_TRAFFIC",
        "value": "true"
      }
    ],
    "portMappings": [
      {
        "containerPort": 8126,
        "protocol": "tcp"
      }
    ]
  }
]
