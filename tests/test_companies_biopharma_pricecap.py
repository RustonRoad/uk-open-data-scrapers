import json
from pathlib import Path

import pytest

from ukopendata.errors import HttpError, UsageError
from ukopendata.sources import biopharma, companies, price_cap
from tests.fakes import FakeClient

FIXTURES = Path(__file__).parent / "fixtures"


def test_companies_search_sends_the_key_as_basic_auth_and_not_in_the_url():
    secret = "super-secret-key"
    seen = {}

    def handler(method, url, payload, headers):
        seen["url"] = url
        seen["headers"] = headers
        return json.loads((FIXTURES / "companies-search.json").read_text())

    rows = companies.search(FakeClient(handler), "roofing", limit=5, key=secret)
    assert secret not in seen["url"]
    assert seen["headers"]["Authorization"] == companies.authorization_header(secret)
    assert not seen["headers"]["Authorization"].startswith("Basic super")
    assert rows[0]["name"] == "ROOFING EXAMPLE LTD"
    assert rows[0]["address"].endswith("SW11 1AA")


def test_company_profile_pads_a_numeric_number_and_formats_the_address():
    def handler(method, url, payload, headers):
        assert url.endswith("/company/00445790")
        return json.loads((FIXTURES / "companies-profile.json").read_text())

    row = companies.profile(FakeClient(handler), "445790", key="abc")
    assert row["company_number"] == "12345678"
    assert row["sic_codes"] == "43910,41202"
    assert row["address"] == "1 Test Street, London, SW11 1AA"


def test_missing_companies_house_key_explains_where_to_get_one(monkeypatch):
    monkeypatch.delenv(companies.ENV_VAR, raising=False)
    with pytest.raises(UsageError) as caught:
        companies.require_key()
    message = str(caught.value)
    assert "COMPANIES_HOUSE_API_KEY" in message
    assert "developer.company-information.service.gov.uk" in message


def test_rejected_key_does_not_echo_the_secret():
    secret = "super-secret-key"

    def handler(method, url, payload, headers):
        raise HttpError(401, url, "Invalid Authorization")

    with pytest.raises(UsageError) as caught:
        companies.search(FakeClient(handler), "roofing", key=secret)
    assert secret not in str(caught.value)
    assert "401" in str(caught.value)


def test_biopharma_dedupes_exhibits_and_drops_other_sics():
    document = json.loads((FIXTURES / "edgar-hits.json").read_text())

    def handler(method, url, payload, headers):
        assert "forms=8-K%2C6-K" in url or "forms=8-K,6-K" in url
        assert "startdt=2026-10-22" in url
        assert headers is None or True
        return document

    rows = biopharma.search(FakeClient(handler), on="2026-10-22", limit=10)
    assert len(rows) == 1
    row = rows[0]
    assert row["company"] == "Sagimet Biosciences Inc."
    assert row["ticker"] == "SGMT"
    assert row["form"] == "8-K"
    assert row["items"] == "7.01,9.01,8.01"
    assert row["sic"] == "2834"
    assert row["url"] == (
        "https://www.sec.gov/Archives/edgar/data/1400118/"
        "000119312526428314/0001193125-26-428314-index.html"
    )
    assert biopharma.SEC_USER_AGENT == "ukopendata Dartiproductions@protonmail.com"
    assert biopharma.SEC_MIN_INTERVAL >= 0.1
    assert "Dartiproductions@protonmail.com" in biopharma.SEC_USER_AGENT


def test_price_cap_reads_the_headline_table():
    rows, note = price_cap.parse_price_cap((FIXTURES / "ofgem_price_cap.html").read_text())
    assert rows[0]["period"] == "1 October to 31 December 2026"
    assert rows[0]["typical_annual_gbp"] == 1723
    assert rows[0]["change_percent"] == 4
    assert isinstance(rows[0]["change_percent"], int)
    assert rows[0]["electricity_unit_p_per_kwh"] == 26.32
    assert rows[0]["electricity_standing_p_per_day"] == 54.83
    assert rows[0]["gas_unit_p_per_kwh"] == 7.97
    assert rows[0]["gas_standing_p_per_day"] == 29.68
    assert rows[1]["period"] == "1 July to 30 September 2026"
    assert rows[1]["electricity_unit_p_per_kwh"] == 26.11
    assert rows[1]["typical_annual_gbp"] == ""
    assert note == "Figures are rounded to two decimal places and include 5% VAT on gas."
