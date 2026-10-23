"""Companies House public data API.

A free application key is required. Create one at
https://developer.company-information.service.gov.uk/ and export it as
COMPANIES_HOUSE_API_KEY. The key is sent as HTTP Basic (the key is the
username, the password is empty). It is never written to disk by this package.

Company data is Crown copyright, reused under the Open Government Licence,
and the API is subject to the Companies House terms. The published rate limit
is 600 requests in 5 minutes. Each command here makes one request.

https://developer-specs.company-information.service.gov.uk/companies-house-public-data-api/reference
"""

from __future__ import annotations

import base64
import os
from urllib.parse import urlencode

from ukopendata.errors import HttpError, SourceError, UsageError

API_ROOT = "https://api.company-information.service.gov.uk"
KEY_URL = "https://developer.company-information.service.gov.uk/"
ENV_VAR = "COMPANIES_HOUSE_API_KEY"

SEARCH_COLUMNS = ["company_number", "name", "status", "incorporated", "type", "address"]
PROFILE_COLUMNS = ["company_number", "name", "status", "incorporated", "type", "sic_codes", "address"]


def require_key(environ: dict[str, str] | None = None) -> str:
    source = os.environ if environ is None else environ
    key = (source.get(ENV_VAR) or "").strip()
    if not key:
        raise UsageError(
            f"Set {ENV_VAR} to a free Companies House API key. "
            f"Create one at {KEY_URL} (register, then create an application). "
            "Do not commit the key."
        )
    return key


def authorization_header(key: str) -> str:
    token = base64.b64encode(f"{key}:".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def search(client, query: str, *, limit: int = 10, key: str | None = None) -> list[dict]:
    text = query.strip()
    if not text:
        raise UsageError("Pass a company name, for example: ukopendata companies \"acme ltd\"")
    if limit < 1 or limit > 50:
        raise UsageError("--limit must be between 1 and 50.")
    api_key = key or require_key()
    params = urlencode({"q": text, "items_per_page": str(limit)})
    url = f"{API_ROOT}/search/companies?{params}"
    try:
        document = client.get_json(url, headers=_headers(api_key))
    except HttpError as exc:
        raise _explain(exc) from None
    if not isinstance(document, dict):
        raise SourceError("Companies House returned an unexpected search response.")
    rows = []
    for item in document.get("items") or []:
        if isinstance(item, dict):
            rows.append(search_row(item))
    return rows


def profile(client, company_number: str, *, key: str | None = None) -> dict:
    number = normalise_number(company_number)
    if not number:
        raise UsageError("Pass a company number, for example: ukopendata company 00445790")
    api_key = key or require_key()
    url = f"{API_ROOT}/company/{number}"
    try:
        document = client.get_json(url, headers=_headers(api_key))
    except HttpError as exc:
        if exc.status == 404:
            raise SourceError(f"No company found with number {number}.") from None
        raise _explain(exc) from None
    if not isinstance(document, dict):
        raise SourceError("Companies House returned an unexpected company profile.")
    return profile_row(document)


def search_row(item: dict) -> dict:
    address = item.get("address_snippet") or _format_address(item.get("address") or {})
    return {
        "company_number": item.get("company_number") or "",
        "name": item.get("title") or item.get("company_name") or "",
        "status": item.get("company_status") or "",
        "incorporated": item.get("date_of_creation") or "",
        "type": item.get("company_type") or "",
        "address": address,
    }


def profile_row(document: dict) -> dict:
    sic = document.get("sic_codes") or []
    return {
        "company_number": document.get("company_number") or "",
        "name": document.get("company_name") or "",
        "status": document.get("company_status") or "",
        "incorporated": document.get("date_of_creation") or "",
        "type": document.get("type") or "",
        "sic_codes": ",".join(sic),
        "address": _format_address(document.get("registered_office_address") or {}),
    }


def normalise_number(value: str) -> str:
    text = value.strip().upper().replace(" ", "")
    if text.isdigit():
        return text.zfill(8)
    return text


def _headers(key: str) -> dict[str, str]:
    return {"Authorization": authorization_header(key), "Accept": "application/json"}


def _explain(exc: HttpError) -> Exception:
    if exc.status == 401:
        return UsageError(
            "Companies House rejected the API key (HTTP 401). "
            f"Check {ENV_VAR}. Create a key at {KEY_URL}"
        )
    if exc.status == 429:
        return SourceError("Companies House rate limit reached (600 requests in 5 minutes). Wait and try again.")
    return exc


def _format_address(address: dict) -> str:
    if not isinstance(address, dict):
        return ""
    keys = (
        "premises",
        "address_line_1",
        "address_line_2",
        "locality",
        "region",
        "postal_code",
        "country",
    )
    parts = [str(address[key]).strip() for key in keys if address.get(key)]
    return ", ".join(parts)
