import json
import os
from unittest import mock

from django.test import TestCase
from django_extensions.settings import BASE_DIR
from dotenv import load_dotenv
from precisely import assert_that, is_mapping

from slack_integration.models import DataSecurityPattern

load_dotenv(os.path.join(BASE_DIR, ".env"))


class TestSignals(TestCase):

    @mock.patch("slack_integration.signals.boto3.client")
    def test_create(self, mock_client):
        mock_sqs_client = mock.MagicMock()
        mock_client.return_value = mock_sqs_client

        pattern = DataSecurityPattern.objects.create(
            name="test_name",
            pattern="test_pattern",
        )
        message = {
            "task": "pattern_update",
            "kwargs": {
                "action": "create",
                "pattern_id": pattern.id,
                "pattern": pattern.pattern,
            },
        }

        mock_sqs_client.send_message.assert_called_once_with(
            QueueUrl=os.getenv("NEW_PATTERNS_QUEUE_URL"),
            MessageBody=json.dumps(message),
        )

    @mock.patch("slack_integration.signals.boto3.client")
    def test_update(self, mock_client):
        mock_sqs_client = mock.MagicMock()
        mock_client.return_value = mock_sqs_client

        pattern = DataSecurityPattern.objects.create(
            name="test_name",
            pattern="test_pattern",
        )

        pattern.pattern = "pattern_updated"
        pattern.save()

        assert mock_sqs_client.send_message.call_args_list[1].kwargs[
            "QueueUrl"
        ] == os.getenv("NEW_PATTERNS_QUEUE_URL")
        assert_that(
            json.loads(
                mock_sqs_client.send_message.call_args_list[1].kwargs["MessageBody"]
            ),
            is_mapping(
                {
                    "task": "pattern_update",
                    "kwargs": is_mapping(
                        {
                            "action": "update",
                            "pattern_id": pattern.id,
                            "pattern": "pattern_updated",
                        }
                    ),
                }
            ),
        )

    @mock.patch("slack_integration.signals.boto3.client")
    def test_delete(self, mock_client):
        mock_sqs_client = mock.MagicMock()
        mock_client.return_value = mock_sqs_client

        pattern = DataSecurityPattern.objects.create(
            name="test_name",
            pattern="test_pattern",
        )

        DataSecurityPattern.objects.filter(id=pattern.id).delete()

        assert mock_sqs_client.send_message.call_args_list[1].kwargs[
            "QueueUrl"
        ] == os.getenv("NEW_PATTERNS_QUEUE_URL")
        assert_that(
            json.loads(
                mock_sqs_client.send_message.call_args_list[1].kwargs["MessageBody"]
            ),
            is_mapping(
                {
                    "task": "pattern_update",
                    "kwargs": is_mapping(
                        {
                            "action": "delete",
                            "pattern_id": pattern.id,
                        }
                    ),
                }
            ),
        )
