#!/bin/bash
set -e

if [ "$TASK_FAMILY" = "" ]; then
    echo "Missing variable TASK_FAMILY" >&2
    exit 1
fi

if [ "$AWS_DEFAULT_REGION" = "" ]; then
    echo "Missing variable AWS_DEFAULT_REGION" >&2
    exit 1
fi

if [ "$IMAGE_NAME" = "" ]; then
    echo "Missing variable IMAGE_NAME" >&2
    exit 1
fi

if [ "$SCHEDULED_TASKS_IMAGE_NAME" = "" ]; then
    echo "Missing variable SCHEDULED_TASKS_IMAGE_NAME" >&2
    exit 1
fi

TASK_DEFINITION=$(aws ecs describe-task-definition --task-definition "$TASK_FAMILY")
echo $TASK_DEFINITION | jq --arg IMAGE "$IMAGE_NAME" --arg SCHEDULED_TASKS_IMAGE_NAME "$SCHEDULED_TASKS_IMAGE_NAME" '.taskDefinition | .containerDefinitions[0].image = $IMAGE | .containerDefinitions[1].image = $IMAGE | .containerDefinitions[2].image = $SCHEDULED_TASKS_IMAGE_NAME | del(.taskDefinitionArn) | del(.revision) | del(.status) | del(.requiresAttributes) | del(.compatibilities)' >task-definition.json
