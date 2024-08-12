from rest_framework import serializers

from slack_integration.models import DataSecurityPattern


class PostedFileSerializer(serializers.Serializer):
    url_private_download = serializers.URLField()


class EventSerializer(serializers.Serializer):
    user = serializers.CharField()
    type = serializers.CharField()
    client_msg_id = serializers.CharField()
    text = serializers.CharField(allow_null=True, allow_blank=True)
    ts = serializers.CharField()
    channel = serializers.CharField()
    files = PostedFileSerializer(required=False, many=True)


class SlackRequestSerializer(serializers.Serializer):
    token = serializers.CharField(required=False, allow_blank=True)
    challenge = serializers.CharField(required=False, allow_blank=True)
    type = serializers.CharField(required=False, allow_blank=True)
    event = EventSerializer(required=False)


class DataLossPositiveMessageSerializer(serializers.Serializer):
    message_uuid = serializers.CharField()
    failed_patterns = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(
            queryset=DataSecurityPattern.objects.all()
        )
    )
