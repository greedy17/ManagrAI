[
  {
    "name": "managr-app-proxy",
    "image": "nginx",
    "essential": true,
    "dependsOn": [
      {
        "containerName": "managr-app",
        "condition": "START"
      },
      {
        "containerName": "nginx-config",
        "condition": "COMPLETE"
      }
    ],
    "portMappings": [
      {
        "containerPort": 80,
        "hostPort": 80
      }
    ],
    "mountPoints": [
      {
        "containerPath": "/etc/nginx",
        "sourceVolume": "nginx-conf-vol"
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
    "name": "nginx-config",
    "image": "bash",
    "essential": false,
    "command": ["-c", "echo $DATA | base64 -d - | tee /etc/nginx/nginx.conf"],
    "environment": [
      {
        "name": "DATA",
        "value": "${nginx_config}"
      }
    ],
    "mountPoints": [
      {
        "containerPath": "/etc/nginx",
        "sourceVolume": "nginx-conf-vol"
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
    "name": "managr-app",
    "image": "${app_image}",
    "cpu": ${fargate_cpu},
    "memory": ${fargate_memory},
    "networkMode": "awsvpc",
    "environment": [
      { "name": "DD_SERVICE", "value": "managr-server" },
      { "name": "DD_ENV", "value": "fargate" },
      { "name": "DD_PROFILING_ENABLED", "value": "true" },

      { "name": "ALLOWED_HOSTS", "value": "*" },
      { "name": "CURRENT_DOMAIN", "value": "${current_domain}" },
      { "name": "CURRENT_PORT", "value": "${current_port}" },
      { "name": "DEBUG", "value": "${debug}" },

      { "name": "USE_CUSTOM_SMTP", "value": "${use_custom_smtp}" },
      { "name": "SMTP_USE_TLS", "value": "${smtp_use_tls}" },
      { "name": "SMTP_PORT", "value": "${smtp_port}" },
      { "name": "SMTP_VALID_TESTING_DOMAINS", "value": "${smtp_valid_testing_domains}" },

      { "name": "USE_AWS_STORAGE", "value": "${use_aws_storage}" },
      { "name": "AWS_LOCATION", "value": "${aws_location}" },
      { "name": "AWS_LOCATION_DEV", "value": "${aws_location_dev}" },
      { "name": "AWS_LOCATION_STAGING", "value": "${aws_location_staging}" },
      { "name": "AWS_LOCATION_PROD", "value": "${aws_location_prod}" },

      { "name": "USE_ROLLBAR", "value": "${use_rollbar}" },
      { "name": "USE_NYLAS", "value": "${use_nylas}" },
      { "name": "USE_TWILIO", "value": "${use_twilio}" },
      { "name": "USE_ZOOM", "value": "${use_zoom}" },
      { "name": "USE_SLACK", "value": "${use_slack}" },
      { "name": "TEST_SLACK", "value": "${test_slack}" },
      { "name": "USE_SALESFORCE", "value": "${use_salesforce}" }
    ],
    "secrets": [
      {
        "name": "SECRET_KEY",
        "valueFrom": "${config_secret_arn}:secretKey::"
      },
      {
        "name": "STAFF_EMAIL",
        "valueFrom": "${config_secret_arn}:staffEmail::"
      },

      {
        "name": "DB_HOST",
        "valueFrom": "${config_secret_arn}:dbHost::"
      },
      {
        "name": "DB_USER",
        "valueFrom": "${config_secret_arn}:dbUser::"
      },
      {
        "name": "DB_PASS",
        "valueFrom": "${config_secret_arn}:dbPass::"
      },
      {
        "name": "DB_NAME",
        "valueFrom": "${config_secret_arn}:dbName::"
      },

      {
        "name": "ROLLBAR_ACCESS_TOKEN",
        "valueFrom": "${config_secret_arn}:rollbarAccessToken::"
      },

      {
        "name": "SMTP_USER",
        "valueFrom": "${config_secret_arn}:smtpUser::"
      },
      {
        "name": "SMTP_PASSWORD",
        "valueFrom": "${config_secret_arn}:smtpPassword::"
      },
      {
        "name": "SMTP_HOST",
        "valueFrom": "${config_secret_arn}:smtpHost::"
      },

      {
        "name": "AWS_ACCESS_KEY_ID",
        "valueFrom": "${config_secret_arn}:awsAccessKeyId::"
      },
      {
        "name": "AWS_SECRET_ACCESS_KEY",
        "valueFrom": "${config_secret_arn}:awsSecretAccessKey::"
      },
      {
        "name": "AWS_STORAGE_BUCKET_NAME",
        "valueFrom": "${config_secret_arn}:awsStorageBucketName::"
      },

      {
        "name": "NYLAS_CLIENT_ID",
        "valueFrom": "${config_secret_arn}:nylasClientId::"
      },
      {
        "name": "NYLAS_CLIENT_SECRET",
        "valueFrom": "${config_secret_arn}:nylasClientSecret::"
      },
      {
        "name": "NYLAS_OAUTH_CALLBACK_URL",
        "valueFrom": "${config_secret_arn}:nylasOauthCallbackUrl::"
      },

      {
        "name": "TWILIO_ACCOUNT_SID",
        "valueFrom": "${config_secret_arn}:twilioAccountSid::"
      },
      {
        "name": "TWILIO_AUTH_TOKEN",
        "valueFrom": "${config_secret_arn}:twilioAuthToken::"
      },
      {
        "name": "TWILIO_BASE_CALLBACK_URL",
        "valueFrom": "${config_secret_arn}:twilioBaseCallbackUrl::"
      },

      {
        "name": "ZOOM_REDIRECT_URI",
        "valueFrom": "${config_secret_arn}:zoomRedirectUri::"
      },
      {
        "name": "ZOOM_CLIENT_ID",
        "valueFrom": "${config_secret_arn}:zoomClientId::"
      },
      {
        "name": "ZOOM_SECRET",
        "valueFrom": "${config_secret_arn}:zoomSecret::"
      },
      {
        "name": "ZOOM_WEBHOOK_TOKEN",
        "valueFrom": "${config_secret_arn}:zoomWebhookToken::"
      },
      {
        "name": "ZOOM_FAKE_MEETING_UUID",
        "valueFrom": "${config_secret_arn}:zoomFakeMeetingUuid::"
      },

      {
        "name": "SLACK_CLIENT_ID",
        "valueFrom": "${config_secret_arn}:slackClientId::"
      },
      {
        "name": "SLACK_SECRET",
        "valueFrom": "${config_secret_arn}:slackSecret::"
      },
      {
        "name": "SLACK_SIGNING_SECRET",
        "valueFrom": "${config_secret_arn}:slackSigningSecret::"
      },
      {
        "name": "SLACK_APP_VERSION",
        "valueFrom": "${config_secret_arn}:slackAppVersion::"
      },

      {
        "name": "SLACK_TEST_TEAM_NAME",
        "valueFrom": "${config_secret_arn}:slackTestTeamName::"
      },
      {
        "name": "SLACK_TEST_TEAM_ID",
        "valueFrom": "${config_secret_arn}:slackTestTeamId::"
      },
      {
        "name": "SLACK_TEST_BOT_USER_ID",
        "valueFrom": "${config_secret_arn}:slackTestBotUserId::"
      },
      {
        "name": "SLACK_TEST_ACCESS_TOKEN",
        "valueFrom": "${config_secret_arn}:slackTestAccessToken::"
      },
      {
        "name": "SLACK_TEST_INCOMING_WEBHOOK_URL",
        "valueFrom": "${config_secret_arn}:slackTestIncomingWebhookUrl::"
      },
      {
        "name": "SLACK_TEST_INCOMING_WEBHOOK_CHANNEL",
        "valueFrom": "${config_secret_arn}:slackTestIncomingWebhookChannel::"
      },
      {
        "name": "SLACK_TEST_INCOMING_WEBHOOK_CHANNEL_ID",
        "valueFrom": "${config_secret_arn}:slackTestIncomingWebhookChannelId::"
      },
      {
        "name": "SLACK_TEST_INCOMING_WEBHOOK_CONFIGURATION_URL",
        "valueFrom": "${config_secret_arn}:slackTestIncomingWebhookConfigurationUrl::"
      },
      
      {
        "name": "SALESFORCE_BASE_URL",
        "valueFrom": "${config_secret_arn}:salesforceBaseUrl::"
      },
      {
        "name": "SALESFORCE_CONSUMER_KEY",
        "valueFrom": "${config_secret_arn}:salesforceConsumerKey::"
      },
      {
        "name": "SALESFORCE_SECRET",
        "valueFrom": "${config_secret_arn}:salesforceSecret::"
      },
      {
        "name": "SALESFORCE_SCOPES",
        "valueFrom": "${config_secret_arn}:salesforceScopes::"
      },
      {
        "name": "SALESFORCE_REDIRECT_URI",
        "valueFrom": "${config_secret_arn}:salesforceRedirectUri::"
      },
      {
        "name": "SALESFORCE_API_VERSION",
        "valueFrom": "${config_secret_arn}:salesforceApiVersion::"
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
        "containerPort": 8000
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
      { "name": "DD_SERVICE", "value": "managr-server-worker" },
      { "name": "DD_ENV", "value": "fargate" },
      { "name": "DD_PROFILING_ENABLED", "value": "true" }
    ],
    "secrets": [
      {
        "name": "DB_HOST",
        "valueFrom": "${config_secret_arn}:dbHost::"
      },
      {
        "name": "DB_USER",
        "valueFrom": "${config_secret_arn}:dbUser::"
      },
      {
        "name": "DB_PASS",
        "valueFrom": "${config_secret_arn}:dbPass::"
      },
      {
        "name": "DB_NAME",
        "valueFrom": "${config_secret_arn}:dbName::"
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
        "containerPort": 8001
      }
    ]
  },
  {
    "name": "managr-app-scheduled-tasks",
    "dependsOn": [
      {
        "containerName": "managr-app",
        "condition": "START"
      }
    ],
    "image": "${app_image_scheduled_tasks}",
    "networkMode": "awsvpc",
    "environment": [
      { "name": "DD_SERVICE", "value": "managr-server-scheduled-tasks" },
      { "name": "DD_ENV", "value": "fargate" },
      { "name": "DD_PROFILING_ENABLED", "value": "true" }
    ],
    "secrets": [
      {
        "name": "DB_HOST",
        "valueFrom": "${config_secret_arn}:dbHost::"
      },
      {
        "name": "DB_USER",
        "valueFrom": "${config_secret_arn}:dbUser::"
      },
      {
        "name": "DB_PASS",
        "valueFrom": "${config_secret_arn}:dbPass::"
      },
      {
        "name": "DB_NAME",
        "valueFrom": "${config_secret_arn}:dbName::"
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
        "valueFrom": "${config_secret_arn}:ddApiKey::"
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
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "/ecs/managr-app",
        "awslogs-region": "${aws_region}",
        "awslogs-stream-prefix": "ecs"
      }
    }
  }
]
