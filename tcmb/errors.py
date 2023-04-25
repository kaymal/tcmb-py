"""Errors module."""


class ApiKeyError(ValueError):
    """Raise for API Key error."""

    def __init__(self, msg="Check API key!", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)


class InvalidSeriesCode(ValueError):
    """Raise for Invalid Series Code error."""

    def __init__(
        self,
        msg=(
            "Invalid series code! "
            "One of the series codes is not valid, "
            "or there are too many codes."
        ),
        *args,
        **kwargs
    ):
        super().__init__(msg, *args, **kwargs)
