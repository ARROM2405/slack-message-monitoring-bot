import copy
import json
import os
from unittest import mock

from django.test import TestCase
from dotenv import load_dotenv
from precisely import assert_that, is_mapping
from rest_framework import status

from avanan_home_assignment.settings import BASE_DIR
from slack_integration.serializers import SlackRequestSerializer
from slack_integration.services.slack_events_services import (
    UrlVerificationRequestService,
    EventCallBackRequestService,
)
from slack_integration.tests.incoming_requests_examples import (
    USER_MESSAGE_WITHOUT_FILE,
    USER_MESSAGE_WITH_FILE,
)

load_dotenv(os.path.join(BASE_DIR, ".env"))


class TestUrlVerificationRequestService(TestCase):
    def test_prepare_response(self):
        challenge_value = "123123"
        service = UrlVerificationRequestService({"challenge": challenge_value})
        response = service.prepare_response()
        assert response.status_code == status.HTTP_200_OK
        assert response.data["challenge"] == challenge_value


class TestEventCallbackRequestService(TestCase):
    def setUp(self):
        self.request_data_message_without_file = copy.deepcopy(
            USER_MESSAGE_WITHOUT_FILE
        )
        self.request_data_message_with_file = copy.deepcopy(USER_MESSAGE_WITH_FILE)

    def _get_serialized_request_data(self, request_data: dict) -> dict:
        return SlackRequestSerializer(request_data).data

    @mock.patch("slack_integration.services.slack_events_services.redis.Redis.hset")
    def test_save_message_without_file_to_memory(self, mock_redis_hset):
        serialized_request_data = self._get_serialized_request_data(
            self.request_data_message_without_file
        )
        service = EventCallBackRequestService(serialized_request_data)
        service._add_message_uuid()
        service._save_message_to_memory()
        assert mock_redis_hset.call_args_list[0].args[0] == service.request_data["uuid"]
        assert_that(
            mock_redis_hset.call_args_list[0].kwargs["mapping"],
            is_mapping(
                {
                    "user_id": self.request_data_message_without_file["event"]["user"],
                    "text": self.request_data_message_without_file["event"]["text"],
                    "ts": self.request_data_message_without_file["event"]["ts"],
                    "channel": self.request_data_message_without_file["event"][
                        "channel"
                    ],
                    "file_download_link": "",
                }
            ),
        )

    @mock.patch("slack_integration.services.slack_events_services.redis.Redis.hset")
    def test_save_message_with_file_to_memory(self, mock_redis_hset):
        serialized_request_data = self._get_serialized_request_data(
            self.request_data_message_with_file
        )
        service = EventCallBackRequestService(serialized_request_data)
        service._add_message_uuid()
        service._save_message_to_memory()
        assert mock_redis_hset.call_args_list[0].args[0] == service.request_data["uuid"]
        assert_that(
            mock_redis_hset.call_args_list[0].kwargs["mapping"],
            is_mapping(
                {
                    "user_id": self.request_data_message_with_file["event"]["user"],
                    "text": self.request_data_message_with_file["event"]["text"],
                    "ts": self.request_data_message_with_file["event"]["ts"],
                    "channel": self.request_data_message_with_file["event"]["channel"],
                    "file_download_link": self.request_data_message_with_file["event"][
                        "files"
                    ][0]["url_private_download"],
                }
            ),
        )

    @mock.patch("slack_integration.services.slack_events_services.boto3.client")
    def test_send_data_to_queue_no_file(self, boto3_client):
        mock_client = mock.MagicMock()
        boto3_client.return_value = mock_client
        serialized_request_data = self._get_serialized_request_data(
            self.request_data_message_without_file
        )
        service = EventCallBackRequestService(serialized_request_data)
        service._add_message_uuid()
        service._send_data_to_queue()
        assert mock_client.send_message.call_args_list[0].kwargs[
            "QueueUrl"
        ] == os.getenv("MESSAGE_CHECK_QUEUE_URL")
        assert_that(
            json.loads(
                mock_client.send_message.call_args_list[0].kwargs["MessageBody"]
            ),
            is_mapping(
                {
                    "task": "user_message_check",
                    "kwargs": is_mapping(
                        {
                            "message_uuid": service.request_data["uuid"],
                            "text": service.request_data["event"]["text"],
                            "file_download_url": "",
                        }
                    ),
                }
            ),
        )

    @mock.patch("slack_integration.services.slack_events_services.boto3.client")
    def test_send_data_to_queue_with_file(self, boto3_client):
        mock_client = mock.MagicMock()
        boto3_client.return_value = mock_client
        serialized_request_data = self._get_serialized_request_data(
            self.request_data_message_with_file
        )
        service = EventCallBackRequestService(serialized_request_data)
        service._add_message_uuid()
        service._send_data_to_queue()
        assert mock_client.send_message.call_args_list[0].kwargs[
            "QueueUrl"
        ] == os.getenv("MESSAGE_CHECK_QUEUE_URL")
        assert_that(
            json.loads(
                mock_client.send_message.call_args_list[0].kwargs["MessageBody"]
            ),
            is_mapping(
                {
                    "task": "user_message_check",
                    "kwargs": is_mapping(
                        {
                            "message_uuid": service.request_data["uuid"],
                            "text": service.request_data["event"]["text"],
                            "file_download_url": service.request_data["event"]["files"][
                                0
                            ]["url_private_download"],
                        }
                    ),
                }
            ),
        )

    @mock.patch(
        "slack_integration.services.slack_events_services.EventCallBackRequestService._send_data_to_queue"
    )
    @mock.patch(
        "slack_integration.services.slack_events_services.EventCallBackRequestService._save_message_to_memory"
    )
    @mock.patch(
        "slack_integration.services.slack_events_services.EventCallBackRequestService._add_message_uuid"
    )
    def test_process_request(
        self,
        mock_add_message_uuid,
        mock_save_message_to_memory,
        mock_send_data_to_queue,
    ):
        serialized_request_data = self._get_serialized_request_data(
            self.request_data_message_with_file
        )
        service = EventCallBackRequestService(serialized_request_data)
        service.process_request()

        mock_add_message_uuid.assert_called_once()
        mock_save_message_to_memory.assert_called_once()
        mock_send_data_to_queue.assert_called_once()

    def test_prepare_response(self):
        response = EventCallBackRequestService({}).prepare_response()
        assert response.status_code == status.HTTP_200_OK
