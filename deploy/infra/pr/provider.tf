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

    random = {
      source  = "hashicorp/random"
      version = "3.1.0"
    }
  }

  backend "s3" {
    bucket = "managr-app-tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = "us-east-1"
}
