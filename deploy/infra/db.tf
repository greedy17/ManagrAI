resource "aws_db_subnet_group" "managrdb" {
  name       = "managrdb"
  subnet_ids = aws_subnet.private.*.id

  tags = {
    "app" = "managr"
  }
}

resource "aws_db_instance" "managrdb" {
  identifier                 = var.rds_db_name
  allocated_storage          = 20
  engine                     = "postgres"
  engine_version             = "12.5"
  instance_class             = "db.t2.micro"
  name                       = var.rds_db_name
  username                   = var.rds_username
  password                   = var.rds_password
  storage_type               = "gp2"
  skip_final_snapshot        = true
  port                       = 5432
  db_subnet_group_name       = aws_db_subnet_group.managrdb.id
  vpc_security_group_ids     = [aws_security_group.managr_db.id]
  publicly_accessible        = false
  auto_minor_version_upgrade = true

  tags = {
    "app" = "managr"
  }
}

resource "aws_secretsmanager_secret" "managrdb_user" {
  name                    = "managrdbuser"
  recovery_window_in_days = 0

  tags = {
    "app" = "managr"
  }
}

resource "aws_secretsmanager_secret_version" "managrdb_user" {
  secret_id     = aws_secretsmanager_secret.managrdb_user.id
  secret_string = var.rds_username
}

resource "aws_secretsmanager_secret" "managrdb_pass" {
  name                    = "managrdbpass"
  recovery_window_in_days = 0

  tags = {
    "app" = "managr"
  }
}

resource "aws_secretsmanager_secret_version" "managrdb_pass" {
  secret_id     = aws_secretsmanager_secret.managrdb_pass.id
  secret_string = var.rds_password
}

resource "aws_secretsmanager_secret" "managrdb_host" {
  name                    = "managrdbhost"
  recovery_window_in_days = 0

  tags = {
    "app" = "managr"
  }
}

resource "aws_secretsmanager_secret_version" "managrdb_host" {
  secret_id     = aws_secretsmanager_secret.managrdb_host.id
  secret_string = aws_db_instance.managrdb.address
}

resource "aws_secretsmanager_secret" "managrdb_name" {
  name                    = "managrdbname"
  recovery_window_in_days = 0

  tags = {
    "app" = "managr"
  }
}

resource "aws_secretsmanager_secret_version" "managrdb_name" {
  secret_id     = aws_secretsmanager_secret.managrdb_name.id
  secret_string = var.rds_db_name
}
