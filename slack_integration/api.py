from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from slack_integration.handlers import RequestHandler
from slack_integration.serializers import (
    SlackRequestSerializer,
    DataLossPositiveMessageSerializer,
)
from slack_integration.services.data_loss_positive_message_service import (
    DataLossMessagePositiveService,
)


class SlackViewSet(GenericViewSet):

    def get_serializer_class(self):
        if self.action == "webhook":
            return SlackRequestSerializer
        elif self.action == "data_loss_positive_message":
            return DataLossPositiveMessageSerializer
        raise NotImplementedError

    @action(methods=["POST"], detail=False)
    def webhook(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        handler = RequestHandler(serializer.validated_data)
        response = handler.handle()
        return response

    @action(methods=["POST"], detail=False)
    def data_loss_positive_message(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = DataLossMessagePositiveService(**serializer.validated_data)
        service.process()
        return Response(status=status.HTTP_200_OK)
