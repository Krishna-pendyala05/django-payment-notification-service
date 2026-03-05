# Dedicated RDS security group — allows port 5432 only from the EC2 security group
resource "aws_security_group" "rds_sg" {
  name        = "${var.project_name}-rds-sg"
  description = "Allow PostgreSQL access from EC2 app servers only"
  vpc_id      = aws_security_group.app_sg.vpc_id

  ingress {
    description     = "PostgreSQL from EC2 app SG"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-rds-sg"
  }
}

resource "aws_db_instance" "default" {
  allocated_storage      = 20
  db_name                = "payment_db"
  engine                 = "postgres"
  engine_version         = "15"
  instance_class         = "db.t3.micro"
  username               = "django_admin"
  password               = "change-me-in-production"
  parameter_group_name   = "default.postgres15"
  skip_final_snapshot    = true
  publicly_accessible    = true
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
}

output "db_endpoint" {
  value = aws_db_instance.default.endpoint
}

output "rds_sg_id" {
  value = aws_security_group.rds_sg.id
}
