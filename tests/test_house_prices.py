import json
from datetime import date
from pathlib import Path

import pytest

from ukopendata.dates import months_before
from ukopendata.errors import UsageError
from ukopendata.sources import house_prices

FIXTURE = Path(__file__).parent / "fixtures" / "ppd-sample.csv"
TODAY = date(2026, 10, 23)


def test_postcode_matching_does_not_confuse_sw1_and_sw11():
    assert house_prices.postcode_matches("SW11 1AA", "SW11")
    assert house_prices.postcode_matches("sw11 1aa", "sw11")
    assert not house_prices.postcode_matches("SW1 1AA", "SW11")
    assert not house_prices.postcode_matches("SW11 1AA", "SW1")
    assert house_prices.postcode_matches("SW11 1AA", "SW11 1")
    assert not house_prices.postcode_matches("SW11 4BB", "SW11 1")
    assert house_prices.postcode_matches("SW11 1AA", "SW11 1AA")


def test_months_before_clips_to_the_month():
    assert months_before(date(2026, 10, 23), 6) == date(2026, 4, 23)
    assert months_before(date(2026, 3, 31), 1) == date(2026, 2, 28)
    assert months_before(date(2026, 1, 31), 2) == date(2025, 11, 30)


def test_median_uses_every_standard_sale_and_comps_are_the_newest():
    summary, comps = house_prices.lookup(
        client=None,
        postcode="SW11",
        months=6,
        limit=2,
        csv_path=FIXTURE,
        today=TODAY,
    )
    assert summary["sales"] == 3
    assert summary["median_gbp"] == 400000
    assert summary["min_gbp"] == 250000
    assert summary["max_gbp"] == 500000
    assert summary["category"] == "A"
    assert [row["price_gbp"] for row in comps] == [400000, 500000]
    assert comps[0]["type"] == "flat"
    assert comps[0]["tenure"] == "leasehold"
    assert comps[0]["new_build"] is False
    assert "SW1" not in {row["postcode"] for row in comps}


def test_additional_category_can_be_included():
    summary, _sales = house_prices.lookup(
        client=None,
        postcode="SW11",
        months=6,
        limit=20,
        include_additional=True,
        csv_path=FIXTURE,
        today=TODAY,
    )
    assert summary["sales"] == 4
    assert summary["category"] == "A and B"


def test_summary_line_and_attribution():
    summary, _sales = house_prices.lookup(
        client=None,
        postcode="sw11",
        months=6,
        limit=5,
        csv_path=FIXTURE,
        today=TODAY,
    )
    line = house_prices.summary_line(summary)
    assert line.startswith("SW11  2026-04-23 to 2026-10-23")
    assert "median=£400,000" in line
    assert "Crown copyright and database right 2021" in house_prices.ATTRIBUTION
    assert "address.management@royalmail.com" in house_prices.ADDRESS_NOTE


def test_rejects_a_huge_window():
    with pytest.raises(UsageError):
        house_prices.lookup(None, "SW11", months=36, csv_path=FIXTURE, today=TODAY)


def test_year_file_is_cached(tmp_path):
    body = FIXTURE.read_bytes()
    headers = {"content-length": str(len(body)), "last-modified": "Tue, 01 Sep 2026 00:00:00 GMT"}
    downloads = {"n": 0}

    def handler(method, url, payload, headers_arg):
        if method == "HEAD":
            return headers
        if method == "DOWNLOAD":
            downloads["n"] += 1
            return body
        raise AssertionError(method)

    from tests.fakes import FakeClient

    client = FakeClient(handler)
    first = house_prices.ensure_year(client, 2026, cache_dir=tmp_path)
    second = house_prices.ensure_year(client, 2026, cache_dir=tmp_path)
    assert first == second
    assert downloads["n"] == 1
    meta = json.loads((tmp_path / "pp-2026.meta.json").read_text())
    assert meta["length"] == headers["content-length"]
    assert "2026" in client.calls[0][1]
