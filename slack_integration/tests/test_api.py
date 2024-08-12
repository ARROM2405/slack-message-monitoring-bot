import copy
from unittest import mock
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse

from slack_integration.models import DataSecurityPattern
from slack_integration.tests.factories import DataSecurityPatternFactory
from slack_integration.tests.incoming_requests_examples import (
    URL_VERIFICATION_REQUEST,
)


class TestApi(TestCase):
    def setUp(self):
        self.webhook_url = reverse("slack_integration:slack-webhook")
        self.data_loss_positive_message_url = reverse(
            "slack_integration:slack-data-loss-positive-message"
        )

    def test_webhook_url_verification(self):
        challenge_value = "some_value"
        request_body = copy.copy(URL_VERIFICATION_REQUEST)
        request_body["challenge"] = challenge_value
        response = self.client.post(path=self.webhook_url, data=request_body)
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["challenge"] == challenge_value

    @mock.patch("slack_integration.api.DataLossMessagePositiveService")
    def test_data_loss_positive_message(self, mock_service):
        mock_service_instance = mock.MagicMock()
        mock_service.return_value = mock_service_instance
        pattern_1 = DataSecurityPatternFactory()
        pattern_2 = DataSecurityPatternFactory()

        payload = {
            "message_uuid": "123123",
            "failed_patterns": [pattern_1.id, pattern_2.id],
        }
        response = self.client.post(
            path=self.data_loss_positive_message_url, data=payload
        )
        assert response.status_code == status.HTTP_200_OK
        mock_service.assert_called_once_with(
            message_uuid="123123",
            failed_patterns=list(DataSecurityPattern.objects.all()),
        )
        mock_service_instance.process.assert_called_once()
