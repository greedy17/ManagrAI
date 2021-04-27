provider "aws" {
  shared_credentials_file = "$HOME/.aws/credentials"
  profile                 = "managr-terraform"
  region                  = var.aws_region
}

provider "local" {}
