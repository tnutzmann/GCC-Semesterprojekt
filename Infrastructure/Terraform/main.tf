terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

locals {
  myBucket = "tonys-bottletube-bucket"
  my_aws_access_key = ""
  my_aws_secret_key = ""
  my_aws_token = ""
  my_aws_ssh_key = ""

  server_ami_ID = ""
  server_sec_group = [""]
  server_subnet_id = ""
}

provider "aws" {
  region     = "us-east-1"
  access_key = local.my_aws_access_key
  secret_key = local.my_aws_secret_key
  token      = local.my_aws_token
}

# erstellt einen S3 Bucket
resource "aws_s3_bucket" "bottletube_bucket" {
  bucket = local.myBucket
}

# setzt die ACL des Buckets auf 'public read'
resource "aws_s3_bucket_acl" "bottletube_bucket_acl" {
  bucket = aws_s3_bucket.bottletube_bucket.id
  acl    = "public-read"
}

# Lädt alles hoch was in assets liegt
resource "aws_s3_object" "assets_upload" {
  for_each = fileset("../images/", "**")

  bucket       = local.myBucket
  key          = "images/${each.value}"
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
  key_name               = local.my_aws_ssh_key
  vpc_security_group_ids = local.server_sec_group
  subnet_id              = local.server_subnet_id
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