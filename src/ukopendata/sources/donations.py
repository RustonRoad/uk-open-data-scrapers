"""Electoral Commission donations search.

The public register search behind search.electoralcommission.org.uk.
One page, sorted by accepted date, so a command stays small.

https://search.electoralcommission.org.uk/Search/Donations

Contains public sector information licensed under the Open Government Licence v3.0.
"""

from __future__ import annotations

from datetime import date, timedelta
from urllib.parse import urlencode

from ukopendata.dates import parse_flexible_date, parse_iso_date
from ukopendata.errors import SourceError, UsageError

SEARCH_URL = "https://search.electoralcommission.org.uk/api/search/Donations"

COLUMNS = [
    "accepted",
    "recipient",
    "recipient_type",
    "donor",
    "donor_type",
    "value_gbp",
    "donation_type",
    "reported",
    "register",
    "ec_ref",
]


def search(
    client,
    *,
    query: str | None = None,
    days: int = 90,
    date_from: str | None = None,
    date_to: str | None = None,
    min_value: float = 0,
    donor_type: str | None = None,
    limit: int = 20,
    today: date | None = None,
    max_pages: int = 3,
) -> list[dict]:
    if limit < 1 or limit > 100:
        raise UsageError("--limit must be between 1 and 100.")
    if days < 1 or days > 3660:
        raise UsageError("--days must be between 1 and 3660.")
    end = parse_iso_date(date_to) if date_to else (today or date.today())
    start = parse_iso_date(date_from) if date_from else end - timedelta(days=days)
    if start > end:
        raise UsageError("--from must be on or before --to.")

    collected: list[dict] = []
    page_size = 50 if min_value or donor_type else min(50, limit)
    for page in range(1, max_pages + 1):
        params = {
            "current": str(page),
            "rows": str(page_size),
            "sort": "AcceptedDate",
            "order": "desc",
            "date": "Accepted",
            "from": start.strftime("%d/%m/%Y"),
            "to": end.strftime("%d/%m/%Y"),
        }
        if query:
            params["query"] = query.strip()
        document = client.get_json(f"{SEARCH_URL}?{urlencode(params)}")
        if not isinstance(document, dict):
            raise SourceError("The Electoral Commission search returned an unexpected response.")
        results = document.get("Result") or []
        if not isinstance(results, list):
            raise SourceError("The Electoral Commission search returned no Result list.")
        for record in results:
            if not isinstance(record, dict):
                continue
            row = donation_row(record)
            if min_value and (row["value_gbp"] or 0) < min_value:
                continue
            if donor_type and donor_type.casefold() not in str(row["donor_type"]).casefold():
                continue
            collected.append(row)
            if len(collected) >= limit:
                return collected
        if len(results) < page_size:
            break
    return collected


def donation_row(record: dict) -> dict:
    value = record.get("Value")
    number: int | float | None
    if isinstance(value, bool) or value is None:
        number = None
    elif isinstance(value, (int, float)):
        number = int(value) if float(value).is_integer() else float(value)
    else:
        try:
            parsed = float(str(value))
            number = int(parsed) if parsed.is_integer() else parsed
        except ValueError:
            number = None
    return {
        "accepted": parse_flexible_date(str(record.get("AcceptedDate") or "")),
        "recipient": _clean(record.get("RegulatedEntityName")),
        "recipient_type": _clean(record.get("RegulatedEntityType")),
        "donor": _clean(record.get("DonorName")),
        "donor_type": _clean(record.get("DonorStatus")),
        "value_gbp": number,
        "donation_type": _clean(record.get("DonationType")),
        "reported": parse_flexible_date(str(record.get("ReportedDate") or "")),
        "register": _clean(record.get("RegisterName")),
        "ec_ref": _clean(record.get("ECRef")),
    }


def _clean(value: object) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())
