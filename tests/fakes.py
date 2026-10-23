"""In-memory HTTP stand-ins. They do not open sockets."""

from __future__ import annotations

import json
from pathlib import Path


class FakeClient:
    def __init__(self, handler):
        self.handler = handler
        self.calls: list[tuple] = []

    def get(self, url, headers=None, timeout=30):
        self.calls.append(("GET", url, headers))
        return self.handler("GET", url, None, headers)

    def get_json(self, url, headers=None, timeout=45):
        self.calls.append(("GET", url, headers))
        return self.handler("GET", url, None, headers)

    def post_json(self, url, payload, headers=None, timeout=45):
        self.calls.append(("POST", url, payload, headers))
        return self.handler("POST", url, payload, headers)

    def head(self, url, timeout=30):
        self.calls.append(("HEAD", url, None))
        return self.handler("HEAD", url, None, None)

    def download(self, url, dest: Path, timeout=300):
        self.calls.append(("DOWNLOAD", url, str(dest)))
        body = self.handler("DOWNLOAD", url, None, None)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(body)


class MemoryResponse:
    def __init__(self, body: bytes, headers: dict | None = None):
        self._body = body
        self.headers = headers or {}
        self.status = 200

    def read(self, size=-1):
        if size is None or size < 0:
            chunk, self._body = self._body, b""
            return chunk
        chunk, self._body = self._body[:size], self._body[size:]
        return chunk

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class FakeOpener:
    def __init__(self, body: bytes, status: int = 200, headers: dict | None = None):
        self.body = body
        self.status = status
        self.headers = headers or {}
        self.requests = []

    def open(self, request, timeout=None):
        self.requests.append(request)
        if self.status >= 400:
            import io
            import urllib.error
            from email.message import Message

            raise urllib.error.HTTPError(
                request.full_url,
                self.status,
                "error",
                Message(),
                io.BytesIO(self.body),
            )
        return MemoryResponse(self.body, self.headers)


def json_bytes(payload: dict) -> bytes:
    return json.dumps(payload).encode("utf-8")
