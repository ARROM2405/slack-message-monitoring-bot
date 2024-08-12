import json
import os
import uuid
from abc import ABC

import boto3
import redis
from django.conf import settings
from dotenv import load_dotenv
from rest_framework import status
from rest_framework.response import Response
from typing import TypeVar, Generic

from slack_integration.types import (
    UrlVerificationRequestData,
    EventCallbackRequestData,
)

load_dotenv(os.path.join(settings.BASE_DIR, ".env"))
redis_client = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"))

RequestData = TypeVar("RequestData")


class RequestServiceBase(ABC, Generic[RequestData]):
    def __init__(self, request_data: RequestData):
        self.request_data = request_data

    def process_request(self): ...

    def prepare_response(self) -> Response: ...


class UrlVerificationRequestService(RequestServiceBase[UrlVerificationRequestData]):
    def process_request(self):
        pass

    def prepare_response(self) -> Response:
        return Response(
            status=status.HTTP_200_OK,
            data={"challenge": self.request_data.get("challenge")},
        )


class EventCallbackRequestService(RequestServiceBase[EventCallbackRequestData]):
    def _add_message_uuid(self):
        self.request_data["uuid"] = str(uuid.UUID())

    def _save_message_to_memory(self):
        event = self.request_data["event"]
        redis_client.hset(
            self.request_data["uuid"],
            mapping={
                "user_id": event["user"],
                "text": event["text"],
                "ts": event["ts"],
                "channel": event["channel"],
                "file_download_link": (
                    event["files"][0]["url_private_download"]
                    if event.get("files")
                    else ""
                ),
            },
        )

    def _send_data_to_queue(self):
        sqs = boto3.client("sqs")
        message_body = {
            "task": "user_message_check",
            "kwargs": {
                "message_uuid": self.request_data["uuid"],
                "text": self.request_data["event"]["text"],
                "file_download_url": (
                    self.request_data["event"]["files"][0]["url_private_download"]
                    if self.request_data["event"].get("files")
                    else ""
                ),
            },
        }
        sqs.send_message(
            QueueUrl=os.getenv("MESSAGE_CHECK_QUEUE_URL"),
            MessageBody=json.dumps(message_body),
        )

    def process_request(self):
        self._add_message_uuid()
        self._save_message_to_memory()
        self._send_data_to_queue()

    def prepare_response(self) -> Response:
        return Response(status=status.HTTP_200_OK)
