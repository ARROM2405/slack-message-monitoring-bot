import os

import redis
import requests
from rest_framework import status

from slack_integration.exceptions import (
    FailDeleteMessageException,
    FailPostMessageException,
)
from slack_integration.models import DataSecurityPattern, DataLossMessage
from slack_integration.types import DataLossPositiveSavedMessage

redis_client = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"))


class DataLossMessagePositiveService:
    def __init__(self, message_uuid: str, failed_patterns: list[DataSecurityPattern]):
        self.message_uuid = message_uuid
        self.failed_patterns = failed_patterns

    @staticmethod
    def _get_message_from_memory(message_uuid: str) -> DataLossMessage:
        message: DataLossPositiveSavedMessage = redis_client.hgetall(message_uuid)
        redis_client.delete(message_uuid)
        return DataLossMessage(
            user_id=message["user_id"],
            text=message["text"],
            ts=message["ts"],
            channel=message["channel"],
        )

    @staticmethod
    def _save_message_to_db(
        message: DataLossMessage, failed_patterns: list[DataSecurityPattern]
    ):
        failed_patterns_ids = [pattern.id for pattern in failed_patterns]
        message.failed_security_patterns.add(*failed_patterns_ids)
        message.save()

    @staticmethod
    def _delete_message_from_slack(message: DataLossMessage):
        delete_message_url = os.getenv("DELETE_MESSAGE_URL")
        user_token = os.getenv("USER_TOKEN")
        headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json",
        }
        payload = {"channel": message.channel, "ts": message.ts}
        response = requests.post(
            delete_message_url,
            headers=headers,
            json=payload,
        )
        if response.status_code != status.HTTP_200_OK:
            raise FailDeleteMessageException

    def _inform_in_slack(self, channel: str):
        post_message_url = os.getenv("POST_MESSAGE_URL")
        bot_token = os.getenv("BOT_TOKEN")
        headers = {
            "Authorization": f"Bearer {bot_token}",
            "Content-Type": "application/json",
        }
        failed_pattern_names = ", ".join(
            [pattern.name for pattern in self.failed_patterns]
        )
        text = f"Deleted message due to the failed patterns: {failed_pattern_names}"
        payload = {"channel": channel, "text": text}
        response = requests.post(
            post_message_url,
            headers=headers,
            json=payload,
        )
        if response.status_code != status.HTTP_200_OK:
            raise FailPostMessageException

    def process(self):
        message = self._get_message_from_memory(self.message_uuid)
        self._save_message_to_db(message, self.failed_patterns)
        self._delete_message_from_slack(message)
        self._inform_in_slack(message.channel)
