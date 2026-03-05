resource "aws_iam_user" "app_user" {
  name = "${var.project_name}-app-user"
}

resource "aws_iam_access_key" "app_user_key" {
  user = aws_iam_user.app_user.name
}

resource "aws_iam_user_policy" "app_user_policy" {
  name = "${var.project_name}-policy"
  user = aws_iam_user.app_user.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "sqs:SendMessage",
          "sqs:ReceiveMessage",
          "sqs:DeleteMessage",
          "sqs:GetQueueAttributes",
        ]
        Effect   = "Allow"
        Resource = "*" # Restrict to specific ARNs in production
      },
      {
        Action = [
          "cloudwatch:PutMetricData",
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

output "app_user_access_key" {
  value = aws_iam_access_key.app_user_key.id
}

output "app_user_secret_key" {
  value     = aws_iam_access_key.app_user_key.secret
  sensitive = true
}
