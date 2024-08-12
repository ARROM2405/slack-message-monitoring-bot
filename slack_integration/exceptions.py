class FailDeleteMessageException(Exception):
    def __init__(self):
        self.message = "Failed to delete slack message."
        super().__init__(self.message)


class FailPostMessageException(Exception):
    def __init__(self):
        self.message = "Failed to post slack message."
        super().__init__(self.message)
