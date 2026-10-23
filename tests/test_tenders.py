import json
from datetime import date
from pathlib import Path

import pytest

from ukopendata.errors import HttpError, SourceError
from ukopendata.sources import tenders
from tests.fakes import FakeClient

FIXTURES = Path(__file__).parent / "fixtures"
CF = json.loads((FIXTURES / "contracts-finder.json").read_text())
FTS = json.loads((FIXTURES / "find-a-tender.json").read_text())


def _client():
    def handler(method, url, payload, headers):
        if method == "POST":
            return CF
        return FTS

    return FakeClient(handler)


def test_search_merges_both_sources_and_filters_find_a_tender():
    rows, warnings = tenders.search(
        _client(),
        keyword="roofing",
        region="London",
        days=30,
        limit=10,
        today=date(2026, 10, 23),
    )
    assert warnings == []
    sources = {row["source"] for row in rows}
    assert sources == {"contracts_finder", "find_a_tender"}
    fts = [row for row in rows if row["source"] == "find_a_tender"]
    assert len(fts) == 1
    assert fts[0]["buyer"] == "London Borough Example"
    assert fts[0]["value_gbp"] == 4000000
    assert fts[0]["deadline"] == "2026-11-19"
    assert fts[0]["url"].endswith("/Notice/100110-2026")
    cf = [row for row in rows if row["source"] == "contracts_finder"][0]
    assert cf["title"].startswith("Roofing")
    assert cf["value_gbp"] == 45000
    assert cf["published"] == "2026-10-14"


def test_contracts_finder_payload_uses_the_published_region_name():
    client = _client()
    tenders.search(client, keyword="roofing", region="greater london", days=14, limit=5, today=date(2026, 10, 23))
    payload = client.calls[0][2]
    assert payload["searchCriteria"]["keyword"] == "roofing"
    assert payload["searchCriteria"]["regions"] == "London"
    assert payload["searchCriteria"]["publishedFrom"].startswith("2026-10-09")


def test_scotland_notice_matches_scotland_not_london():
    release = FTS["releases"][1]
    assert tenders.release_matches(release, "roofing", "Scotland")
    assert not tenders.release_matches(release, "roofing", "London")
    assert not tenders.release_matches(FTS["releases"][2], "roofing", "London")


def test_one_source_failing_still_returns_the_other():
    def handler(method, url, payload, headers):
        if "contractsfinder" in url:
            raise HttpError(503, url, "unavailable")
        return FTS

    rows, warnings = tenders.search(
        FakeClient(handler),
        keyword="roofing",
        region="London",
        days=7,
        limit=5,
        today=date(2026, 10, 23),
    )
    assert rows and rows[0]["source"] == "find_a_tender"
    assert "Contracts Finder unavailable" in warnings[0]


def test_both_sources_failing_is_an_error():
    def handler(method, url, payload, headers):
        raise HttpError(500, url, "down")

    with pytest.raises(SourceError):
        tenders.search(FakeClient(handler), keyword="roofing", days=7, today=date(2026, 10, 23))
