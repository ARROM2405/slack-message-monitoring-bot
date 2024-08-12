import json
import os
from unittest import mock

import pytest
from dotenv import load_dotenv
from precisely import assert_that, is_mapping
from rest_framework import status

from data_loss_prevention_tool import Manager, PATTERNS

load_dotenv(".env")


def test_pattern_update_create():
    manager = Manager("test_queue")

    pattern_id = "test_id"
    pattern_value = "test_pattern"
    action = "create"

    manager._pattern_update(
        pattern_id,
        action,
        pattern_value,
    )
    assert PATTERNS[pattern_id] == pattern_value


def test_pattern_update_update():
    manager = Manager("test_queue")

    pattern_id = "test_id"
    pattern_value = "test_pattern"
    action = "update"

    manager._pattern_update(
        pattern_id,
        action,
        pattern_value,
    )
    assert PATTERNS[pattern_id] == pattern_value


def test_pattern_update_delete():

    manager = Manager("test_queue")

    pattern_id = "test_id"
    action = "delete"

    PATTERNS[pattern_id] = "some_pattern"

    manager._pattern_update(pattern_id, action)
    assert pattern_id not in PATTERNS


@pytest.mark.asyncio
async def test_get_messages_with_pattern_updates():
    with mock.patch("data_loss_prevention_tool.boto3.client") as mock_client:
        receipt_handle = "AQEBJqaPR+IpSojYX"
        mock_sqs_client = mock.MagicMock()
        mock_sqs_client.receive_message.return_value = {
            "Messages": [
                {
                    "Body": '{"task": "pattern_update", "kwargs": {"action": '
                    '"create", "instance_id": 1, "pattern": "test_pattern"}}',
                    "MD5OfBody": "9e5d737f5314604d1289065815e068c0",
                    "MessageId": "629ba4cd-a796-44db-ba4c-2740f8402f08",
                    "ReceiptHandle": receipt_handle,
                }
            ],
            "ResponseMetadata": {
                "HTTPHeaders": {
                    "connection": "keep-alive",
                    "content-length": "643",
                    "content-type": "application/x-amz-json-1.0",
                    "date": "Mon, 12 Aug 2024 16:54:07 GMT",
                    "x-amzn-requestid": "b594e2d6-5c87-549a-b95e-bde21ce87e14",
                },
                "HTTPStatusCode": 200,
                "RequestId": "b594e2d6-5c87-549a-b95e-bde21ce87e14",
                "RetryAttempts": 0,
            },
        }
        mock_client.return_value = mock_sqs_client

        manager = Manager(queue_name="test_queue")
        messages = await manager._get_messages_with_pattern_updates()

        assert_that(
            json.loads(messages[0]["Body"]),
            is_mapping(
                {
                    "task": "pattern_update",
                    "kwargs": is_mapping(
                        {
                            "action": "create",
                            "instance_id": 1,
                            "pattern": "test_pattern",
                        }
                    ),
                }
            ),
        )

        assert_that(
            mock_sqs_client.delete_message.call_args_list[0].kwargs,
            is_mapping(
                {
                    "QueueUrl": os.getenv("NEW_PATTERNS_QUEUE_URL"),
                    "ReceiptHandle": receipt_handle,
                }
            ),
        )


@pytest.mark.asyncio
async def test_get_user_messages_for_check():
    with mock.patch("data_loss_prevention_tool.boto3.client") as mock_client:
        receipt_handle = "AQEBJqaPR+IpSojYX"
        mock_sqs_client = mock.MagicMock()
        mock_sqs_client.receive_message.return_value = {
            "Messages": [
                {
                    "Body": '{"task": "user_message_check", "kwargs": '
                    '{"message_uuid": "uuid_1", "text": "test_text", '
                    '"file_download_url": "test_url"}}',
                    "MD5OfBody": "caed187e77798e9e5bccc04cbae3e59c",
                    "MessageId": "d2f42057-2082-4489-9c0e-9a16205e299f",
                    "ReceiptHandle": receipt_handle,
                }
            ],
            "ResponseMetadata": {
                "HTTPHeaders": {
                    "connection": "keep-alive",
                    "content-length": "695",
                    "content-type": "application/x-amz-json-1.0",
                    "date": "Mon, 12 Aug 2024 17:23:06 GMT",
                    "x-amzn-requestid": "123d24b8-7164-5785-84b6-7b8c365e0174",
                },
                "HTTPStatusCode": 200,
                "RequestId": "123d24b8-7164-5785-84b6-7b8c365e0174",
                "RetryAttempts": 0,
            },
        }
        mock_client.return_value = mock_sqs_client

        manager = Manager(queue_name="test_queue")
        messages = await manager._get_user_messages_for_check()

        assert_that(
            json.loads(messages[0]["Body"]),
            is_mapping(
                {
                    "task": "user_message_check",
                    "kwargs": is_mapping(
                        {
                            "message_uuid": "uuid_1",
                            "text": "test_text",
                            "file_download_url": "test_url",
                        }
                    ),
                }
            ),
        )
        assert_that(
            mock_sqs_client.delete_message.call_args_list[0].kwargs,
            is_mapping(
                {
                    "QueueUrl": os.getenv("MESSAGE_CHECK_QUEUE_URL"),
                    "ReceiptHandle": receipt_handle,
                }
            ),
        )


def test_get_user_messages_for_check_no_file_passed():
    with mock.patch("data_loss_prevention_tool.requests.get") as mock_get, mock.patch(
        "data_loss_prevention_tool.requests.post"
    ) as mock_post:
        PATTERNS[1] = "(?:\d[ -]*?){13,19}"
        manager = Manager(queue_name="test_queue")
        manager._user_message_check(
            message_uuid="123", text="some text", file_download_url=""
        )
        mock_get.assert_not_called()
        mock_post.assert_not_called()


def test_get_user_messages_for_check_no_file_data_loss():
    with mock.patch("data_loss_prevention_tool.requests.get") as mock_get, mock.patch(
        "data_loss_prevention_tool.requests.post"
    ) as mock_post:
        PATTERNS[1] = "(?:\d[ -]*?){13,19}"
        PATTERNS[2] = "(?:\d[ -]*?){13,15}"
        manager = Manager(queue_name="test_queue")
        manager._user_message_check(
            message_uuid="123", text="12345678901234", file_download_url=""
        )
        mock_get.assert_not_called()
        mock_post.assert_called_once_with(
            os.getenv("DATA_LOSS_POSITIVE_MESSAGES_ENDPOINT"),
            json={
                "message_uuid": "123",
                "failed_patterns": [1, 2],
            },
        )


def test_get_user_messages_for_check_with_file_passed():
    with mock.patch("data_loss_prevention_tool.requests.get") as mock_get, mock.patch(
        "data_loss_prevention_tool.requests.post"
    ) as mock_post:

        mock_file_response = mock.MagicMock()
        mock_file_response.content = b"asd"
        mock_get.return_value = mock_file_response

        PATTERNS[1] = "(?:\d[ -]*?){13,19}"
        PATTERNS[2] = "(?:\d[ -]*?){13,15}"
        manager = Manager(queue_name="test_queue")
        manager._user_message_check(
            message_uuid="123", text="some text", file_download_url="some_url"
        )
        mock_get.assert_called_once_with(
            "some_url", headers={"Authorization": f"Bearer {os.getenv('BOT_TOKEN')}"}
        )
        mock_post.assert_not_called()


def test_get_user_messages_for_check_with_file_data_loss():
    with mock.patch("data_loss_prevention_tool.requests.get") as mock_get, mock.patch(
        "data_loss_prevention_tool.requests.post"
    ) as mock_post:
        mock_file_response = mock.MagicMock()
        mock_file_response.content = b"12345678901234"
        mock_file_response.status_code = status.HTTP_200_OK
        mock_get.return_value = mock_file_response

        PATTERNS[1] = "(?:\d[ -]*?){13,19}"
        PATTERNS[2] = "(?:\d[ -]*?){13,15}"
        manager = Manager(queue_name="test_queue")
        manager._user_message_check(
            message_uuid="123", text="some text", file_download_url="some_url"
        )
        mock_get.assert_called_once_with(
            "some_url", headers={"Authorization": f"Bearer {os.getenv('BOT_TOKEN')}"}
        )
        mock_post.assert_called_once_with(
            os.getenv("DATA_LOSS_POSITIVE_MESSAGES_ENDPOINT"),
            json={
                "message_uuid": "123",
                "failed_patterns": [1, 2],
            },
        )
