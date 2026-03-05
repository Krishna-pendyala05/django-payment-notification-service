resource "aws_sqs_queue" "payment_notifications_dlq" {
  name = "${var.project_name}-dlq"
}

resource "aws_sqs_queue" "payment_notifications" {
  name                      = var.project_name
  delay_seconds             = 0
  max_message_size          = 2048
  message_retention_seconds = 86400
  receive_wait_time_seconds = 10
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.payment_notifications_dlq.arn
    maxReceiveCount     = 3
  })
}

output "sqs_queue_url" {
  value = aws_sqs_queue.payment_notifications.url
}

output "sqs_queue_arn" {
  value = aws_sqs_queue.payment_notifications.arn
}
