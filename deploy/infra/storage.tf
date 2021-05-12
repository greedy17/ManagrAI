resource "aws_s3_bucket" "managr" {
  bucket        = var.s3_bucket_name
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

resource "aws_s3_bucket_object" "public" {
  bucket       = aws_s3_bucket.managr.id
  key          = "public/slack/"
  content_type = "application/x-directory"
}

resource "aws_s3_bucket_policy" "public" {
  bucket = aws_s3_bucket.managr.id
  policy = jsonencode(
    {
      Version = "2008-10-17"
      Statement = [
        {
          Sid    = "AllowPublicRead"
          Effect = "Allow"
          Principal = {
            AWS = "*"
          }
          Action   = "s3:GetObject"
          Resource = "${aws_s3_bucket.managr.arn}/${aws_s3_bucket_object.public.id}*"
        }
      ]
  })
}
