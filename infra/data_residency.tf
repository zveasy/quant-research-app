# Terraform configuration for regional buckets used to satisfy data residency requirements

provider "aws" {
  alias  = "eu"
  region = "eu-central-1"
}

provider "aws" {
  alias  = "ap"
  region = "ap-southeast-1"
}

resource "aws_kms_key" "eu" {
  provider = aws.eu
  description = "EU bucket encryption"
}

resource "aws_kms_alias" "eu" {
  provider      = aws.eu
  name          = "alias/data-residency-eu"
  target_key_id = aws_kms_key.eu.key_id
}

resource "aws_kms_key" "ap" {
  provider = aws.ap
  description = "APAC bucket encryption"
}

resource "aws_kms_alias" "ap" {
  provider      = aws.ap
  name          = "alias/data-residency-ap"
  target_key_id = aws_kms_key.ap.key_id
}

resource "aws_s3_bucket" "eu" {
  provider = aws.eu
  bucket   = "data-residency-eu-${random_id.eu.hex}"
  force_destroy = true

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.eu.arn
        sse_algorithm     = "aws:kms"
      }
    }
  }
}

resource "aws_s3_bucket" "ap" {
  provider = aws.ap
  bucket   = "data-residency-ap-${random_id.ap.hex}"
  force_destroy = true

  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.ap.arn
        sse_algorithm     = "aws:kms"
      }
    }
  }
}

resource "random_id" "eu" {
  byte_length = 4
}

resource "random_id" "ap" {
  byte_length = 4
}

locals {
  deny_policy_eu = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Deny"
      Principal = "*"
      Action = "s3:PutObject"
      Resource = "${aws_s3_bucket.eu.arn}/*"
      Condition = {
        StringNotEquals = {
          "aws:RequestTag/region" = "EU"
        }
      }
    }]
  })

  deny_policy_ap = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Deny"
      Principal = "*"
      Action = "s3:PutObject"
      Resource = "${aws_s3_bucket.ap.arn}/*"
      Condition = {
        StringNotEquals = {
          "aws:RequestTag/region" = "APAC"
        }
      }
    }]
  })
}

resource "aws_s3_bucket_policy" "eu" {
  provider = aws.eu
  bucket   = aws_s3_bucket.eu.id
  policy   = local.deny_policy_eu
}

resource "aws_s3_bucket_policy" "ap" {
  provider = aws.ap
  bucket   = aws_s3_bucket.ap.id
  policy   = local.deny_policy_ap
}

output "eu_bucket_arn" {
  value = aws_s3_bucket.eu.arn
}

output "ap_bucket_arn" {
  value = aws_s3_bucket.ap.arn
}

output "eu_kms_key_id" {
  value = aws_kms_key.eu.key_id
}

output "ap_kms_key_id" {
  value = aws_kms_key.ap.key_id
}
