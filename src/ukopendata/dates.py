"""Date helpers shared by the sources. No third-party date library."""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone


def parse_iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value.strip())
    except ValueError as exc:
        raise ValueError(f"expected a date as YYYY-MM-DD, got {value!r}") from exc


def parse_flexible_date(value: str) -> str:
    """Return YYYY-MM-DD from an ISO timestamp or a UK dd/mm/yyyy date."""
    text = value.strip()
    if not text:
        return ""
    if len(text) >= 10 and text[4] == "-" and text[7] == "-":
        return text[:10]
    for fmt in ("%d/%m/%Y", "%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            continue
    dotnet = re.search(r"/Date\((-?\d+)", text)
    if dotnet:
        millis = int(dotnet.group(1))
        return datetime.fromtimestamp(millis / 1000, tz=timezone.utc).date().isoformat()
    return text


def months_before(day: date, months: int) -> date:
    """The same day of the month, ``months`` earlier, clipped to the month length."""
    year = day.year
    month = day.month - months
    while month <= 0:
        month += 12
        year -= 1
    # Day 31 in a 30-day month, and February, clip rather than overflow.
    last = _last_day(year, month)
    return date(year, month, min(day.day, last))


def _last_day(year: int, month: int) -> int:
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    return (next_month - timedelta(days=1)).day
