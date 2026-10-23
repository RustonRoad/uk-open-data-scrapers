"""Biopharma 8-K and 6-K filings from the SEC EDGAR full-text search.

Endpoint: https://efts.sec.gov/LATEST/search-index
Fair access: https://www.sec.gov/os/accessing-edgar-data

Every request sends a User-Agent that includes a contact address, and this
client waits at least 0.15s between SEC requests (under the 10 requests/second
limit). EDGAR filings are US government works.
"""

from __future__ import annotations

import re
from urllib.parse import urlencode

from ukopendata.dates import parse_iso_date
from ukopendata.errors import SourceError, UsageError

SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
SEC_USER_AGENT = "ukopendata Dartiproductions@protonmail.com"
# Stay under the SEC's 10 requests/second fair-access limit.
SEC_MIN_INTERVAL = 0.15

# Pharmaceutical preparations, medicinal chemicals, in-vitro diagnostics,
# biological products. Hits that carry a different SIC are dropped. Hits with
# no SIC are kept, because some 6-K filers do not have one.
BIOPHARMA_SICS = frozenset({"2833", "2834", "2835", "2836"})

DEFAULT_QUERY = (
    'pharmaceutical OR biotech OR "clinical trial" OR "Food and Drug Administration" OR FDA'
)

COLUMNS = ["filed", "company", "ticker", "form", "items", "sic", "location", "accession", "url"]


def search(client, *, on: str, query: str | None = None, limit: int = 20) -> list[dict]:
    if limit < 1 or limit > 50:
        raise UsageError("--limit must be between 1 and 50.")
    try:
        parse_iso_date(on)
    except ValueError as exc:
        raise UsageError(str(exc)) from None
    text = (query or DEFAULT_QUERY).strip()
    if not text:
        raise UsageError("Pass a search query or omit --query to use the default biopharma terms.")

    # Exhibits inflate the hit list, so ask for more than --limit and dedupe.
    page_size = min(100, max(limit * 3, 20))
    hits: list[dict] = []
    offset = 0
    total = None
    for _ in range(3):
        params = {
            "q": text,
            "forms": "8-K,6-K",
            "dateRange": "custom",
            "startdt": on,
            "enddt": on,
            "from": str(offset),
            "size": str(page_size),
        }
        document = client.get_json(f"{SEARCH_URL}?{urlencode(params)}")
        if not isinstance(document, dict):
            raise SourceError("EDGAR full-text search returned an unexpected response.")
        bucket = document.get("hits") or {}
        page = bucket.get("hits") or []
        if total is None:
            raw_total = (bucket.get("total") or {}).get("value")
            total = raw_total if isinstance(raw_total, int) else None
        if not isinstance(page, list) or not page:
            break
        hits.extend(item for item in page if isinstance(item, dict))
        offset += len(page)
        if total is not None and offset >= total:
            break
        if len(page) < page_size:
            break
        if len(_dedupe(hits)) >= limit:
            break
    return _dedupe(hits)[:limit]


def _dedupe(hits: list[dict]) -> list[dict]:
    grouped: dict[str, dict] = {}
    for hit in hits:
        source = hit.get("_source") or {}
        if not isinstance(source, dict):
            continue
        sics = {str(code) for code in (source.get("sics") or [])}
        if sics and sics.isdisjoint(BIOPHARMA_SICS):
            continue
        accession = str(source.get("adsh") or hit.get("_id") or "")
        if not accession:
            continue
        current = grouped.get(accession)
        if current is None:
            grouped[accession] = _row(source, hit)
            continue
        merged_items = _merge_items(current["items"], _items(source))
        current["items"] = merged_items
    rows = list(grouped.values())
    rows.sort(key=lambda row: (row["company"], row["accession"]))
    return rows


def _row(source: dict, hit: dict) -> dict:
    company, ticker = _name_and_ticker(source.get("display_names") or [])
    ciks = source.get("ciks") or []
    cik = str(ciks[0]).lstrip("0") if ciks else ""
    accession = str(source.get("adsh") or "")
    accession_compact = accession.replace("-", "")
    url = ""
    if cik and accession_compact and accession:
        url = (
            f"https://www.sec.gov/Archives/edgar/data/{cik}/"
            f"{accession_compact}/{accession}-index.html"
        )
    locations = source.get("biz_locations") or []
    sics = source.get("sics") or []
    return {
        "filed": source.get("file_date") or "",
        "company": company,
        "ticker": ticker,
        "form": source.get("form") or (source.get("root_forms") or [""])[0],
        "items": _items(source),
        "sic": ",".join(str(code) for code in sics),
        "location": locations[0] if locations else "",
        "accession": accession,
        "url": url,
    }


def _items(source: dict) -> str:
    values = source.get("items") or []
    return ",".join(str(item) for item in values)


def _merge_items(left: str, right: str) -> str:
    seen: list[str] = []
    for part in f"{left},{right}".split(","):
        item = part.strip()
        if item and item not in seen:
            seen.append(item)
    return ",".join(seen)


_NAME = re.compile(r"^(.*?)\s+\(([^)]+)\)\s+\(CIK\s+\d+\)\s*$")


def _name_and_ticker(display_names: list) -> tuple[str, str]:
    if not display_names:
        return "", ""
    text = str(display_names[0]).strip()
    match = _NAME.match(text)
    if not match:
        return text, ""
    ticker = match.group(2).strip()
    # A missing ticker is sometimes a second copy of the name. Keep short tokens.
    if len(ticker) > 8 or " " in ticker:
        ticker = ""
    return match.group(1).strip(), ticker
