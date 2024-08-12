import os
import uuid
from unittest import mock

from django.test import TestCase
from django_extensions.settings import BASE_DIR
from dotenv import load_dotenv
from precisely import assert_that, has_attrs, contains_exactly
from rest_framework import status

from slack_integration.exceptions import (
    FailDeleteMessageException,
    FailPostMessageException,
)
from slack_integration.models import DataLossMessage
from slack_integration.services.data_loss_positive_message_service import (
    DataLossMessagePositiveService,
)
from slack_integration.tests.factories import (
    DataSecurityPatternFactory,
    DataLossMessageFactory,
)

load_dotenv(os.path.join(BASE_DIR, ".env"))


class TestDataLossPositiveSavedMessage(TestCase):
    @mock.patch(
        "slack_integration.services.data_loss_positive_message_service.redis.Redis.delete"
    )
    @mock.patch(
        "slack_integration.services.data_loss_positive_message_service.redis.Redis.hgetall"
    )
    def test_get_message_from_memory(self, mock_redis_hgetall, mock_redis_delete):

        message_uuid = str(uuid.uuid4())
        user_id = "some_user_id"
        text = "some_text"
        ts = "123"
        channel = "456"
        file_download_link = "some_url"
        mock_redis_hgetall.return_value = {
            b"user_id": user_id.encode("utf-8"),
            b"text": text.encode("utf-8"),
            b"ts": ts.encode("utf-8"),
            b"channel": channel.encode("utf-8"),
            b"file_download_link": file_download_link.encode("utf-8"),
        }

        message = DataLossMessagePositiveService._get_message_from_memory(message_uuid)
        mock_redis_hgetall.assert_called_once_with(message_uuid)
        mock_redis_delete.assert_called_once_with(message_uuid)
        assert_that(
            message,
            has_attrs(
                user_id=user_id,
                text=text,
                ts=ts,
                channel=channel,
            ),
        )

    def test_save_message_to_db(self):
        message = DataLossMessage(
            user_id="some_user_id",
            text="some_text",
            ts="123",
            channel="456",
            file_download_link="some_url",
        )
        pattern_1 = DataSecurityPatternFactory()
        pattern_2 = DataSecurityPatternFactory()

        assert not DataLossMessage.objects.exists()
        DataLossMessagePositiveService._save_message_to_db(
            message,
            [pattern_1, pattern_2],
        )
        saved_message = DataLossMessage.objects.get()
        assert_that(
            list(saved_message.failed_security_patterns.all()),
            contains_exactly(pattern_1, pattern_2),
        )

    @mock.patch(
        "slack_integration.services.data_loss_positive_message_service.requests.post"
    )
    def test_delete_message_from_slack_ok(self, mock_post):
        response_mock = mock.MagicMock()
        response_mock.status_code = status.HTTP_200_OK
        mock_post.return_value = response_mock

        message = DataLossMessageFactory()
        DataLossMessagePositiveService._delete_message_from_slack(message)

        mock_post.assert_called_once_with(
            os.getenv("DELETE_MESSAGE_URL"),
            headers={
                "Authorization": f"Bearer {os.getenv('USER_TOKEN')}",
                "Content-Type": "application/json",
            },
            json={"channel": message.channel, "ts": message.ts},
        )

    @mock.patch(
        "slack_integration.services.data_loss_positive_message_service.requests.post"
    )
    def test_delete_message_from_slack_failed(self, mock_post):
        response_mock = mock.MagicMock()
        response_mock.status_code = status.HTTP_400_BAD_REQUEST
        mock_post.return_value = response_mock

        message = DataLossMessageFactory()
        with self.assertRaises(FailDeleteMessageException):
            DataLossMessagePositiveService._delete_message_from_slack(message)

    @mock.patch(
        "slack_integration.services.data_loss_positive_message_service.requests.post"
    )
    def test_inform_in_slack_ok(self, mock_post):
        response_mock = mock.MagicMock()
        response_mock.status_code = status.HTTP_200_OK
        mock_post.return_value = response_mock

        pattern = DataSecurityPatternFactory()
        service = DataLossMessagePositiveService("123", [pattern])
        service._inform_in_slack("345")

        mock_post.assert_called_once_with(
            os.getenv("POST_MESSAGE_URL"),
            headers={
                "Authorization": f"Bearer {os.getenv('BOT_TOKEN')}",
                "Content-Type": "application/json",
            },
            json={
                "channel": "345",
                "text": f"Deleted message due to the failed patterns: {pattern.name}.",
            },
        )

    @mock.patch(
        "slack_integration.services.data_loss_positive_message_service.requests.post"
    )
    def test_inform_in_slack_failed(self, mock_post):
        response_mock = mock.MagicMock()
        response_mock.status_code = status.HTTP_400_BAD_REQUEST
        mock_post.return_value = response_mock

        with self.assertRaises(FailPostMessageException):
            service = DataLossMessagePositiveService(
                "123", [DataSecurityPatternFactory()]
            )
            service._inform_in_slack("345")

    @mock.patch(
        "slack_integration.services.data_loss_positive_message_service.DataLossMessagePositiveService._inform_in_slack"
    )
    @mock.patch(
        "slack_integration.services.data_loss_positive_message_service.DataLossMessagePositiveService._delete_message_from_slack"
    )
    @mock.patch(
        "slack_integration.services.data_loss_positive_message_service.DataLossMessagePositiveService._save_message_to_db"
    )
    @mock.patch(
        "slack_integration.services.data_loss_positive_message_service.DataLossMessagePositiveService._get_message_from_memory"
    )
    def test_process(
        self,
        mock_get_message_from_memory,
        mock_save_message_to_db,
        mock_delete_message_from_slack,
        mock_inform_in_slack,
    ):
        pattern = DataSecurityPatternFactory()
        mock_message = mock.MagicMock()
        mock_message.channel = "345"
        mock_get_message_from_memory.return_value = mock_message
        service = DataLossMessagePositiveService(
            message_uuid="123",
            failed_patterns=[pattern],
        )
        service.process()

        mock_get_message_from_memory.assert_called_once_with("123")
        mock_save_message_to_db.assert_called_once_with(mock_message, [pattern])
        mock_delete_message_from_slack.assert_called_once_with(mock_message)
        mock_inform_in_slack.assert_called_once_with("345")
