from typing import TypedDict


class PostedFile(TypedDict, total=False):
    url_private_download: str


class Event(TypedDict, total=False):
    user: str
    type: str
    client_msg_id: str
    text: str
    ts: str
    channel: str
    files: list[PostedFile]


class EventCallbackRequestData(TypedDict, total=False):
    token: str
    type: str
    event: Event
    uuid: str


class UrlVerificationRequestData(TypedDict):
    token: str
    challenge: str
    type: str


class DataLossPositiveSavedMessage(TypedDict):
    user_id: str
    text: str
    ts: str
    channel: str
    file_download_link: str
