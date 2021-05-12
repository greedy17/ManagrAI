
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "3.38.0"
    }

    local = {
      source  = "hashicorp/local"
      version = "2.1.0"
    }
  }

  #Update with ThinkNimble's S3 bucket
   backend "s3" {
     bucket = "managr-app-tfstate"
     key    = "tfstate"
     region = "us-east-1"
   }
}

provider "aws" {}

data "aws_region" "current" {}
