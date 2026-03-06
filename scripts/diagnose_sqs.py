import boto3
import os
import environ
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

def test_sqs():
    sqs = boto3.resource(
        'sqs',
        region_name=env('AWS_REGION'),
        aws_access_key_id=env('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=env('AWS_SECRET_ACCESS_KEY')
    )
    queue_name = env('SQS_QUEUE_NAME')
    print(f"Testing queue: {queue_name} in {env('AWS_REGION')}")
    
    try:
        queue = sqs.get_queue_by_name(QueueName=queue_name)
        print(f"Success! Queue URL: {queue.url}")
        print(f"Queue ARN: {queue.attributes.get('QueueArn')}")
        print(f"Messages in queue: {queue.attributes.get('ApproximateNumberOfMessages')}")
        print(f"Messages not visible (in flight): {queue.attributes.get('ApproximateNumberOfMessagesNotVisible')}")
        
        # response = queue.send_message(MessageBody='test-connection')
        # print(f"Test message sent: {response.get('MessageId')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_sqs()
