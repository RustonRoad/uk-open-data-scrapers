"""HM Land Registry Price Paid, from the official yearly bulk CSVs.

The yearly files use the same columns as the monthly CSV. The monthly file
is a change file (additions, changes and deletions), so a median for an area
is computed from the yearly file, which lists the transactions received that
year. Pass ``--file`` to read a CSV you already have.

https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads
https://price-paid-data.publicdata.landregistry.gov.uk/pp-{year}.csv

The linked-data API on landregistry.data.gov.uk is not used: its robots.txt
disallows /data and /sparql.

Required attribution, as published by HM Land Registry:

Contains HM Land Registry data © Crown copyright and database right 2021.
This data is licensed under the Open Government Licence v3.0.

Price Paid Data includes Royal Mail PAF address data and Ordnance Survey
address data. Royal Mail and Ordnance Survey allow that address data for
personal and/or non-commercial use, and to display it so you can provide
residential property price information. Any other use of the address data
needs permission from Royal Mail: address.management@royalmail.com.
"""

from __future__ import annotations

import csv
import json
import os
import statistics
from datetime import date
from pathlib import Path

from ukopendata.dates import months_before
from ukopendata.errors import SourceError, UsageError

YEAR_URL = "https://price-paid-data.publicdata.landregistry.gov.uk/pp-{year}.csv"
DOWNLOADS_PAGE = "https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads"

ATTRIBUTION = (
    "Contains HM Land Registry data © Crown copyright and database right 2021. "
    "This data is licensed under the Open Government Licence v3.0."
)
ADDRESS_NOTE = (
    "Address fields include Royal Mail PAF and Ordnance Survey data. "
    "Personal/non-commercial use, and display for residential price information, "
    "is permitted. Other address use needs Royal Mail's permission "
    "(address.management@royalmail.com)."
)

PROPERTY_TYPES = {
    "D": "detached",
    "S": "semi-detached",
    "T": "terraced",
    "F": "flat",
    "O": "other",
}
TENURE = {"F": "freehold", "L": "leasehold"}

COLUMNS = ["date", "price_gbp", "type", "tenure", "new_build", "paon", "street", "town", "postcode"]

# Headerless Price Paid column order, unchanged for many years.
_INDEX = {
    "id": 0,
    "price": 1,
    "date": 2,
    "postcode": 3,
    "type": 4,
    "new": 5,
    "tenure": 6,
    "paon": 7,
    "saon": 8,
    "street": 9,
    "locality": 10,
    "town": 11,
    "district": 12,
    "county": 13,
    "category": 14,
    "status": 15,
}


def lookup(
    client,
    postcode: str,
    *,
    months: int = 6,
    limit: int = 20,
    include_additional: bool = False,
    csv_path: Path | None = None,
    today: date | None = None,
    cache_dir: Path | None = None,
) -> tuple[dict, list[dict]]:
    if months < 1 or months > 18:
        raise UsageError("--months must be between 1 and 18. For a longer window, download a yearly CSV and pass --file.")
    if limit < 1 or limit > 200:
        raise UsageError("--limit must be between 1 and 200.")
    area = normalise_postcode(postcode)
    if not area:
        raise UsageError("Pass a postcode or outward code, for example SW11 or SW11 1AA.")
    end = today or date.today()
    start = months_before(end, months)
    paths = [csv_path] if csv_path else [ensure_year(client, year, cache_dir) for year in range(start.year, end.year + 1)]
    sales = []
    for path in paths:
        sales.extend(read_sales(path, area, start, end, include_additional=include_additional))
    sales.sort(key=lambda row: (row["date"], row["price_gbp"]), reverse=True)
    summary = summarise(area, start, end, sales, include_additional=include_additional)
    return summary, sales[:limit]


def summarise(area: str, start: date, end: date, sales: list[dict], *, include_additional: bool) -> dict:
    prices = [row["price_gbp"] for row in sales]
    median = statistics.median(prices) if prices else None
    if isinstance(median, float) and median.is_integer():
        median = int(median)
    return {
        "postcode": area,
        "from": start.isoformat(),
        "to": end.isoformat(),
        "sales": len(sales),
        "median_gbp": median,
        "min_gbp": min(prices) if prices else None,
        "max_gbp": max(prices) if prices else None,
        "category": "A and B" if include_additional else "A",
    }


def read_sales(
    path: Path,
    area: str,
    start: date,
    end: date,
    *,
    include_additional: bool,
) -> list[dict]:
    rows: list[dict] = []
    with path.open(newline="", encoding="utf-8-sig", errors="replace") as handle:
        reader = csv.reader(handle)
        for record in reader:
            if len(record) < 16:
                continue
            if record[0].casefold().startswith("transaction"):
                continue
            status = record[_INDEX["status"]].strip().upper()
            if status == "D":
                continue
            category = record[_INDEX["category"]].strip().upper()
            if category == "B" and not include_additional:
                continue
            postcode = record[_INDEX["postcode"]].strip().upper()
            if not postcode_matches(postcode, area):
                continue
            sold = _parse_transfer_date(record[_INDEX["date"]])
            if sold is None or sold < start or sold > end:
                continue
            price = _price(record[_INDEX["price"]])
            if price is None:
                continue
            type_code = record[_INDEX["type"]].strip().upper()
            tenure_code = record[_INDEX["tenure"]].strip().upper()
            rows.append(
                {
                    "date": sold.isoformat(),
                    "price_gbp": price,
                    "type": PROPERTY_TYPES.get(type_code, type_code),
                    "tenure": TENURE.get(tenure_code, tenure_code),
                    "new_build": record[_INDEX["new"]].strip().upper() == "Y",
                    "paon": record[_INDEX["paon"]].strip(),
                    "street": record[_INDEX["street"]].strip(),
                    "town": record[_INDEX["town"]].strip(),
                    "postcode": postcode,
                }
            )
    return rows


def ensure_year(client, year: int, cache_dir: Path | None = None) -> Path:
    directory = cache_dir or default_cache_dir()
    directory.mkdir(parents=True, exist_ok=True)
    dest = directory / f"pp-{year}.csv"
    meta_path = directory / f"pp-{year}.meta.json"
    url = YEAR_URL.format(year=year)
    remote = client.head(url)
    length = remote.get("content-length")
    modified = remote.get("last-modified")
    signature = {"length": length, "modified": modified}
    if dest.exists() and meta_path.exists() and length:
        saved = json.loads(meta_path.read_text(encoding="utf-8"))
        if saved == signature and dest.stat().st_size == int(length):
            return dest
    client.download(url, dest, timeout=300)
    if length and dest.stat().st_size != int(length):
        raise SourceError(f"Price Paid {year} download was {dest.stat().st_size} bytes, expected {length}.")
    meta_path.write_text(json.dumps(signature), encoding="utf-8")
    return dest


def default_cache_dir() -> Path:
    root = os.environ.get("XDG_CACHE_HOME")
    base = Path(root) if root else Path.home() / ".cache"
    return base / "ukopendata"


def normalise_postcode(value: str) -> str:
    parts = value.strip().upper().split()
    return " ".join(part for part in parts if part)


def postcode_matches(postcode: str, query: str) -> bool:
    """Match a full postcode, a sector (``SW11 1``) or an outward code (``SW11``).

    ``SW11`` matches ``SW11 1AA`` and does not match ``SW1 1AA``.
    """
    postcode = normalise_postcode(postcode)
    query = normalise_postcode(query)
    if not postcode or not query:
        return False
    if " " in query:
        return postcode.startswith(query)
    outward = postcode.split(" ", 1)[0]
    return outward == query


def summary_line(summary: dict) -> str:
    median = summary["median_gbp"]
    median_text = _pounds(median) if median is not None else "n/a"
    minimum = _pounds(summary["min_gbp"]) if summary["min_gbp"] is not None else "n/a"
    maximum = _pounds(summary["max_gbp"]) if summary["max_gbp"] is not None else "n/a"
    return (
        f"{summary['postcode']}  {summary['from']} to {summary['to']}  "
        f"sales={summary['sales']}  median={median_text}  min={minimum}  max={maximum}  "
        f"category={summary['category']}"
    )


def _pounds(value: int | float) -> str:
    if isinstance(value, float) and not value.is_integer():
        return f"£{value:,.1f}"
    return f"£{int(value):,}"


def _parse_transfer_date(value: str) -> date | None:
    text = value.strip().strip('"')
    if len(text) < 10:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _price(value: str) -> int | None:
    text = value.strip().strip('"').replace(",", "")
    if not text:
        return None
    try:
        return int(float(text))
    except ValueError:
        return None
