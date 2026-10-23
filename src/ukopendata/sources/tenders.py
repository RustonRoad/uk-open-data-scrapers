"""UK public tenders from Contracts Finder and Find a Tender.

Contracts Finder search:
https://www.contractsfinder.service.gov.uk/apidocumentation/Notices/2/POST-rest-searches-search

Find a Tender OCDS releases:
https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages

Both publish under the Open Government Licence v3.0. A search here is a
small sample: a few pages, not the whole archive.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from ukopendata.dates import parse_flexible_date
from ukopendata.errors import HttpError, SourceError, UsageError

CF_URL = "https://www.contractsfinder.service.gov.uk/api/rest/2/search_notices/json"
FTS_URL = "https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages"
OGL = "http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/"

# Contracts Finder's region names, and the NUTS 1 code Find a Tender puts on
# the buyer address. Text such as "London" is also matched against locality.
REGION_NUTS = {
    "london": ("UKI",),
    "greater london": ("UKI",),
    "south east": ("UKJ",),
    "south west": ("UKK",),
    "east of england": ("UKH",),
    "east midlands": ("UKF",),
    "west midlands": ("UKG",),
    "north west": ("UKD",),
    "north east": ("UKC",),
    "yorkshire and the humber": ("UKE",),
    "yorkshire": ("UKE",),
    "wales": ("UKL",),
    "scotland": ("UKM",),
    "northern ireland": ("UKN",),
}

CF_REGION_NAMES = {
    "london": "London",
    "greater london": "London",
    "south east": "South East",
    "south west": "South West",
    "east of england": "East of England",
    "east midlands": "East Midlands",
    "west midlands": "West Midlands",
    "north west": "North West",
    "north east": "North East",
    "yorkshire and the humber": "Yorkshire and The Humber",
    "yorkshire": "Yorkshire and The Humber",
    "wales": "Wales",
    "scotland": "Scotland",
    "northern ireland": "Northern Ireland",
}

COLUMNS = [
    "source",
    "published",
    "title",
    "buyer",
    "value_gbp",
    "currency",
    "deadline",
    "status",
    "region",
    "cpv",
    "url",
]


def search(
    client,
    *,
    keyword: str,
    region: str | None = None,
    days: int = 30,
    limit: int = 20,
    status: str | None = None,
    stage: str = "tender",
    sources: str = "both",
    today: date | None = None,
    max_fts_pages: int = 3,
) -> tuple[list[dict], list[str]]:
    keyword = keyword.strip()
    if not keyword:
        raise UsageError("Pass a keyword, for example: ukopendata tenders --keyword roofing")
    if days < 1 or days > 366:
        raise UsageError("--days must be between 1 and 366. This command is a small sample.")
    if limit < 1 or limit > 100:
        raise UsageError("--limit must be between 1 and 100.")
    if sources not in {"both", "contracts-finder", "find-a-tender"}:
        raise UsageError("--source must be both, contracts-finder or find-a-tender.")
    if stage not in {"tender", "award", "planning", "all"}:
        raise UsageError("--stage must be tender, award, planning or all.")

    end = today or datetime.now(timezone.utc).date()
    start = end - timedelta(days=days)
    warnings: list[str] = []
    rows: list[dict] = []

    if sources in {"both", "contracts-finder"}:
        try:
            rows.extend(
                fetch_contracts_finder(
                    client,
                    keyword=keyword,
                    region=region,
                    start=start,
                    end=end,
                    limit=limit,
                    status=status,
                )
            )
        except HttpError as exc:
            warnings.append(f"Contracts Finder unavailable: {exc}")

    if sources in {"both", "find-a-tender"}:
        try:
            rows.extend(
                fetch_find_a_tender(
                    client,
                    keyword=keyword,
                    region=region,
                    start=start,
                    end=end,
                    limit=limit,
                    max_pages=max_fts_pages,
                    stage=stage,
                )
            )
        except HttpError as exc:
            warnings.append(f"Find a Tender unavailable: {exc}")

    if warnings and not rows:
        raise SourceError(" ".join(warnings))

    rows.sort(key=lambda row: row.get("published") or "", reverse=True)
    return rows[:limit], warnings


def fetch_contracts_finder(
    client,
    *,
    keyword: str,
    region: str | None,
    start: date,
    end: date,
    limit: int,
    status: str | None,
) -> list[dict]:
    criteria: dict[str, Any] = {
        "keyword": keyword,
        "publishedFrom": f"{start.isoformat()}T00:00:00Z",
        "publishedTo": f"{end.isoformat()}T23:59:59Z",
    }
    if region:
        criteria["regions"] = CF_REGION_NAMES.get(_region_key(region), region.strip())
    if status:
        criteria["statuses"] = [status.strip()]
    payload = {"searchCriteria": criteria, "size": limit}
    document = client.post_json(CF_URL, payload)
    if not isinstance(document, dict):
        raise SourceError("Contracts Finder returned an unexpected response.")
    notices = document.get("noticeList") or []
    rows = []
    for entry in notices:
        item = entry.get("item") if isinstance(entry, dict) else None
        if isinstance(item, dict):
            rows.append(notice_row(item))
    return rows


def notice_row(item: dict) -> dict:
    value = _first_number(item.get("valueHigh"), item.get("valueLow"), item.get("awardedValue"))
    notice_id = str(item.get("id") or "")
    return {
        "source": "contracts_finder",
        "published": parse_flexible_date(str(item.get("publishedDate") or "")),
        "title": _clean(item.get("title")),
        "buyer": _clean(item.get("organisationName")),
        "value_gbp": value,
        "currency": "GBP" if value is not None else "",
        "deadline": parse_flexible_date(str(item.get("deadlineDate") or "")),
        "status": _clean(item.get("noticeStatus")),
        "region": _clean(item.get("regionText") or item.get("region")),
        "cpv": _clean(item.get("cpvCodes")),
        "url": f"https://www.contractsfinder.service.gov.uk/notice/{notice_id}" if notice_id else "",
    }


def fetch_find_a_tender(
    client,
    *,
    keyword: str,
    region: str | None,
    start: date,
    end: date,
    limit: int,
    max_pages: int,
    stage: str = "tender",
) -> list[dict]:
    # The OCDS search has no keyword parameter. Read a few pages of the
    # published window and keep notices whose title or description matches.
    # A comma-separated stages value returns an empty package from the live
    # API, so one stage is sent, or the parameter is omitted for "all".
    stage_query = "" if stage == "all" else f"&stages={stage}"
    params = (
        f"limit=100{stage_query}"
        f"&updatedFrom={start.isoformat()}T00:00:00"
        f"&updatedTo={end.isoformat()}T23:59:59"
    )
    url = f"{FTS_URL}?{params}"
    matched: list[dict] = []
    seen_urls: set[str] = set()
    for _ in range(max_pages):
        if url in seen_urls:
            break
        seen_urls.add(url)
        document = client.get_json(url)
        if not isinstance(document, dict):
            raise SourceError("Find a Tender returned an unexpected response.")
        for release in document.get("releases") or []:
            if isinstance(release, dict) and release_matches(release, keyword, region):
                matched.append(release_row(release))
        if len(matched) >= limit:
            break
        link = (document.get("links") or {}).get("next")
        if not link:
            break
        url = str(link)
    return matched


def release_matches(release: dict, keyword: str, region: str | None) -> bool:
    tender = release.get("tender") or {}
    haystack = " ".join(
        str(part)
        for part in (tender.get("title"), tender.get("description"), release.get("id"))
        if part
    ).casefold()
    if keyword.casefold() not in haystack:
        return False
    if region and not region_matches(release, region):
        return False
    return True


def region_matches(release: dict, region: str) -> bool:
    wanted = _region_key(region)
    prefixes = REGION_NUTS.get(wanted, ())
    buyer = _buyer(release)
    address = buyer.get("address") or {}
    code = str(address.get("region") or "").upper()
    if prefixes and any(code.startswith(prefix) for prefix in prefixes):
        return True
    blob = " ".join(
        str(address.get(key) or "")
        for key in ("region", "locality", "postalCode", "countryName")
    ).casefold()
    return wanted in blob


def release_row(release: dict) -> dict:
    tender = release.get("tender") or {}
    buyer = _buyer(release)
    address = buyer.get("address") or {}
    value = tender.get("value") or {}
    amount = value.get("amount")
    currency = value.get("currency") or ""
    classification = tender.get("classification") or {}
    cpv = classification.get("id") or ""
    notice_id = str(release.get("id") or "")
    region = address.get("locality") or address.get("region") or ""
    deadline = ""
    period = tender.get("tenderPeriod") or {}
    if period.get("endDate"):
        deadline = parse_flexible_date(str(period["endDate"]))
    number = amount if isinstance(amount, (int, float)) and amount != float("inf") else None
    value_gbp = number if currency in {"", "GBP"} else None
    return {
        "source": "find_a_tender",
        "published": parse_flexible_date(str(release.get("date") or "")),
        "title": _clean(tender.get("title")),
        "buyer": _clean(buyer.get("name")),
        "value_gbp": value_gbp if value_gbp is None else _number(value_gbp),
        "currency": currency,
        "deadline": deadline,
        "status": _clean(tender.get("status")),
        "region": _clean(region),
        "cpv": _clean(cpv),
        "url": f"https://www.find-tender.service.gov.uk/Notice/{notice_id}" if notice_id else "",
    }


def _region_key(region: str) -> str:
    return " ".join(region.strip().casefold().replace("-", " ").replace("_", " ").split())


def _buyer(release: dict) -> dict:
    for party in release.get("parties") or []:
        roles = party.get("roles") or []
        if "buyer" in roles:
            return party
    parties = release.get("parties") or []
    return parties[0] if parties else {}


def _clean(value: object) -> str:
    if value is None:
        return ""
    return " ".join(str(value).replace("\xa0", " ").split())


def _number(value: float) -> int | float:
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def _first_number(*values: object) -> int | float | None:
    for value in values:
        if isinstance(value, bool) or value is None or value == "":
            continue
        if isinstance(value, (int, float)):
            if value == float("inf"):
                continue
            return _number(float(value))
        try:
            return _number(float(str(value)))
        except (TypeError, ValueError):
            continue
    return None
