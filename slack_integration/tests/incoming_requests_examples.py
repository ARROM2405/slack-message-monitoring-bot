URL_VERIFICATION_REQUEST = {
    "token": "sroNKIgJkrBiHa7dLYrp0dau",
    "challenge": "pjdJW953u1cPqniMmS24fh0qvYsArRfLdJKe3hcxY5QkQCuGniL8",
    "type": "url_verification",
}


USER_MESSAGE_WITHOUT_FILE = {
    "token": "sroNKIgJkrBiHa7dLYrp0dau",
    "team_id": "T07GHF9FK8C",
    "context_team_id": "T07GHF9FK8C",
    "context_enterprise_id": None,
    "api_app_id": "A07G0LGBB63",
    "event": {
        "user": "U07G8BPDWDU",
        "type": "message",
        "ts": "1723396328.920629",
        "client_msg_id": "f158f5af-2b8c-4bc4-97bb-489a51550939",
        "text": "a",
        "team": "T07GHF9FK8C",
        "blocks": [
            {
                "type": "rich_text",
                "block_id": "9gSJ+",
                "elements": [
                    {
                        "type": "rich_text_section",
                        "elements": [{"type": "text", "text": "a"}],
                    }
                ],
            }
        ],
        "channel": "C07H3Q77RUG",
        "event_ts": "1723396328.920629",
        "channel_type": "channel",
    },
    "type": "event_callback",
    "event_id": "Ev07H44EE50Q",
    "event_time": 1723396328,
    "authorizations": [
        {
            "enterprise_id": None,
            "team_id": "T07GHF9FK8C",
            "user_id": "U07GF7D4ZT4",
            "is_bot": True,
            "is_enterprise_install": False,
        }
    ],
    "is_ext_shared_channel": False,
    "event_context": "4-eyJldCI6Im1lc3NhZ2UiLCJ0aWQiOiJUMDdHSEY5Rks4QyIsImFpZCI6IkEwN0cwTEdCQjYzIiwiY2lkIjoiQzA3SDNRNzdSVUcifQ",
}


USER_MESSAGE_WITH_FILE = {
    "token": "sroNKIgJkrBiHa7dLYrp0dau",
    "team_id": "T07GHF9FK8C",
    "context_team_id": "T07GHF9FK8C",
    "context_enterprise_id": None,
    "api_app_id": "A07G0LGBB63",
    "event": {
        "text": "",
        "files": [
            {
                "id": "F07GFAY40BC",
                "created": 1723397228,
                "timestamp": 1723397228,
                "name": "file.txt",
                "title": "file.txt",
                "mimetype": "text/plain",
                "filetype": "text",
                "pretty_type": "Plain Text",
                "user": "U07G8BPDWDU",
                "user_team": "T07GHF9FK8C",
                "editable": True,
                "size": 3,
                "mode": "snippet",
                "is_external": False,
                "external_type": "",
                "is_public": True,
                "public_url_shared": False,
                "display_as_bot": False,
                "username": "",
                "url_private": "https://test-lxi4231.slack.com/files/U07G8BPDWDU/F07GFAY40BC/file.txt/edit",
                "url_private_download": "https://files.slack.com/files-pri/T07GHF9FK8C-F07GFAY40BC/download/file.txt",
                "permalink": "https://test-lxi4231.slack.com/files/U07G8BPDWDU/F07GFAY40BC/file.txt",
                "permalink_public": "https://slack-files.com/T07GHF9FK8C-F07GFAY40BC-fa27d8f4f4",
                "edit_link": "https://test-lxi4231.slack.com/files/U07G8BPDWDU/F07GFAY40BC/file.txt/edit",
                "preview": "asd",
                "preview_highlight": '<div class="CodeMirror cm-s-default CodeMirrorServer">\n<div class="CodeMirror-code">\n<div><pre>asd</pre></div>\n</div>\n</div>\n',
                "lines": 1,
                "lines_more": 0,
                "preview_is_truncated": False,
                "has_rich_preview": False,
                "file_access": "visible",
            }
        ],
        "upload": False,
        "user": "U07G8BPDWDU",
        "display_as_bot": False,
        "type": "message",
        "ts": "1723397230.991799",
        "client_msg_id": "f513275d-96b4-47ce-b8d6-5e9c4ae69f7b",
        "channel": "C07H3Q77RUG",
        "subtype": "file_share",
        "event_ts": "1723397230.991799",
        "channel_type": "channel",
    },
    "type": "event_callback",
    "event_id": "Ev07GHRETRFW",
    "event_time": 1723397230,
    "authorizations": [
        {
            "enterprise_id": None,
            "team_id": "T07GHF9FK8C",
            "user_id": "U07GF7D4ZT4",
            "is_bot": True,
            "is_enterprise_install": False,
        }
    ],
    "is_ext_shared_channel": False,
    "event_context": "4-eyJldCI6Im1lc3NhZ2UiLCJ0aWQiOiJUMDdHSEY5Rks4QyIsImFpZCI6IkEwN0cwTEdCQjYzIiwiY2lkIjoiQzA3SDNRNzdSVUcifQ",
}
