from unittest import mock
from django.test import TestCase
from rest_framework.reverse import reverse


class TestApi(TestCase):
    def setUp(self):
        self.webhook_url = reverse("slack_integration:slack-webhook")
        self.data_loss_positive_message_url = reverse(
            "slack_integration:slack-data-loss-positive-message"
        )

    def test_webhook_url_verification(self):
        pass
