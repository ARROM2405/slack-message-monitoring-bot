from typing import TypeVar

from rest_framework import status
from rest_framework.response import Response

from slack_integration.enums import SlackRequestType
from slack_integration.services.slack_events_services import (
    RequestServiceBase,
    UrlVerificationRequestService,
    EventCallBackRequestService,
)

RequestService = TypeVar("RequestService", bound=RequestServiceBase)


class RequestHandler:
    def __init__(self, request_data: dict):
        self.request_data = request_data

    def _get_service(self) -> RequestService:
        request_type = SlackRequestType.from_payload_value(self.request_data["type"])
        if request_type is SlackRequestType.URL_VERIFICATION:
            return UrlVerificationRequestService(self.request_data)
        elif request_type is SlackRequestType.EVENT_CALLBACK:
            return EventCallBackRequestService(self.request_data)
        raise NotImplementedError

    def handle(self):
        try:
            service = self._get_service()
            service.process_request()
            response = service.prepare_response()
        except Exception:
            response = Response(status=status.HTTP_200_OK)
        return response
