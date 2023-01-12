"""Errors module."""


class ApiKeyError(ValueError):
    """Raise for API Key error."""

    def __init__(self, msg="Check API key!", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)
