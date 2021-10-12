[
  {
    "name": "managr-app-scheduled-tasks",
    "image": "${app_image_scheduled_tasks}",
    "networkMode": "awsvpc",
    "command": ${command},
    "environment": [
      { "name": "DD_SERVICE", "value": "managr-server-scheduled-tasks" },
      { "name": "DD_ENV", "value": "fargate:${environment}" },
      { "name": "DD_PROFILING_ENABLED", "value": "true" },

      { "name": "ALLOWED_HOSTS", "value": "${allowed_hosts}" },
      { "name": "CURRENT_DOMAIN", "value": "${current_domain}" },
      { "name": "CURRENT_PORT", "value": "${current_port}" },
      { "name": "DEBUG", "value": "${debug}" },
      { "name": "ENVIRONMENT", "value": "${environment}" },

      { "name": "USE_CUSTOM_SMTP", "value": "${use_custom_smtp}" },
      { "name": "SMTP_USE_TLS", "value": "${smtp_use_tls}" },
      { "name": "SMTP_PORT", "value": "${smtp_port}" },
      { "name": "SMTP_VALID_TESTING_DOMAINS", "value": "${smtp_valid_testing_domains}" },

      { "name": "AWS_LOCATION", "value": "${aws_location}" },
      { "name": "ENVIRONMENT", "value": "${environment}" },
      { "name": "USE_ROLLBAR", "value": "${use_rollbar}" },
      { "name": "USE_NYLAS", "value": "${use_nylas}" },
      { "name": "USE_TWILIO", "value": "${use_twilio}" },
      { "name": "USE_ZOOM", "value": "${use_zoom}" },
      { "name": "USE_SLACK", "value": "${use_slack}" },
      { "name": "USE_SALESFORCE", "value": "${use_salesforce}" },
      { "name": "USE_SALESLOFT", "value": "${use_salesloft}" }
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
        "name": "dbSnapShot",
        "valueFrom": "${config_secret_arn}:dbSnapShot::"
      },
      {
        "name": "SUPERUSER_EMAIL",
        "valueFrom": "${config_secret_arn}:superuserEmail::"
      },
      {
        "name": "SUPERUSER_PASSWORD",
        "valueFrom": "${config_secret_arn}:superuserPassword::"
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
        "name": "SLACK_ERROR_WEBHOOK",
        "valueFrom": "${config_secret_arn}:slackErrorWebhook::"
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
      },
      {
        "name": "SALESLOFT_BASE_URL",
        "valueFrom": "${config_secret_arn}:salesloftBaseUrl::"
      },
      {
        "name": "SALESLOFT_CLIENT_ID",
        "valueFrom": "${config_secret_arn}:salesloftClientId::"
      },
      {
        "name": "SALESLOFT_SECRET",
        "valueFrom": "${config_secret_arn}:salesloftSecret::"
      },
      {
        "name": "SALESLOFT_REDIRECT_URI",
        "valueFrom": "${config_secret_arn}:salesloftRedirectUri::"
      },
      {
        "name": "GONG_BASE_URL",
        "valueFrom": "${config_secret_arn}:gongBaseUrl::"
      },
      {
        "name": "GONG_CLIENT_ID",
        "valueFrom": "${config_secret_arn}:gongClientId::"
      },
      {
        "name": "GONG_SECRET",
        "valueFrom": "${config_secret_arn}:gongSecret::"
      },
      {
        "name": "GONG_REDIRECT_URI",
        "valueFrom": "${config_secret_arn}:gongRedirectUri::"
      }
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "${aws_logs_group}",
        "awslogs-region": "${aws_region}",
        "awslogs-stream-prefix": "ecs"
      }
    }
  },
  {
    "name": "datadog-agent",
    "essential": false,
    "image": "${datadog_image}",
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
        "value": "env:fargate:${environment}"
      },
      {
        "name": "DD_APM_ENABLED",
        "value": "true"
      },
      {
        "name": "DD_APM_NON_LOCAL_TRAFFIC",
        "value": "true"
      },
      {
        "name": "DD_DOGSTATSD_NON_LOCAL_TRAFFIC",
        "value": "true"
      }
    ],
    "portMappings": [
      {
        "containerPort": 8126,
        "protocol": "tcp"
      },
      {
        "containerPort": 8125,
        "protocol": "udp"
      }
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "${aws_logs_group}",
        "awslogs-region": "${aws_region}",
        "awslogs-stream-prefix": "ecs"
      }
    }
  }
]
