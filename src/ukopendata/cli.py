"""Command line interface. One command, one public source, a small result."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

from ukopendata import __version__
from ukopendata.errors import HttpError, SourceError, UsageError
from ukopendata.http import HttpClient
from ukopendata.marketing import footer_lines, help_epilog
from ukopendata.output import render
from ukopendata.sources import (
    biopharma,
    companies,
    donations,
    fuel,
    house_prices,
    price_cap,
    shorts,
    tenders,
)

GENERAL_USER_AGENT = f"ukopendata/{__version__} (Dartiproductions@protonmail.com)"


@dataclass
class CommandResult:
    rows: list[dict]
    columns: list[str]
    summary_lines: list[str] = field(default_factory=list)
    extra_footer: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    json_document: dict | None = None
    truncate: dict[str, int] = field(default_factory=dict)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ukopendata",
        description=(
            "Small, keyless (or free-key) commands for official UK open data. "
            "No telemetry. Each source keeps its own licence."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=help_epilog(),
    )
    parser.add_argument("--version", action="version", version=f"ukopendata {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    tenders_parser = subparsers.add_parser(
        "tenders",
        help="Recent UK public-sector notices",
        description=(
            "Search a small window of UK public-sector notices.\n\n"
            "Contracts Finder is the published search API. Find a Tender is the "
            "OCDS release API, filtered locally by keyword and region because that "
            "API has no keyword parameter. This is a sample of a few pages, not a "
            "full archive.\n\n"
            "Licence: Open Government Licence v3.0 (Cabinet Office)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=help_epilog(),
    )
    tenders_parser.add_argument("--keyword", required=True, help="Word or phrase to match")
    tenders_parser.add_argument("--region", help="For example London, Scotland, North West")
    tenders_parser.add_argument("--days", type=int, default=30, help="How many days back (default 30, max 366)")
    tenders_parser.add_argument("--limit", type=int, default=20, help="Maximum notices (default 20, max 100)")
    tenders_parser.add_argument("--status", help="Contracts Finder status, for example Open or Awarded")
    tenders_parser.add_argument(
        "--source",
        choices=("both", "contracts-finder", "find-a-tender"),
        default="both",
    )
    _add_output(tenders_parser)
    tenders_parser.set_defaults(func=command_tenders)

    shorts_parser = subparsers.add_parser(
        "shorts",
        help="Most-shorted UK shares from the FCA file",
        description=(
            "The largest aggregated net short positions in the FCA's current daily file.\n\n"
            "Not investment advice. The file is one row per issuer. Individual holders "
            "are not published.\n\n"
            "Source: Financial Conduct Authority, current aggregated net short positions."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=help_epilog(),
    )
    shorts_parser.add_argument("--top", type=int, default=20, help="How many issuers (default 20)")
    _add_output(shorts_parser)
    shorts_parser.set_defaults(func=command_shorts)

    donations_parser = subparsers.add_parser(
        "donations",
        help="Electoral Commission donation search",
        description=(
            "One page of the Electoral Commission donations register, newest accepted "
            "date first.\n\n"
            "Contains public sector information licensed under the Open Government Licence v3.0."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=help_epilog(),
    )
    donations_parser.add_argument("--query", help="Donor or recipient text, as the register search does")
    donations_parser.add_argument("--days", type=int, default=90, help="Accepted-date window when --from is omitted")
    donations_parser.add_argument("--from", dest="date_from", help="Accepted from, YYYY-MM-DD")
    donations_parser.add_argument("--to", dest="date_to", help="Accepted to, YYYY-MM-DD")
    donations_parser.add_argument("--min-value", type=float, default=0, help="Minimum value in GBP")
    donations_parser.add_argument("--donor-type", help="For example Individual, Company, Trade Union")
    donations_parser.add_argument("--limit", type=int, default=20)
    _add_output(donations_parser)
    donations_parser.set_defaults(func=command_donations)

    prices_parser = subparsers.add_parser(
        "house-prices",
        help="Land Registry price paid median and comps",
        description=(
            "Median and recent comparable sales for a postcode or outward code, "
            "from the HM Land Registry Price Paid yearly CSV (the same columns as "
            "the monthly file). The monthly file is a change file, so the median "
            "uses the yearly file. The download is cached under ~/.cache/ukopendata.\n\n"
            f"{house_prices.ATTRIBUTION}\n\n"
            f"{house_prices.ADDRESS_NOTE}"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=help_epilog(),
    )
    prices_parser.add_argument("postcode", help="Outward code or full postcode, for example SW11")
    prices_parser.add_argument("--months", type=int, default=6, help="Transfer-date window (default 6, max 18)")
    prices_parser.add_argument("--limit", type=int, default=20, help="How many comps to print. The median uses every match.")
    prices_parser.add_argument("--file", type=Path, help="Read this Price Paid CSV instead of downloading")
    prices_parser.add_argument(
        "--include-additional",
        action="store_true",
        help="Include category B (additional) sales as well as standard category A",
    )
    _add_output(prices_parser)
    prices_parser.set_defaults(func=command_house_prices)

    companies_parser = subparsers.add_parser(
        "companies",
        help="Search the Companies House register",
        description=(
            "Search company names on the Companies House public API.\n\n"
            "Requires a free key in COMPANIES_HOUSE_API_KEY. Create one at "
            "https://developer.company-information.service.gov.uk/ : register, "
            "create an application, and copy the REST API key. Do not commit it.\n\n"
            "Rate limit: 600 requests in 5 minutes. This command makes one request.\n"
            "Data: Crown copyright, Open Government Licence, Companies House API terms."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=help_epilog(),
    )
    companies_parser.add_argument("query", help="Name or words to search for")
    companies_parser.add_argument("--limit", type=int, default=10)
    _add_output(companies_parser)
    companies_parser.set_defaults(func=command_companies)

    company_parser = subparsers.add_parser(
        "company",
        help="One Companies House profile",
        description=(
            "Fetch one company profile by number.\n\n"
            "Requires COMPANIES_HOUSE_API_KEY. See `ukopendata companies --help` "
            "for how to create the free key."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=help_epilog(),
    )
    company_parser.add_argument("number", help="Company number, for example 00445790")
    _add_output(company_parser)
    company_parser.set_defaults(func=command_company)

    bio_parser = subparsers.add_parser(
        "biopharma-events",
        help="Biopharma 8-K and 6-K filings from EDGAR",
        description=(
            "US biopharma current reports (8-K and 6-K) filed on one date, from the "
            "SEC EDGAR full-text search. The default query looks for trial, FDA and "
            "related wording, then keeps filings whose SIC is a pharma or biologics "
            "code (2833–2836) when a SIC is present.\n\n"
            "Not investment advice.\n\n"
            "The User-Agent includes Dartiproductions@protonmail.com, and requests "
            "stay under 10 per second, as SEC fair access requires. EDGAR filings "
            "are US government works."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=help_epilog(),
    )
    bio_parser.add_argument(
        "--date",
        default=(date.today() - timedelta(days=1)).isoformat(),
        help="Filing date YYYY-MM-DD (default: yesterday)",
    )
    bio_parser.add_argument("--query", help="Replace the default biopharma search text")
    bio_parser.add_argument("--limit", type=int, default=20)
    _add_output(bio_parser)
    bio_parser.set_defaults(func=command_biopharma)

    cap_parser = subparsers.add_parser(
        "price-cap",
        help="Ofgem energy price cap headline rates",
        description=(
            "The current Ofgem price cap and the previous quarter: typical Direct "
            "Debit annual cost, and average electricity and gas unit rates and "
            "standing charges for England, Scotland and Wales.\n\n"
            "Source: Ofgem's published price cap page. Attribute figures to Ofgem."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=help_epilog(),
    )
    _add_output(cap_parser)
    cap_parser.set_defaults(func=command_price_cap)

    fuel_parser = subparsers.add_parser(
        "fuel",
        help="Weekly UK petrol and diesel pump prices",
        description=(
            "The latest weeks from the DESNZ weekly road fuel prices CSV "
            "(pence per litre, duty and VAT).\n\n"
            "Accredited official statistics. Open Government Licence v3.0. "
            "Department for Energy Security and Net Zero."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=help_epilog(),
    )
    fuel_parser.add_argument("--weeks", type=int, default=8, help="How many weeks (default 8, max 104)")
    _add_output(fuel_parser)
    fuel_parser.set_defaults(func=command_fuel)

    return parser


def _add_output(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--format", choices=("table", "csv", "json"), default="table")
    parser.add_argument("--output", type=Path, help="Write the data to this file. The footer stays on the terminal.")


def general_client() -> HttpClient:
    return HttpClient(
        GENERAL_USER_AGENT,
        min_interval=0.2,
        log=lambda message: print(message, file=sys.stderr),
    )


def sec_client() -> HttpClient:
    return HttpClient(biopharma.SEC_USER_AGENT, min_interval=biopharma.SEC_MIN_INTERVAL)


def command_tenders(args: argparse.Namespace) -> CommandResult:
    rows, warnings = tenders.search(
        general_client(),
        keyword=args.keyword,
        region=args.region,
        days=args.days,
        limit=args.limit,
        status=args.status,
        sources=args.source,
    )
    return CommandResult(
        rows=rows,
        columns=tenders.COLUMNS,
        warnings=warnings,
        truncate={"title": 72, "buyer": 40},
        extra_footer=[
            "Source: Contracts Finder and Find a Tender (Cabinet Office). "
            f"Open Government Licence v3.0. {tenders.OGL}"
        ],
    )


def command_shorts(args: argparse.Namespace) -> CommandResult:
    rows = shorts.fetch_top(general_client(), top=args.top)
    return CommandResult(
        rows=rows,
        columns=shorts.COLUMNS,
        extra_footer=[f"Source: FCA current aggregated net short positions. {shorts.PAGE_URL}"],
    )


def command_donations(args: argparse.Namespace) -> CommandResult:
    rows = donations.search(
        general_client(),
        query=args.query,
        days=args.days,
        date_from=args.date_from,
        date_to=args.date_to,
        min_value=args.min_value,
        donor_type=args.donor_type,
        limit=args.limit,
    )
    return CommandResult(
        rows=rows,
        columns=donations.COLUMNS,
        truncate={"recipient": 36, "donor": 32},
        extra_footer=[
            "Source: The Electoral Commission donations register. "
            "Open Government Licence v3.0. https://search.electoralcommission.org.uk/Search/Donations"
        ],
    )


def command_house_prices(args: argparse.Namespace) -> CommandResult:
    if args.file is not None and not args.file.is_file():
        raise UsageError(f"No such Price Paid file: {args.file}")
    summary, sales = house_prices.lookup(
        general_client(),
        args.postcode,
        months=args.months,
        limit=args.limit,
        include_additional=args.include_additional,
        csv_path=args.file,
    )
    return CommandResult(
        rows=sales,
        columns=house_prices.COLUMNS,
        summary_lines=[house_prices.summary_line(summary)],
        json_document={"summary": summary, "sales": sales},
        truncate={"street": 28, "town": 22},
        extra_footer=[house_prices.ATTRIBUTION, house_prices.ADDRESS_NOTE],
    )


def command_companies(args: argparse.Namespace) -> CommandResult:
    rows = companies.search(general_client(), args.query, limit=args.limit)
    return CommandResult(
        rows=rows,
        columns=companies.SEARCH_COLUMNS,
        truncate={"name": 42, "address": 48},
        extra_footer=[
            "Source: Companies House public API. Crown copyright, Open Government Licence, "
            f"subject to the API terms. Key: {companies.KEY_URL}"
        ],
    )


def command_company(args: argparse.Namespace) -> CommandResult:
    row = companies.profile(general_client(), args.number)
    return CommandResult(
        rows=[row],
        columns=companies.PROFILE_COLUMNS,
        truncate={"address": 64},
        extra_footer=[
            "Source: Companies House public API. Crown copyright, Open Government Licence, "
            "subject to the API terms."
        ],
    )


def command_biopharma(args: argparse.Namespace) -> CommandResult:
    rows = biopharma.search(sec_client(), on=args.date, query=args.query, limit=args.limit)
    return CommandResult(
        rows=rows,
        columns=biopharma.COLUMNS,
        summary_lines=[f"Filing date {args.date}"],
        truncate={"company": 36, "url": 48},
        extra_footer=[
            "Source: SEC EDGAR full-text search (efts.sec.gov). US government work. "
            "Fair access: at most 10 requests/second, User-Agent includes a contact address."
        ],
    )


def command_price_cap(args: argparse.Namespace) -> CommandResult:
    rows, note = price_cap.fetch(general_client())
    return CommandResult(
        rows=rows,
        columns=price_cap.COLUMNS,
        summary_lines=[note] if note else [],
        extra_footer=[f"Source: Ofgem energy price cap. {price_cap.PAGE_URL}"],
    )


def command_fuel(args: argparse.Namespace) -> CommandResult:
    rows = fuel.fetch_latest(general_client(), weeks=args.weeks)
    return CommandResult(
        rows=rows,
        columns=fuel.COLUMNS,
        extra_footer=[
            "Source: DESNZ weekly road fuel prices. Accredited official statistics. "
            f"Open Government Licence v3.0. {fuel.PAGE_URL}"
        ],
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = args.func(args)
    except UsageError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (SourceError, HttpError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    for warning in result.warnings:
        print(f"Warning: {warning}", file=sys.stderr)
    if not result.rows and not result.summary_lines:
        print("No rows.", file=sys.stderr)

    payload = render(
        result.rows,
        result.columns,
        args.format,
        truncate=result.truncate,
        json_document=result.json_document,
    )
    if result.summary_lines and args.format == "table":
        payload = "\n".join(result.summary_lines) + "\n" + payload
    elif result.summary_lines:
        for line in result.summary_lines:
            print(line, file=sys.stderr)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
        print(f"Wrote {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(payload)
        sys.stdout.flush()

    for line in footer_lines(args.command, result.extra_footer):
        print(line, file=sys.stderr)
    return 0
