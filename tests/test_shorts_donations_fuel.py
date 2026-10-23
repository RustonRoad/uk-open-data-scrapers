import json
from pathlib import Path

from ukopendata.sources import donations, fuel, shorts
from tests.fakes import FakeClient

FIXTURES = Path(__file__).parent / "fixtures"


def test_shorts_are_ranked_by_percent():
    rows = shorts.top_positions(shorts.parse_positions((FIXTURES / "fca-shorts.csv").read_bytes()), top=2)
    assert [row["issuer"] for row in rows] == ["PRIMARY HEALTH PROPERTIES PLC", "ENERGEAN PLC"]
    assert rows[0]["rank"] == 1
    assert rows[0]["net_short_pct"] == 5.24
    assert rows[0]["position_date"] == "2026-10-19"
    assert rows[1]["isin"] == "GB00BG12Y042"


def test_shorts_fetch_uses_the_current_csv_without_a_query_string():
    seen = {}

    def handler(method, url, payload, headers):
        seen["url"] = url
        return (FIXTURES / "fca-shorts.csv").read_bytes()

    rows = shorts.fetch_top(FakeClient(handler), top=1)
    assert "?" not in seen["url"]
    assert seen["url"].endswith("aggregated-current-net-short-positions.csv")
    assert rows[0]["issuer"].startswith("PRIMARY")


def test_donation_dates_and_minimum_value():
    document = json.loads((FIXTURES / "donations.json").read_text())

    def handler(method, url, payload, headers):
        assert "from=01%2F01%2F2026" in url or "from=01/01/2026" in url
        assert "rows=50" in url
        return document

    rows = donations.search(
        FakeClient(handler),
        min_value=50000,
        date_from="2026-01-01",
        date_to="2026-10-23",
        donor_type="Company",
        limit=10,
    )
    assert len(rows) == 1
    assert rows[0]["donor"] == "Flowidea Limited"
    assert rows[0]["accepted"] == "2026-09-10"
    assert rows[0]["value_gbp"] == 250000
    assert rows[0]["recipient"] == "Labour Party"


def test_fuel_picks_the_current_csv_and_the_latest_weeks():
    content = json.loads((FIXTURES / "fuel-content.json").read_text())
    assert fuel.csv_attachment_url(content).endswith("fuel-2018.csv")
    rows = fuel.parse_fuel_csv((FIXTURES / "fuel.csv").read_bytes())
    assert [row["date"] for row in rows] == ["2026-10-06", "2026-10-13", "2026-10-20"]
    assert rows[-1]["petrol_ppl"] == 136.4
    assert rows[-1]["petrol_vat_pct"] == 20

    def handler(method, url, payload, headers):
        if url.endswith("weekly-road-fuel-prices"):
            return content
        return (FIXTURES / "fuel.csv").read_bytes()

    latest = fuel.fetch_latest(FakeClient(handler), weeks=1)
    assert latest[0]["date"] == "2026-10-20"
    assert latest[0]["diesel_ppl"] == 143.0
