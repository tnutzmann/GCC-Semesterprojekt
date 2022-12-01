terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

#TODO: AMI ROLE

locals {
  my_aws_access_key = ""
  my_aws_secret_key = ""
  my_aws_token      = ""
  my_aws_ssh_key    = "Mac-Key"

  myBucket = "tonys-bottletube-bucket"

  server_ami_ID    = "ami-0184316ae54baeb2a"
  server_iam_role  = "LabInstanceProfile"
  server_sec_group = ["sg-0a763b59f550d1d80"]
}

provider "aws" {
  region     = "us-east-1"
  access_key = local.my_aws_access_key
  secret_key = local.my_aws_secret_key
  token      = local.my_aws_token
}

# erstellt einen S3 Bucket
resource "aws_s3_bucket" "bottletube_bucket" {
  bucket        = local.myBucket
  force_destroy = true
}

# setzt die ACL des Buckets auf 'public read'
resource "aws_s3_bucket_acl" "bottletube_bucket_acl" {
  bucket = aws_s3_bucket.bottletube_bucket.id
  acl    = "public-read"
}

# Lädt alles hoch was in images liegt
resource "aws_s3_object" "assets_upload" {
  for_each = fileset("../images/", "**")

  bucket       = local.myBucket
  key          = "user_uploads/${each.value}"
  source       = "../images/${each.value}"
  content_type = "image/jpg"
  etag         = filemd5("../images/${each.value}")

  acl = "public-read"

  depends_on = [
    aws_s3_bucket.bottletube_bucket
  ]
}

# EC2 Instanz erstellen (SERVER)
resource "aws_instance" "bottletube_ec2" {
  ami                    = local.server_ami_ID
  instance_type          = "t3.nano"
  iam_instance_profile   = local.server_iam_role
  key_name               = local.my_aws_ssh_key
  vpc_security_group_ids = local.server_sec_group
  monitoring             = false
}

/*
# Datenbank erstllen (POSTGRESQL)
resource "aws_db_instance" "bottletube_db" {
  allocated_storage      = 20
  db_name                = "bottletube_db"
  engine                 = "postgres"
  instance_class         = "db.t3.micro"
  username               = local.my_db_user
  password               = local.my_db_user_passwd
  publicly_accessible    = true
  skip_final_snapshot    = true
  vpc_security_group_ids = [local.db_sec_group]
}
*/
