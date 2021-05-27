#!/bin/bash
set -e

docker pull datadog/agent:latest
docker pull bash:latest

docker tag datadog/agent:latest "${ECR_DATADOG_REPO}:latest"
docker tag bash:latest "${ECR_BASH_REPO}:latest"

aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY_URL}
docker push "${ECR_DATADOG_REPO}:latest"
docker push "${ECR_BASH_REPO}:latest"
