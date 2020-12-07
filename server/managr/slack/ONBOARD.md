Set ngrok to the current request_url at: https://api.slack.com/apps/A01ERE1QAE9/interactive-messages

(feel free to change it!)

```
ngrok http -subdomain=managr-request-endpoint 8000
```

ENV variables:

```
SLACK_CLIENT_ID=3505648522.1501477826485
SLACK_SECRET= __

```

Important Notes:

- rotating/expiring Slack access tokens has not been implemented.
  - https://api.slack.com/legacy/workspace-apps/rotating-and-refreshing-credentials
- validating an incoming webhook is from Slack is not currently working.
  - managr.slack.helpers.utils
- endpoint for getting the Slack URL for a message is not implemented.
  - managr.slack.constants.CHAT_GET_PERMALINK
  - can leverage managr.slack.helpers.requests
