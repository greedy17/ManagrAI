#!/bin/bash
set -e

docker pull datadog/agent:latest
docker pull bash:latest

docker tag datadog/agent:latest "${ECR_DATADOG_REPO}:latest"
docker tag bash:latest "${ECR_BASH_REPO}:latest"

aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY_URL}
docker push "${ECR_DATADOG_REPO}:latest"
docker push "${ECR_BASH_REPO}:latest"

docker build -f deploy/server/Dockerfile --build-arg NPM_PRIVATE_TOKEN --build-arg "VUE_APP_DD_ENV=fargate:prod" -t ${MANAGR_SERVER_IMAGE_NAME} .
docker build -f deploy/tasks/Dockerfile -t ${MANAGR_SERVER_SCHEDULED_TASKS_IMAGE_NAME} .
docker build -f deploy/nginx/Dockerfile -t ${MANAGR_SERVER_NGINX_IMAGE_NAME} deploy/nginx/

docker push ${MANAGR_SERVER_IMAGE_NAME}
docker push ${MANAGR_SERVER_SCHEDULED_TASKS_IMAGE_NAME}
docker push ${MANAGR_SERVER_NGINX_IMAGE_NAME}
