"""Weekly road fuel prices from the Department for Energy Security and Net Zero.

The statistics page is read through the GOV.UK content API, which lists the
current CSV attachment. The asset id changes when the file is updated, so
the command does not hard-code it.

https://www.gov.uk/api/content/government/statistics/weekly-road-fuel-prices
https://www.gov.uk/government/statistics/weekly-road-fuel-prices

Accredited official statistics, Open Government Licence v3.0.
gov.uk robots.txt allows this path. It disallows /search and print views,
which this command does not use.
"""

from __future__ import annotations

import csv
import io

from ukopendata.dates import parse_flexible_date
from ukopendata.errors import SourceError, UsageError

CONTENT_URL = "https://www.gov.uk/api/content/government/statistics/weekly-road-fuel-prices"
PAGE_URL = "https://www.gov.uk/government/statistics/weekly-road-fuel-prices"

COLUMNS = [
    "date",
    "petrol_ppl",
    "diesel_ppl",
    "petrol_duty_ppl",
    "diesel_duty_ppl",
    "petrol_vat_pct",
    "diesel_vat_pct",
]


def fetch_latest(client, *, weeks: int) -> list[dict]:
    if weeks < 1 or weeks > 104:
        raise UsageError("--weeks must be between 1 and 104.")
    document = client.get_json(CONTENT_URL, headers={"Accept": "application/json"})
    if not isinstance(document, dict):
        raise SourceError("The GOV.UK content API did not return the fuel-price publication.")
    url = csv_attachment_url(document)
    body = client.get(url, timeout=60)
    rows = parse_fuel_csv(body)
    return rows[-weeks:]


def csv_attachment_url(document: dict) -> str:
    attachments = (document.get("details") or {}).get("attachments") or []
    csvs = []
    for attachment in attachments:
        if not isinstance(attachment, dict):
            continue
        title = attachment.get("title") or ""
        filename = attachment.get("filename") or ""
        content_type = attachment.get("content_type") or ""
        url = attachment.get("url") or ""
        looks_like_csv = "csv" in content_type or filename.lower().endswith(".csv") or "CSV" in title
        if looks_like_csv and url:
            csvs.append(attachment)
    current = [item for item in csvs if "2018" in (item.get("title") or "")]
    chosen = current[0] if current else (csvs[0] if csvs else None)
    if chosen is None:
        raise SourceError(f"No CSV attachment was listed for weekly road fuel prices. See {PAGE_URL}")
    # Prefer the series that runs from 2018, not the closed 2003–2017 file.
    if not current and len(csvs) > 1:
        raise SourceError("The fuel-price publication did not label a current CSV series.")
    return str(chosen["url"])


def parse_fuel_csv(body: bytes) -> list[dict]:
    text = body.decode("utf-8-sig", "replace")
    reader = csv.reader(io.StringIO(text))
    header: list[str] | None = None
    rows: list[dict] = []
    for record in reader:
        if not any(cell.strip() for cell in record):
            continue
        joined = " ".join(record).casefold()
        if header is None:
            if "date" in joined and "ulsp" in joined:
                header = record
            continue
        if len(record) < 7:
            continue
        raw_date = record[0].strip()
        # Notes under the table are not part of the series.
        if not raw_date[:1].isdigit():
            break
        date_text = parse_flexible_date(raw_date)
        rows.append(
            {
                "date": date_text,
                "petrol_ppl": _number(record[1]),
                "diesel_ppl": _number(record[2]),
                "petrol_duty_ppl": _number(record[3]),
                "diesel_duty_ppl": _number(record[4]),
                "petrol_vat_pct": _number(record[5]),
                "diesel_vat_pct": _number(record[6]),
            }
        )
    if not rows:
        raise SourceError("The road fuel prices CSV had no data rows.")
    return rows


def _number(value: str) -> float | int | str:
    text = value.strip()
    if not text:
        return ""
    try:
        number = float(text)
    except ValueError:
        return text
    if number.is_integer():
        return int(number)
    return number
