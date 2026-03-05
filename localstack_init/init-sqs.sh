#!/bin/bash
awslocal sqs create-queue --queue-name payment-notifications
awslocal sqs create-queue --queue-name payment-notifications-dlq
echo "Queues created successfully"
