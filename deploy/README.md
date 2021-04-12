# Managr Deployment

Managr deployment information and instructions.

## Architecture

Managr leverages a container-based architecture that is facilitated via Bitbucket Pipelines. Both the back-end Django application and front-end client are bundled into a Docker image. The Pipeline is configured to build an image for each PR and for every new tagged deployment into staging and production. All images are pushed into AWS ECR before they are deployed. Images are tagged as follows:

| stage      | tag                                                                 |
| ---------- | ------------------------------------------------------------------- |
| PR         | `<ecr_endpoint>/thinknimble/managr/server:pr-$BITBUCKET_PR_ID`      |
| staging    | `<ecr_endpoint>/thinknimble/managr/serverstaging-$BITBUCKET_COMMIT` |
| production | `<ecr_endpoint>/thinknimble/managr/serverprod-$BITBUCKET_TAG`       |

Each deployment stage is associated with an ECS Fargate service and each ECS service is associated with its own Fargate task definition that stipulates the app's compute requirements. During deployment, the Pipeline will automatically update the existing task definition with the updated image tag using the `update-task.sh` script. The Fargate service will then be updated using the default [rolling update strategy](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-type-ecs.html).

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

The `infra/` directory includes a Terraform module that can be optionally used as an infrastructure bootstrapping and deployment mechanism.

### Fargate

A sample Fargate task definition can be found in the `taskdefinitions/` directory. The task definition includes 3 containers: managr server, managr worker and Datadog agent.

### Bitbucket Pipelines

The following Bitbucket variables are required for deployment:

| variable                   | value                                                    |
| -------------------------- | -------------------------------------------------------- |
| `MANAGR_SERVER_IMAGE_NAME` | Image tag. e.g. <ecr_endpoint>/thinknimble/managr/server |
| `AWS_ECS_CLUSTER_NAME`     | AWS ECS cluster name                                     |
| `AWS_SERVICE_NAME`         | AWS ECS service name                                     |

### Datadog

Datadog is used to collect metrics for the deployed application stages. The agent included in the ECS task definition is configured to collect tracing information from the managr server and worker containers. Datadog is also configured to collect metrics from the AWS components including RDS and ALB.
