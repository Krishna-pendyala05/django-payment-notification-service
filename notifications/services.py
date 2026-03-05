import boto3
from abc import ABC, abstractmethod
from django.conf import settings
from botocore.exceptions import ClientError
import structlog

logger = structlog.get_logger(__name__)

class QueuePublisher(ABC):
    @abstractmethod
    def publish(self, message: str):
        pass

class SQSPublisher(QueuePublisher):
    def __init__(self):
        self.sqs = boto3.resource(
            'sqs',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.SQS_ENDPOINT_URL
        )
        self.queue_name = settings.SQS_QUEUE_NAME
        self._queue = None

    @property
    def queue(self):
        if not self._queue:
            try:
                self._queue = self.sqs.get_queue_by_name(QueueName=self.queue_name)
            except ClientError as e:
                if e.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
                    # In local development with LocalStack, we might want to create the queue if it doesn't exist
                    logger.info("Queue not found, creating it...", queue_name=self.queue_name)
                    self._queue = self.sqs.create_queue(QueueName=self.queue_name)
                else:
                    logger.error("Failed to get SQS queue", error=str(e))
                    raise
        return self._queue

    def publish(self, message: str):
        try:
            response = self.queue.send_message(MessageBody=message)
            logger.info("Message published to SQS", message_id=response.get('MessageId'))
            return response
        except Exception as e:
            logger.error("Failed to publish message to SQS", error=str(e))
            raise
