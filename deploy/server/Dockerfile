FROM node:14 AS build-client
ARG NPM_PRIVATE_TOKEN
ARG VUE_APP_DD_APP_ID=35ea3d99-bcca-4bb4-a524-e5286670d24f
ARG VUE_APP_DD_CLIENT_TOKEN=pubb6721f7da3995916ac146e3fefc18ad6
ARG VUE_APP_DD_ENV
WORKDIR /app
COPY ./client/package.json ./client/package-lock.json ./client/.npmrc ./
RUN npm install
COPY ./client .
RUN npm run build

FROM python:3.7-slim-buster

# These environment values help with watching for file changes
ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1

# Install system-level dependencies.
RUN apt-get update && apt-get install -y \
  # dependencies for building Python packages
  build-essential \
  gcc \
  # psycopg2 dependencies
  libpq-dev \
  # Pillow dependencies
  libjpeg-dev zlib1g-dev \
  python3-pip

ENV SECRET_KEY='secret123' \
  ENVIRONMENT='' \
  STAFF_EMAIL='test@test.com' \
  ALLOWED_HOSTS=* \
  CURRENT_DOMAIN=localhost \
  CURRENT_PORT=8080 \
  DB_NAME=managr \
  DB_USER=managr\
  DB_PASS=managr \
  SUPERUSER_EMAIL='' \
  SUPERUSER_PASSWORD='' \
  DB_HOST=localhost \
  DEBUG=True \
  USE_ROLLBAR=False \
  ROLLBAR_ACCESS_TOKEN='' \
  USE_CUSTOM_SMTP=False \
  SMTP_USER='' \
  SMTP_USE_TLS=False \
  SMTP_PASSWORD='' \
  SMTP_HOST='' \
  SMTP_PORT='' \
  SMTP_VALID_TESTING_DOMAINS='' \
  USE_AWS_STORAGE=False \
  AWS_ACCESS_KEY_ID='' \
  AWS_SECRET_ACCESS_KEY='' \
  AWS_STORAGE_BUCKET_NAME='' \
  AWS_LOCATION='' \
  AWS_LOCATION_DEV='' \
  AWS_LOCATION_STAGING='' \
  AWS_LOCATION_PROD='' \
  USE_NYLAS=False \
  NYLAS_CLIENT_ID='' \
  NYLAS_CLIENT_SECRET='' \
  NYLAS_OAUTH_CALLBACK_URL='' \
  USE_TWILIO=False \
  TWILIO_ACCOUNT_SID='' \
  TWILIO_AUTH_TOKEN='' \
  TWILIO_BASE_CALLBACK_URL='' \
  USE_ZOOM=False \
  ZOOM_REDIRECT_URI='' \
  ZOOM_CLIENT_ID='' \
  ZOOM_SECRET='' \
  ZOOM_WEBHOOK_TOKEN='' \
  ZOOM_FAKE_MEETING_UUID='' \
  USE_SLACK=False \
  SLACK_CLIENT_ID='' \
  SLACK_SECRET='' \
  SLACK_SIGNING_SECRET='' \
  SLACK_APP_VERSION='' \
  SLACK_ERROR_WEBHOOK='' \
  TEST_SLACK=False \
  SLACK_TEST_TEAM_NAME='' \
  SLACK_TEST_TEAM_ID='' \
  SLACK_TEST_BOT_USER_ID='' \
  SLACK_TEST_ACCESS_TOKEN='' \
  SLACK_TEST_INCOMING_WEBHOOK_URL='' \
  SLACK_TEST_INCOMING_WEBHOOK_CHANNEL='' \
  SLACK_TEST_INCOMING_WEBHOOK_CHANNEL_ID='' \
  SLACK_TEST_INCOMING_WEBHOOK_CONFIGURATION_URL='' \
  USE_SALESFORCE=False \
  SALESFORCE_BASE_URL='' \
  SALESFORCE_CONSUMER_KEY='' \
  SALESFORCE_SECRET='' \
  SALESFORCE_SCOPES='' \
  SALESFORCE_REDIRECT_URI='' \
  SALESFORCE_API_VERSION=''

# Set the name of the working directory inside the docker container
WORKDIR /app

# Install pipenv and create a virtual environment with it.
COPY ./Pipfile /app/Pipfile
COPY ./Pipfile.lock /app/Pipfile.lock

# Install Python packages from the Pipfile at the system level,
# since virtual environments are not needed in containers.
RUN pip3 install pipenv \
  && pipenv install --system --deploy --ignore-pipfile

# Copy app source
COPY ./server ./server
COPY --from=build-client /app/dist ./client/dist

RUN python3 server/manage.py collectstatic --noinput

# Move the 'start' shell script to the root
# and alter line endings for compatibility.
COPY ./deploy/server/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start
ENTRYPOINT [ "/start" ]
