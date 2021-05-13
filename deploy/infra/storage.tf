resource "aws_s3_bucket" "managr" {
  bucket        = lower(var.s3_bucket_name)
  acl           = "private"
  force_destroy = true
  versioning {
    enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "managr" {
  bucket                  = aws_s3_bucket.managr.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket" "managr_public" {
  bucket        = "${lower(var.s3_bucket_name)}-public"
  acl           = "public-read"
  force_destroy = true
  versioning {
    enabled = true
  }
}


resource "aws_s3_bucket_object" "managr_public" {
  bucket       = aws_s3_bucket.managr_public.id
  key          = "public/slack/"
  content_type = "application/x-directory"
}

resource "aws_s3_bucket_policy" "managr_public" {
  bucket = aws_s3_bucket.managr_public.id
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
          Resource = "${aws_s3_bucket.managr_public.arn}/${aws_s3_bucket_object.managr_public.id}*"
        }
      ]
  })
}
