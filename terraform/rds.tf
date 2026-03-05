resource "aws_db_instance" "default" {
  allocated_storage    = 20
  db_name              = "payment_db"
  engine               = "postgres"
  engine_version       = "15"
  instance_class       = "db.t3.micro"
  username             = "django_admin"
  password             = "change-me-in-production" # Should be handled via secrets manager
  parameter_group_name = "default.postgres15"
  skip_final_snapshot  = true
  publicly_accessible  = true # For dev purposes if not in VPC, ideally false
}

output "db_endpoint" {
  value = aws_db_instance.default.endpoint
}
