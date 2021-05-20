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
  python3-pip \
  cron

ENV DB_NAME=managr \
  DB_USER=managr \
  DB_PASS=managr \
  DB_HOST=localhost

# Set the name of the working directory inside the docker container
WORKDIR /app

# Install pipenv and create a virtual environment with it.
COPY ./Pipfile /app/Pipfile
COPY ./Pipfile.lock /app/Pipfile.lock

# Install Python packages from the Pipfile at the system level,
# since virtual environments are not needed in containers.
RUN pip3 install pipenv \
  && pipenv install --system --deploy --ignore-pipfile

COPY ./deploy/tasks/prod-crontab /etc/cron.d/prod-crontab
RUN chmod 0644 /etc/cron.d/prod-crontab
RUN crontab /etc/cron.d/prod-crontab
RUN touch /var/log/cron.log

# Copy app source
COPY ./server ./server

COPY ./deploy/tasks/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start
ENTRYPOINT [ "/start" ]
