provider "aws" {
  # shared_credentials_file = "$HOME/.aws/credentials"
  # profile                 = "managr-terraform"
}

provider "local" {}

data "aws_region" "current" {}
