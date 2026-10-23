"""Errors the CLI turns into a non-zero exit code."""


class UsageError(Exception):
    """The command was called in a way we can explain. Exit 2."""


class SourceError(Exception):
    """A public source could not be read or understood. Exit 1."""


class HttpError(Exception):
    """An HTTP response we will not treat as data."""

    def __init__(self, status: int, url: str, detail: str = "") -> None:
        self.status = status
        self.url = url
        clean = " ".join(detail.split())[:300]
        message = f"HTTP {status} for {url}"
        if clean:
            message = f"{message}: {clean}"
        super().__init__(message)
