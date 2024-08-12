from unittest import mock

from django.test import TestCase
from precisely import has_attrs, assert_that
from rest_framework import status

from slack_integration.handlers import RequestHandler
from slack_integration.services.slack_events_services import (
    UrlVerificationRequestService,
    EventCallBackRequestService,
)


class TestRequestHandler(TestCase):
    def test_get_service(self):
        url_verification_serialized_data = {"type": "url_verification"}
        handler = RequestHandler(url_verification_serialized_data)
        assert isinstance(handler._get_service(), UrlVerificationRequestService)

        event_serialized_data = {"type": "event_callback"}
        handler = RequestHandler(event_serialized_data)
        assert isinstance(handler._get_service(), EventCallBackRequestService)

    @mock.patch(
        "slack_integration.handlers.EventCallBackRequestService.process_request"
    )
    def test_handle_exception_raised_by_the_service(self, mock_service_process):
        mock_service_process.side_effect = Exception
        event_serialized_data = {"type": "event_callback"}
        handler = RequestHandler(event_serialized_data)
        assert_that(handler.handle(), has_attrs(status_code=status.HTTP_200_OK))
