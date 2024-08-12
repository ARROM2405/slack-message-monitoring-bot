from enum import IntEnum


class SlackRequestType(IntEnum):
    URL_VERIFICATION = 1
    EVENT_CALLBACK = 2

    @classmethod
    def from_payload_value(cls, payload_value):
        if payload_value == "url_verification":
            return cls.URL_VERIFICATION
        elif payload_value == "event_callback":
            return cls.EVENT_CALLBACK
        raise NotImplementedError
