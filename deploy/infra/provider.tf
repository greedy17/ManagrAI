provider "aws" {
   shared_credentials_file = "$HOME/.aws/credentials"
   profile                 = "managr-terraform"
   region                  = "us-east-1"
}

provider "local" {}

data "aws_region" "current" {}

#Update with ThinkNimble's S3 bucket
terraform {
  backend "s3" {
    bucket = "managr-app-tfstate"
    key    = "tfstate"
    region = "us-east-1"
  }
}
