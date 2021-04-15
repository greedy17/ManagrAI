resource "aws_s3_bucket" "managr" {
  bucket        = var.aws_storage_bucket_name
  acl           = "private"
  force_destroy = true
  versioning {
    enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "managr" {
  bucket              = aws_s3_bucket.managr.id
  block_public_acls   = true
  block_public_policy = true
}
