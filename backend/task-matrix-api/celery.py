import os

from celery import Celery
from django.conf import settings

sqs_queue_url = settings.SQS_QUEUE_URL
aws_access_key = settings.AWS_ACCESS_KEY
aws_secret_key = settings.AWS_SECRET_KEY

app = Celery(
    "task-matrix-api",
    broker_url="sqs:",
    broker_transport_options={
        "region": "eu-north-1", # your AWS SQS region
        "predefined_queues": {
            "Celery": {  # the name of the SQS queue
                "url": sqs_queue_url,
                "access_key_id": aws_access_key,
                "secret_access_key": aws_secret_key,
            }
        },
    },
    task_create_missing_queues=False,
)

# for TEST mode
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'task-matrix-api.settings')
#app = Celery("task-matrix-api",)
#app.config_from_object('django.conf:settings', namespace='CELERY')
#app.autodiscover_tasks()
