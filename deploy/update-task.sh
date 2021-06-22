#!/bin/bash
set -e

if [ "$AWS_DEFAULT_REGION" = "" ]; then
    echo "Missing variable AWS_DEFAULT_REGION" >&2
    exit 1
fi

if [ "$MANAGR_ECR_REPO_URL" = "" ]; then
    echo "Missing variable MANAGR_ECR_REPO_URL" >&2
    exit 1
fi

if [ "$MANAGR_SERVER_IMAGE_NAME" = "" ]; then
    echo "Missing variable MANAGR_SERVER_IMAGE_NAME" >&2
    exit 1
fi

if [ "$MANAGR_SERVER_SCHEDULED_TASKS_IMAGE_NAME" = "" ]; then
    echo "Missing variable MANAGR_SERVER_SCHEDULED_TASKS_IMAGE_NAME" >&2
    exit 1
fi

if [ "$IMAGE_TAG" = "" ]; then
    echo "Missing variable IMAGE_TAG" >&2
    exit 1
fi

IMAGE_NAME="$MANAGR_ECR_REPO_URL/$MANAGR_SERVER_IMAGE_NAME:$IMAGE_TAG"
SCHEDULED_TASKS_IMAGE_NAME="$MANAGR_ECR_REPO_URL/$MANAGR_SERVER_SCHEDULED_TASKS_IMAGE_NAME:$IMAGE_TAG"

if [ -n "$TASK_FAMILY" ]; then
    TASK_DEFINITION=$(aws ecs describe-task-definition --task-definition "$TASK_FAMILY")
    echo $TASK_DEFINITION | jq --arg IMAGE "$IMAGE_NAME" '.taskDefinition | .containerDefinitions[0].image = $IMAGE | del(.taskDefinitionArn) | del(.revision) | del(.status) | del(.requiresAttributes) | del(.compatibilities) | del(.registeredAt) | del(.registeredBy)' >task-definition.json
elif [ -n "$SCHEDULED_TASK_FAMILY" ]; then
    TASK_DEFINITION=$(aws ecs describe-task-definition --task-definition "$SCHEDULED_TASK_FAMILY")
    echo $TASK_DEFINITION | jq --arg SCHEDULED_TASKS_IMAGE_NAME "$SCHEDULED_TASKS_IMAGE_NAME" '.taskDefinition | .containerDefinitions[0].image = $SCHEDULED_TASKS_IMAGE_NAME | del(.taskDefinitionArn) | del(.revision) | del(.status) | del(.requiresAttributes) | del(.compatibilities) | del(.registeredAt) | del(.registeredBy)' >task-definition.json
    aws ecs register-task-definition --family "$SCHEDULED_TASK_FAMILY" --cli-input-json file://task-definition.json
    TASK_REVISION=$(aws ecs describe-task-definition --task-definition "$SCHEDULED_TASK_FAMILY" | jq '.taskDefinition.revision')
    EVENTS_RULE=$(aws events list-targets-by-rule --rule "$SCHEDULED_TASK_FAMILY")
    TASK_DEFINITION_ARN=$(aws events list-targets-by-rule --rule "$SCHEDULED_TASK_FAMILY" | egrep "TaskDefinitionArn" | tr "/" " " | awk '{print $2}')
    EVENTS_ROLE=$(aws events list-targets-by-rule --rule "$SCHEDULED_TASK_FAMILY" | egrep "RoleArn" | tr "/" " " | awk '{print $2}')
    ROLE_ARN="${EVENTS_ROLE:1}/ecs-events-role"
    NEW_TASK_DEFINITION_ARN="${TASK_DEFINITION_ARN:1}/${SCHEDULED_TASK_FAMILY}:${TASK_REVISION}"
    echo $EVENTS_RULE | jq '.Targets[0].EcsParameters.TaskDefinitionArn='\"${NEW_TASK_DEFINITION_ARN}\" | jq '.Targets[0].RoleArn='\"${ROLE_ARN}\" >tempEvents.json
    aws events put-targets --rule "$SCHEDULED_TASK_FAMILY" --cli-input-json file://tempEvents.json
fi
