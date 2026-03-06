# AWS EC2 Deployment Guide

This guide describes how to deploy the Django Async Payment Notification Service to an AWS EC2 instance (Free Tier eligible).

## Prerequisites

1. **AWS CLI** configured on your local machine.
2. **Terraform** installed.
3. EC2 Instance (t2.micro, free-tier eligible) with **Docker** and **Docker Compose** installed.

## Infrastructure Setup

1. Navigate to the `terraform/` directory.
2. Run `terraform init`.
3. Run `terraform apply`. Note the outputs (RDS Endpoint, SQS URL, IAM Keys).

## Deployment Steps

1. SSH into your EC2 Instance.
2. Clone the repository.
3. Create a `.env` file with the following values (using the Terraform outputs):
   ```
   DEBUG=False
   SECRET_KEY=your-production-secret-key
   DATABASE_URL=postgres://django_admin:your-db-password@your-rds-endpoint:5432/payment_db
   AWS_ACCESS_KEY_ID=your-app-user-access-key
   AWS_SECRET_ACCESS_KEY=your-app-user-secret-key
   AWS_REGION=us-east-1
   SQS_QUEUE_NAME=django-payment-service
   SQS_DEAD_LETTER_QUEUE_NAME=django-payment-service-dlq
   ALLOWED_HOSTS=your-ec2-public-ip,your-domain.com
   ```
4. Start the services:
   ```bash
   docker-compose up -d --build
   ```

## Scaling and Maintenance

- The Celery worker can be scaled by running more containers or increasing EC2 instance size.
- RDS handles database backups and maintenance automatically.
