resource "aws_db_subnet_group" "managrdb" {
  name       = "managrdb"
  subnet_ids = aws_subnet.private.*.id

  tags = {
    "app" = "managr"
  }
}

resource "aws_db_instance" "managrdb" {
  for_each                   = { for e in var.environments : e.name => e }
  identifier                 = "${each.value.rds_db_name}-${each.value.name}"
  allocated_storage          = 20
  engine                     = "postgres"
  engine_version             = "12.5"
  instance_class             = "db.t2.medium"
  name                       = each.value.rds_db_name
  username                   = each.value.rds_username
  password                   = each.value.rds_password
  storage_type               = "gp2"
  skip_final_snapshot        = true
  port                       = 5432
  db_subnet_group_name       = aws_db_subnet_group.managrdb.id
  vpc_security_group_ids     = [aws_security_group.managr_db.id]
  publicly_accessible        = false
  auto_minor_version_upgrade = true
  snapshot_identifier        = each.value.rds_db_snapshot_id


  tags = {
    "app" = "managr"
  }
}
