# Managr Deployment

Managr deployment information and instructions.

## Architecture

Managr leverages a container-based architecture that is facilitated via Bitbucket Pipelines. Both the back-end Django application and front-end client are bundled into a Docker image. The Pipeline is configured to build an image for every new tagged deployment into staging and production. All images are pushed into AWS ECR before they are deployed. Images are tagged as follows:

| stage      | tags                                                                                                                                               |
| ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| staging    | `<ecr_endpoint>/thinknimble/managr/server:staging-$BITBUCKET_COMMIT`<br/>`<ecr_endpoint>/thinknimble/managr/server-tasks:staging-$BITBUCKET_PR_ID` |
| production | `<ecr_endpoint>/thinknimble/managr/server:prod-$BITBUCKET_TAG`<br/>`<ecr_endpoint>/thinknimble/managr/server-tasks:prod-$BITBUCKET_TAG`            |

Each deployment stage is associated with an ECS Fargate service and each ECS service is associated with its own Fargate task definition that stipulates the app's compute requirements. During deployment, the Pipeline will automatically update the existing task definition with the updated image tag using the `update-task.sh` script. The Fargate service will then be updated using the default [rolling update strategy](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-type-ecs.html).

### Containers

The Managr deployment is backed by two container images and multiple containers at runtime. The primary image includes both the front-end and back-end components and its Dockerfile can be found in [`server/`](server/). Another similar image includes the scheduled tasks and crontab configuration and can be found in [`tasks/`](tasks/).

The following containers are launched at runtime:

| Name                       | Description                                    |
| -------------------------- | ---------------------------------------------- |
| managr-app                 | Django backend server                          |
| managr-app-proxy           | nginx proxy to Django server and worker        |
| managr-app-worker          | worker                                         |
| managr-app-scheduled-tasks | scheduled tasks                                |
| nginx-config               | loads nginx managrconfig into managr-app-proxy |
| datadog-agent              | Datadog monitoring agent                       |

## Configuration

Below are the configuration steps for deploying Managr.

### AWS

The following AWS resources are required:

- ALB
- Application Auto Scaling
- ECS Fargate
- ECR
- Secrets Manager
- RDB Postgres

### Terraform (optional)

The [`infra/`](infra/) directory includes a Terraform module that can be optionally used as an infrastructure bootstrapping and deployment mechanism. The `sample.tfvars` file can be used for creating separate staging and prod variable input files.

### Fargate

A sample Fargate task definition can be found in the [`taskdefinitions/`](taskdefinitions/) directory. The task definition includes 3 containers: managr server, managr worker and Datadog agent.

### Bitbucket Pipelines

The following Bitbucket variables are required for deployment:

| variable                                   | value                                                                                 |
| ------------------------------------------ | ------------------------------------------------------------------------------------- |
| `MANAGR_SERVER_IMAGE_NAME`                 | Image name. e.g. `<ecr_endpoint>/thinknimble/managr/server`                           |
| `MANAGR_SERVER_SCHEDULED_TASKS_IMAGE_NAME` | Image name for scheduled tasks. e.g. `<ecr_endpoint>/thinknimble/managr/server-tasks` |
| `AWS_ECS_CLUSTER_NAME`                     | AWS ECS cluster name                                                                  |
| `AWS_ECS_SERVICE_NAME`                     | AWS ECS service name                                                                  |
| `AWS_ECS_TASK_NAME`                        | AWS ECS task name. e.g. `managr-app-task`                                             |
| `AWS_ACCESS_KEY_ID`                        | AWS access key id                                                                     |
| `AWS_SECRET_ACCESS_KEY`                    | AWS secret access key                                                                 |

### Datadog

Datadog is used to collect metrics for the deployed application stages. The agent included in the ECS task definition is configured to collect tracing information from the managr server and worker containers. Datadog is also configured to collect metrics from the AWS components including RDS and ALB.




### Adding new variables to the terraform configuration 

1. 
   1. ***Sensitive*** in **ecs.tf** add variable to **aws_secretsmanager_secret_version** this will add the variable to the secrets managr
   2. ***Insensitive*** in **ecs.tf** add variable to the **template_file** since it can be exposed 
2. Add the variable in the **variables.tf** to **environments**
3. Add the variable in the **managr_app.json.tpl** and the **managr_app_tasks.json.tpl** file since we have multiple task definitions here add the variable to the ones that it needs (eg. app and tasks)
4. add to **Dockerfile** for each environment (if needed)
5. add to **default.auto.tfvars** for deployment 
6. Run `terraform apply -auto-approve -parallelism=1` to apply changes 

### SSH Into (New) Environments 


`aws ecs execute-command --cluster managr-cluster --task <task_id> --container <container_name> --interactive --command "/bin/bash"`

You can get the correct task_id by looking at the AWS Console under ECS tasks there may be multiple definitions running (if there was autoscaling) any one will do, the container_name corresponds to the container you are accessing aka managr-app, managr-tasks etc. 



For SSH Access

- Upgarde AWS cli to the latest version if you do not have it (2.x and up)
- Install [session manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html#install-plugin-macos)

There are a couple of ways to ssh into the instance:
1. use the helper commands (see section bellow named connect to the instances helper command)
2. use the two commands to list the instances and then connect 
   1. `aws ecs list-tasks --cluster managr-cluster --family managr-app-task-prod`   cluster will always be managr-cluster family will be managr-app-task-{env} (not app-task is the app you can change that to scheduled tasks etc)
   2. `aws ecs execute-command --cluster managr-cluster --task <task_id> --container managr-app --interactive --command "/bin/bash"` task id will be from the previous command which returns an arn the last part of the arn is the id container name is managr-app

***You will notice we are specifically setting the container name to managr-app but this could be any container we run***

3. Login to the aws console, navigate to ECS tasks and choose the task definition for the environment you are looking for from there you can grab the task id  (note this is the task id not the container id) then use the previous command to connect


### Connect to the instances helper ### 

You can also add a shortcut to connect to prod or staging by copying these into your ~/.zshrc or ~/.bash_profile depending on what you use (remember to source your env after closing the file)
```
alias connect-prod-app="aws ecs execute-command --cluster managr-cluster --task \"$(aws ecs list-tasks --cluster managr-cluster --family managr-app-task-prod | grep -e "arn" | grep -o '/managr-cluster/\w*' | sed "s@/managr-cluster/@@g")\" --container managr-app --interactive --command \"/bin/bash"\"
```
```
alias connect-staging-app="aws ecs execute-command --cluster managr-cluster --task \"$(aws ecs list-tasks --cluster managr-cluster --family managr-app-task-staging | grep -e "arn" | grep -o '/managr-cluster/\w*' | sed "s@/managr-cluster/@@g")\" --container managr-app --interactive --command \"/bin/bash"\"
```

### Describe the task definition

`aws ecs describe-task-definition --task-definition managr-app-task-demo`


### Helpful commands

When updating values for environment variables you will need to re apply the terraform configuration 
`terraform apply -auto-approve -parallelism=1`


