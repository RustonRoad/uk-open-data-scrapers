"""FCA aggregated net short positions, current daily file.

The FCA publishes this CSV each working day. It is already one row per
issuer: individual position holders are not disclosed.

https://www.fca.org.uk/markets/short-selling/notification-disclosure-net-short-positions
https://www.fca.org.uk/publication/documents/aggregated-current-net-short-positions.csv

The file path has no query string. The FCA robots.txt disallows crawling
URLs that contain a query string; this direct file does not.
"""

from __future__ import annotations

import csv
import io

from ukopendata.dates import parse_flexible_date
from ukopendata.errors import SourceError, UsageError

CSV_URL = "https://www.fca.org.uk/publication/documents/aggregated-current-net-short-positions.csv"
PAGE_URL = "https://www.fca.org.uk/markets/short-selling/notification-disclosure-net-short-positions"

COLUMNS = ["rank", "issuer", "isin", "net_short_pct", "position_date"]


def fetch_top(client, *, top: int) -> list[dict]:
    if top < 1 or top > 500:
        raise UsageError("--top must be between 1 and 500.")
    body = client.get(CSV_URL, timeout=60)
    return top_positions(parse_positions(body), top)


def parse_positions(body: bytes) -> list[dict]:
    text = body.decode("utf-8-sig", "replace")
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise SourceError("The FCA short-positions file had no header row.")
    fields = {_normalise(name): name for name in reader.fieldnames}
    issuer_key = _pick(fields, "name of company", "issuer", "name")
    isin_key = _pick(fields, "international securities identification number (isin)", "isin")
    pct_key = _pick(fields, "aggregated net short position (%)", "net short position (%)", "net short")
    date_key = _pick(fields, "position date (of latest position date notified)", "position date")
    if not all([issuer_key, isin_key, pct_key]):
        raise SourceError(
            "The FCA short-positions file did not have the expected columns: "
            + ", ".join(reader.fieldnames)
        )
    rows = []
    for record in reader:
        issuer = (record.get(issuer_key) or "").strip()
        if not issuer:
            continue
        rows.append(
            {
                "issuer": issuer,
                "isin": (record.get(isin_key) or "").strip(),
                "net_short_pct": _percent(record.get(pct_key) or ""),
                "position_date": parse_flexible_date(record.get(date_key) or "") if date_key else "",
            }
        )
    return rows


def top_positions(rows: list[dict], top: int) -> list[dict]:
    ordered = sorted(rows, key=lambda row: (row["net_short_pct"] is None, -(row["net_short_pct"] or 0)))
    chosen = []
    for index, row in enumerate(ordered[:top], start=1):
        chosen.append({"rank": index, **row})
    return chosen


def _normalise(name: str) -> str:
    return " ".join(name.replace("\ufeff", "").strip().casefold().split())


def _pick(fields: dict[str, str], *candidates: str) -> str | None:
    for candidate in candidates:
        if candidate in fields:
            return fields[candidate]
    for candidate in candidates:
        for key, original in fields.items():
            if candidate in key:
                return original
    return None


def _percent(value: str) -> float | None:
    text = value.strip().replace("%", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None
