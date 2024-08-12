import os
import re

import boto3
import requests
from dotenv import load_dotenv

import asyncio
import json


load_dotenv(".env")
sqs = boto3.client("sqs")

PATTERNS = {}


class Manager:

    def __init__(self, queue_name: str):
        self.loop = asyncio.get_event_loop()
        self.queue = queue_name
        self.tasks = {
            "user_message_check": Manager._user_message_check,
            "pattern_update": Manager._pattern_update,
        }

    @staticmethod
    async def _pattern_update(pattern_id: str, pattern: str, action: str):

        print(f"{action} task")
        if action == "delete":
            if pattern_id in PATTERNS:
                PATTERNS.pop(pattern_id)
        else:
            PATTERNS[pattern_id] = pattern
        print(PATTERNS)

    @staticmethod
    async def _user_message_check(message_uuid: str, text: str, file_download_url: str):
        failed_pattern_ids = {}

        bot_token = os.getenv("BOT_TOKEN")
        file_content = ""
        response = requests.get(
            file_download_url, headers={"Authorization": f"Bearer {bot_token}"}
        )
        if response.status_code == 200:
            file_content = response.content.decode("utf-8")

        for pattern_id in PATTERNS:
            pattern = re.compile(PATTERNS[pattern_id])
            if pattern.search(text):
                failed_pattern_ids.update({pattern_id})
            if pattern.search(file_content):
                failed_pattern_ids.update({pattern_id})

        if failed_pattern_ids:
            url = os.getenv("DATA_LOSS_POSITIVE_MESSAGES_ENDPOINT")
            requests.post(
                url,
                json=json.dumps(
                    {
                        "message_uuid": message_uuid,
                        "failed_patterns": failed_pattern_ids,
                    }
                ),
            )

    async def _get_messages_with_pattern_updates(self):
        """Read and pop messages with patterns update from SQS queue"""
        queue_url = os.getenv("NEW_PATTERNS_QUEUE_URL")
        patterns_message = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
        )

        messages = patterns_message.get("Messages", [])
        if messages:
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=messages[0]["ReceiptHandle"],
            )
        return messages

    async def _get_messages_for_check(self):
        """Read and pop messages with for data loss validation from SQS queue"""
        queue_url = os.getenv("MESSAGE_CHECK_QUEUE_URL")
        patterns_message = sqs.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
        )
        messages = patterns_message.get("Messages", [])
        if messages:
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=messages[0]["ReceiptHandle"],
            )
        return messages

    async def main(self):
        while True:
            patterns_messages = await self._get_messages_with_pattern_updates()
            messages = patterns_messages or await self._get_messages_for_check()
            for message in messages:
                body = json.loads(message["Body"])
                print(body)

                task_name = body.get("task")
                kwargs = body.get("kwargs", {})

                task = self.tasks.get(task_name)
                self.loop.create_task(task(**kwargs))
            await asyncio.sleep(1)


if __name__ == "__main__":
    manager = Manager("queue_name")
    asyncio.run(manager.main())
