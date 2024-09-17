from celery import Celery
from django.conf import settings

sqs_queue_url = settings.SQS_QUEUE_URL
aws_access_key = settings.AWS_ACCESS_KEY
aws_secret_key = settings.AWS_SECRET_KEY

app = Celery(
    "app",
    broker_url=f"sqs://{aws_access_key}:{aws_secret_key}@",
    broker_transport_options={
        "region": "us-east-1", # your AWS SQS region
        "predefined_queues": {
            "celery": {  ## the name of the SQS queue
                "url": sqs_queue_url,
                "access_key_id": aws_access_key,
                "secret_access_key": aws_secret_key,
            }
        },
    },
    task_create_missing_queues=False,
)
