from pathlib import Path

import pytest

from ukopendata.cli import build_parser, main
from ukopendata.errors import HttpError
from ukopendata.http import HttpClient
from ukopendata.marketing import APIFY_URL, NEWSLETTER_URL, SCALE_SENTENCE, STORE_URL
from tests.fakes import FakeOpener

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = [
    "tenders",
    "shorts",
    "donations",
    "house-prices",
    "companies",
    "company",
    "biopharma-events",
    "price-cap",
    "fuel",
]


@pytest.mark.parametrize("command", COMMANDS)
def test_every_command_help_points_at_the_hosted_version(command, capsys):
    with pytest.raises(SystemExit) as caught:
        main([command, "--help"])
    assert caught.value.code == 0
    text = capsys.readouterr().out
    assert SCALE_SENTENCE in text
    assert APIFY_URL in text
    assert NEWSLETTER_URL in text
    assert STORE_URL in text


def test_shorts_and_biopharma_help_say_not_investment_advice(capsys):
    for command in ("shorts", "biopharma-events"):
        with pytest.raises(SystemExit):
            main([command, "--help"])
        assert "Not investment advice" in capsys.readouterr().out


def test_footer_stays_off_the_csv(monkeypatch, capsys, tmp_path):
    from ukopendata.sources import shorts

    monkeypatch.setattr(
        shorts,
        "fetch_top",
        lambda client, top: [
            {
                "rank": 1,
                "issuer": "EXAMPLE PLC",
                "isin": "GB0000000000",
                "net_short_pct": 1.5,
                "position_date": "2026-10-20",
            }
        ],
    )
    destination = tmp_path / "shorts.csv"
    assert main(["shorts", "--top", "1", "--format", "csv", "--output", str(destination)]) == 0
    captured = capsys.readouterr()
    payload = destination.read_text()
    assert "EXAMPLE PLC" in payload
    assert "apify.com" not in payload
    assert "apify.com" not in captured.out
    assert SCALE_SENTENCE in captured.err
    assert NEWSLETTER_URL in captured.err
    assert STORE_URL in captured.err
    assert "Not investment advice" in captured.err


def test_house_prices_table_includes_the_median(monkeypatch, capsys):
    from ukopendata.sources import house_prices

    summary = {
        "postcode": "SW11",
        "from": "2026-04-23",
        "to": "2026-10-23",
        "sales": 3,
        "median_gbp": 400000,
        "min_gbp": 250000,
        "max_gbp": 500000,
        "category": "A",
    }
    sales = [
        {
            "date": "2026-08-01",
            "price_gbp": 400000,
            "type": "flat",
            "tenure": "leasehold",
            "new_build": False,
            "paon": "12",
            "street": "LATCHMERE ROAD",
            "town": "LONDON",
            "postcode": "SW11 1AA",
        }
    ]
    monkeypatch.setattr(house_prices, "lookup", lambda *args, **kwargs: (summary, sales))
    assert main(["house-prices", "SW11", "--months", "6", "--limit", "1"]) == 0
    out, err = capsys.readouterr()
    assert "median=£400,000" in out
    assert "SW11 1AA" in out
    assert "database right 2021" in err
    assert "Royal Mail" in err


def test_companies_without_a_key_exits_2(monkeypatch, capsys):
    monkeypatch.delenv("COMPANIES_HOUSE_API_KEY", raising=False)
    assert main(["companies", "roofing"]) == 2
    err = capsys.readouterr().err
    assert "COMPANIES_HOUSE_API_KEY" in err
    assert "developer.company-information.service.gov.uk" in err


def test_readme_markets_each_command_and_answers_the_faq():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert readme.count(SCALE_SENTENCE) >= 8
    assert APIFY_URL in readme
    assert NEWSLETTER_URL in readme
    assert STORE_URL in readme
    assert "Is this legal?" in readme
    assert "Not investment advice" in readme
    assert "Open Government Licence" in readme
    assert "COMPANIES_HOUSE_API_KEY" in readme


def test_contributing_suggests_repo_topics():
    text = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "uk-open-data" in text
    assert "Suggested GitHub description" in text


def test_no_telemetry_hosts_in_the_package():
    banned = ("google-analytics", "mixpanel", "segment.io", "sentry.io", "posthog", "amplitude.com")
    for path in (ROOT / "src").rglob("*.py"):
        text = path.read_text(encoding="utf-8").casefold()
        for host in banned:
            assert host not in text, f"{host} found in {path}"


def test_parser_requires_a_command():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_http_client_paces_sec_requests_and_surfaces_errors():
    clock = {"now": 0.0}
    slept = []

    def now():
        return clock["now"]

    def sleep(seconds):
        slept.append(seconds)
        clock["now"] += seconds

    opener = FakeOpener(b"{}")
    client = HttpClient(
        "ukopendata Dartiproductions@protonmail.com",
        min_interval=0.15,
        opener=opener,
        sleep=sleep,
        now=now,
    )
    assert client.get_json("https://efts.sec.gov/LATEST/search-index") == {}
    clock["now"] += 0.05
    client.get("https://efts.sec.gov/LATEST/search-index")
    assert slept == [pytest.approx(0.10)]
    assert opener.requests[0].headers["User-agent"] == "ukopendata Dartiproductions@protonmail.com"

    failing = HttpClient("ua", opener=FakeOpener(b"nope", status=429))
    with pytest.raises(HttpError) as caught:
        failing.get("https://example.test/limited")
    assert caught.value.status == 429
    assert "nope" in str(caught.value)
