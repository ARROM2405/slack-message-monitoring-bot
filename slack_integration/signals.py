import json
import os

import boto3
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from dotenv import load_dotenv

from avanan_home_assignment import settings
from slack_integration.models import DataSecurityPattern

load_dotenv(os.path.join(settings.BASE_DIR, ".env"))


sqs = boto3.client("sqs")
sqs_queue_url = os.getenv("NEW_PATTERNS_QUEUE_URL")


@receiver(post_save, sender=DataSecurityPattern)
def send_message_on_save(sender, instance, **kwargs):
    action = "created" if kwargs.get("created", False) else "updated"
    message = {
        "task": "pattern_update",
        "kwargs": {
            "action": action,
            "instance_id": instance.id,
            "pattern": instance.pattern,
        },
    }
    sqs.send_message(QueueUrl=sqs_queue_url, MessageBody=json.dumps(message))


@receiver(post_delete, sender=DataSecurityPattern)
def send_message_on_save(sender, instance, **kwargs):
    message = {
        "task": "pattern_update",
        "kwargs": {
            "action": "delete",
            "instance_id": instance.id,
        },
    }
    sqs.send_message(QueueUrl=sqs_queue_url, MessageBody=json.dumps(message))
