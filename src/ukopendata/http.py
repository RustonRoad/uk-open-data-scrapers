"""A small HTTP client. No telemetry, no extra headers, no retries that hide rate limits."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable

from ukopendata.errors import HttpError

Log = Callable[[str], None]


class HttpClient:
    """Polite client with a minimum gap between requests on this instance.

    SEC EDGAR asks for at most 10 requests per second. Pass ``min_interval``
    of 0.15 (about 6 per second) for that host and stay under the cap even
    if a command pages.
    """

    def __init__(
        self,
        user_agent: str,
        *,
        min_interval: float = 0.0,
        opener: urllib.request.OpenerDirector | None = None,
        sleep: Callable[[float], None] = time.sleep,
        now: Callable[[], float] = time.monotonic,
        log: Log | None = None,
    ) -> None:
        self.user_agent = user_agent
        self.min_interval = min_interval
        self._opener = opener or urllib.request.build_opener()
        self._sleep = sleep
        self._now = now
        self._log = log
        self._last: float | None = None

    def _pace(self) -> None:
        now = self._now()
        if self.min_interval > 0 and self._last is not None:
            elapsed = now - self._last
            if elapsed < self.min_interval:
                self._sleep(self.min_interval - elapsed)
                now = self._now()
        self._last = now

    def _open(
        self,
        url: str,
        *,
        data: bytes | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 30,
        method: str | None = None,
    ):
        self._pace()
        hdrs = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/csv, text/plain, */*",
        }
        if headers:
            hdrs.update(headers)
        request = urllib.request.Request(url, data=data, headers=hdrs, method=method)
        try:
            return self._opener.open(request, timeout=timeout)
        except urllib.error.HTTPError as exc:
            detail = exc.read(500).decode("utf-8", "replace")
            raise HttpError(exc.code, url, detail) from None

    @staticmethod
    def _header_map(headers) -> dict[str, str]:
        return {key.lower(): value for key, value in headers.items()}

    def get(self, url: str, *, headers: dict[str, str] | None = None, timeout: float = 30) -> bytes:
        with self._open(url, headers=headers, timeout=timeout) as response:
            return response.read()

    def get_json(self, url: str, *, headers: dict[str, str] | None = None, timeout: float = 45) -> object:
        body = self.get(url, headers=headers, timeout=timeout)
        return _load_json(body, url)

    def post_json(
        self,
        url: str,
        payload: dict,
        *,
        headers: dict[str, str] | None = None,
        timeout: float = 45,
    ) -> object:
        data = json.dumps(payload).encode("utf-8")
        hdrs = {"Content-Type": "application/json", "Accept": "application/json"}
        if headers:
            hdrs.update(headers)
        with self._open(url, data=data, headers=hdrs, timeout=timeout, method="POST") as response:
            return _load_json(response.read(), url)

    def head(self, url: str, *, timeout: float = 30) -> dict[str, str]:
        with self._open(url, timeout=timeout, method="HEAD") as response:
            return self._header_map(response.headers)

    def download(self, url: str, dest: Path, *, timeout: float = 180) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        temporary = dest.with_suffix(dest.suffix + ".part")
        with self._open(url, timeout=timeout) as response:
            total = int(response.headers.get("Content-Length") or 0)
            written = 0
            next_mark = 5 * 1024 * 1024
            with temporary.open("wb") as handle:
                while True:
                    chunk = response.read(256 * 1024)
                    if not chunk:
                        break
                    handle.write(chunk)
                    written += len(chunk)
                    if self._log and total and written >= next_mark:
                        self._log(
                            f"Downloading {dest.name}: {written // (1024 * 1024)} / "
                            f"{total // (1024 * 1024)} MB"
                        )
                        next_mark += 5 * 1024 * 1024
        if total and written != total:
            temporary.unlink(missing_ok=True)
            raise HttpError(200, url, f"download stopped at {written} of {total} bytes")
        temporary.replace(dest)


def _load_json(body: bytes, url: str) -> object:
    try:
        return json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HttpError(200, url, f"response was not JSON ({exc})") from None
