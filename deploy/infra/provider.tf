provider "aws" {
  shared_credentials_file = "$HOME/.aws/credentials"
  profile                 = "managr-terraform"
  region              = "us-east-1"
}

provider "local" {}

data "aws_region" "current" {}
