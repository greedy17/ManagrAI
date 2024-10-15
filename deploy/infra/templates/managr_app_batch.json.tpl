{
    "name": "managr-app-batch-task",
    "image": "${app_image_scheduled_tasks}",
    "networkMode": "awsvpc",
    "executionRoleArn": "${execution_role_arn}",
    "command": ["crawl_spider"],
    "resourceRequirements": [
      {
        "type"  : "VCPU",
        "value" : "4"
      },
      {
        "type"  : "MEMORY",
        "value" : "8192"
      }
    ],
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
      { "name": "USE_AWS_STORAGE", "value": "${use_aws_storage}" },
      { "name": "AWS_LOCATION", "value": "${aws_location}" },
      { "name": "USE_ROLLBAR", "value": "${use_rollbar}" },
      { "name": "USE_NYLAS", "value": "${use_nylas}" },
      { "name": "USE_TWILIO", "value": "${use_twilio}" },
      { "name": "USE_ZOOM", "value": "${use_zoom}" },
      { "name": "USE_SLACK", "value": "${use_slack}" },
      { "name": "USE_SALESFORCE", "value": "${use_salesforce}" },
      { "name": "USE_SALESLOFT", "value": "${use_salesloft}" },
      { "name": "USE_GONG", "value": "${use_gong}" },
      { "name": "USE_OUTREACH", "value": "${use_outreach}" },
      { "name": "USE_HUBSPOT", "value": "${use_hubspot}" },
      { "name": "USE_OPEN_AI", "value": "${use_open_ai}" },
      { "name": "USE_SSO", "value": "${use_sso}" },
      { "name": "USE_NEWS_API", "value": "${use_news_api}" },
      { "name": "USE_TWITTER_API", "value": "${use_twitter_api}" },
      { "name": "USE_INSTAGRAM_API", "value": "${use_instagram_api}" }
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
        "name": "ZOOM_VERIFICATION_TOKEN",
        "valueFrom": "${config_secret_arn}:zoomVerificationToken::"
      },
      {
        "name": "ZOOM_API_SECRET",
        "valueFrom": "${config_secret_arn}:zoomApiSecret::"
      },
      {
        "name": "ZOOM_API_KEY",
        "valueFrom": "${config_secret_arn}:zoomApiKey::"
      },
      {
        "name": "SLACK_CLIENT_ID",
        "valueFrom": "${config_secret_arn}:slackClientId::"
      },
      {
        "name": "SLACK_CLIENT_SECRET",
        "valueFrom": "${config_secret_arn}:slackClientSecret::"
      },
      {
        "name": "SLACK_OAUTH_CALLBACK_URL",
        "valueFrom": "${config_secret_arn}:slackOauthCallbackUrl::"
      },
      {
        "name": "SLACK_VERIFICATION_TOKEN",
        "valueFrom": "${config_secret_arn}:slackVerificationToken::"
      },
      {
        "name": "SALESFORCE_CLIENT_ID",
        "valueFrom": "${config_secret_arn}:salesforceClientId::"
      },
      {
        "name": "SALESFORCE_CLIENT_SECRET",
        "valueFrom": "${config_secret_arn}:salesforceClientSecret::"
      },
      {
        "name": "SALESFORCE_OAUTH_CALLBACK_URL",
        "valueFrom": "${config_secret_arn}:salesforceOauthCallbackUrl::"
      },
      {
        "name": "SALESLOFT_CLIENT_ID",
        "valueFrom": "${config_secret_arn}:salesloftClientId::"
      },
      {
        "name": "SALESLOFT_CLIENT_SECRET",
        "valueFrom": "${config_secret_arn}:salesloftClientSecret::"
      },
      {
        "name": "SALESLOFT_OAUTH_CALLBACK_URL",
        "valueFrom": "${config_secret_arn}:salesloftOauthCallbackUrl::"
      },
      {
        "name": "GONG_CLIENT_ID",
        "valueFrom": "${config_secret_arn}:gongClientId::"
      },
      {
        "name": "GONG_CLIENT_SECRET",
        "valueFrom": "${config_secret_arn}:gongClientSecret::"
      },
      {
        "name": "GONG_OAUTH_CALLBACK_URL",
        "valueFrom": "${config_secret_arn}:gongOauthCallbackUrl::"
      },
      {
        "name": "OUTREACH_CLIENT_ID",
        "valueFrom": "${config_secret_arn}:outreachClientId::"
      },
      {
        "name": "OUTREACH_CLIENT_SECRET",
        "valueFrom": "${config_secret_arn}:outreachClientSecret::"
      },
      {
        "name": "OUTREACH_OAUTH_CALLBACK_URL",
        "valueFrom": "${config_secret_arn}:outreachOauthCallbackUrl::"
      },
      {
        "name": "HUBSPOT_CLIENT_ID",
        "valueFrom": "${config_secret_arn}:hubspotClientId::"
      },
      {
        "name": "HUBSPOT_CLIENT_SECRET",
        "valueFrom": "${config_secret_arn}:hubspotClientSecret::"
      },
      {
        "name": "HUBSPOT_OAUTH_CALLBACK_URL",
        "valueFrom": "${config_secret_arn}:hubspotOauthCallbackUrl::"
      },
      {
        "name": "OPEN_AI_API_KEY",
        "valueFrom": "${config_secret_arn}:openAiApiKey::"
      },
      {
        "name": "SSO_CLIENT_ID",
        "valueFrom": "${config_secret_arn}:ssoClientId::"
      },
      {
        "name": "SSO_CLIENT_SECRET",
        "valueFrom": "${config_secret_arn}:ssoClientSecret::"
      },
      {
        "name": "SSO_OAUTH_CALLBACK_URL",
        "valueFrom": "${config_secret_arn}:ssoOauthCallbackUrl::"
      },
      {
        "name": "NEWS_API_KEY",
        "valueFrom": "${config_secret_arn}:newsApiKey::"
      },
      {
        "name": "TWITTER_API_KEY",
        "valueFrom": "${config_secret_arn}:twitterApiKey::"
      },
      {
        "name": "TWITTER_API_SECRET",
        "valueFrom": "${config_secret_arn}:twitterApiSecret::"
      },
      {
        "name": "INSTAGRAM_API_KEY",
        "valueFrom": "${config_secret_arn}:instagramApiKey::"
      },
      {
        "name": "INSTAGRAM_API_SECRET",
        "valueFrom": "${config_secret_arn}:instagramApiSecret::"
      },
      {
        "name": "INSTAGRAM_REDIRECT_URI",
        "valueFrom": "${config_secret_arn}:instagramRedirectUri::"
      },
      {
        "name": "HUNTER_API_KEY",
        "valueFrom": "${config_secret_arn}:hunterApiKey::"
      },
      {
        "name": "GOOGLE_SEARCH_API_KEY",
        "valueFrom": "${config_secret_arn}:googleSearchApiKey::"
      },
      {
        "name": "GOOGLE_SEARCH_ID",
        "valueFrom": "${config_secret_arn}:googleSearchId::"
      },
      {
        "name": "GOOGLE_CLIENT_SECRET",
        "valueFrom": "${config_secret_arn}:googleClientSecret::"
      },
      {
        "name": "GOOGLE_REDIRECT_URI",
        "valueFrom": "${config_secret_arn}:googleRedirectUri::"
      },
      {
        "name": "MICROSOFT_CLIENT_ID",
        "valueFrom": "${config_secret_arn}:microsoftClientId::"
      },
      {
        "name": "MICROSOFT_CLIENT_SECRET",
        "valueFrom": "${config_secret_arn}:microsoftClientSecret::"
      },
      {
        "name": "MICROSOFT_REDIRECT_URI",
        "valueFrom": "${config_secret_arn}:microsoftRedirectUri::"
      },
      {
        "name": "SCRAPER_API_KEY",
        "valueFrom": "${config_secret_arn}:scraperApiKey::"
      },
      {
        "name": "SEMRUSH_API_KEY",
        "valueFrom": "${config_secret_arn}:semrushApiKey::"
      },
      {
        "name": "BUZZSUMO_API_KEY",
        "valueFrom": "${config_secret_arn}:buzzsumoApiKey::"
      }
    ]
}
