# ukopendata

[![Tests](https://github.com/RustonRoad/uk-open-data-scrapers/actions/workflows/tests.yml/badge.svg)](https://github.com/RustonRoad/uk-open-data-scrapers/actions/workflows/tests.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**A small, free Python CLI for official UK open data: tenders, short positions, donations, house prices, Companies House, the energy price cap and pump prices.**

No account, no telemetry, no tracking. Each command does one job and prints a table, CSV or JSON. The data stays under the publisher's licence. The code is MIT.

```text
$ ukopendata house-prices SW11 --months 6 --limit 3
SW11  2026-04-23 to 2026-10-23  sales=3  median=£400,000  min=£250,000  max=£500,000  category=A
date        price_gbp  type           tenure     new_build  paon  street          town    postcode
----------  ---------  -------------  ---------  ---------  ----  --------------  ------  --------
2026-08-01  400000     flat           leasehold  False      12    LATCHMERE ROAD  LONDON  SW11 1AA
2026-07-01  500000     semi-detached  freehold   False      2     COMYN ROAD      LONDON  SW11 3FF
2026-06-15  250000     terraced       freehold   False      3     SHELGATE ROAD   LONDON  SW11 4BB
```

The median uses every matching standard sale. The table is the newest comps. This block is the real layout from a tiny sample file, not a live Land Registry extract.

## Quick start

Python 3.10 or newer.

```bash
pip install "ukopendata @ git+https://github.com/RustonRoad/uk-open-data-scrapers.git"
```

From a checkout:

```bash
pip install -e .
ukopendata --help
ukopendata tenders --keyword roofing --region London
ukopendata shorts --top 20
ukopendata donations --min-value 50000 --days 180
ukopendata house-prices SW11 --months 6
ukopendata price-cap
ukopendata fuel --weeks 8
ukopendata biopharma-events --date 2026-10-22
```

`--format table` (the default), `--format csv` or `--format json`. `--output path.csv` writes the data to a file. The source line and the links below it go to the terminal, not into the file, so a CSV stays a CSV.

Companies House is the one command that needs a free key. See [Companies](#companies-and-company).

## Commands

### tenders

```bash
ukopendata tenders --keyword roofing --region London
ukopendata tenders --keyword software --days 7 --status Open --format csv
```

Contracts Finder is searched with its published API (keyword, region, date). Find a Tender has no keyword parameter on the OCDS feed, so the command reads a few pages of that window and keeps notices whose title or description matches. The live Find a Tender API returns an empty package if several stages are sent together, so the default is a single stage, `tender`. Use `--stage award`, `--stage planning` or `--stage all`. Region names such as London, Scotland and North West are mapped to the NUTS code Find a Tender puts on the buyer. Default is 30 days and 20 notices.

Need this at scale, scheduled, with alerts? Use the hosted version on Apify: https://imrawtrader.beehiiv.com/p/data. The tenders actor is listed on that page.

### shorts

```bash
ukopendata shorts --top 20
```

The FCA's current aggregated net short positions file, one row per issuer, largest first. Individual holders are not in the file. **Not investment advice.**

Need this at scale, scheduled, with alerts? Use the hosted version on Apify: https://imrawtrader.beehiiv.com/p/data. The short interest actor is listed on that page.

### donations

```bash
ukopendata donations --query "Labour Party" --days 180 --min-value 50000
ukopendata donations --from 2026-01-01 --to 2026-06-30 --donor-type Company --limit 20
```

One or a few pages of the Electoral Commission donations search, newest accepted date first. `--min-value` and `--donor-type` are applied to those pages, not to the whole historical register.

Need this at scale, scheduled, with alerts? Use the hosted version on Apify: https://imrawtrader.beehiiv.com/p/data. The donations actor is listed on that page.

### house-prices

```bash
ukopendata house-prices SW11 --months 6
ukopendata house-prices "SW11 1AA" --months 12 --limit 15 --format json
ukopendata house-prices SW11 --file ~/Downloads/pp-2026.csv
```

Median and comps from the HM Land Registry Price Paid yearly CSV (same columns as the monthly file). `SW11` matches that outward code and does not match `SW1`. Category B sales and deleted records are left out unless you pass `--include-additional`. The yearly file is about 70–170 MB; it is cached in `~/.cache/ukopendata` and reused until the publisher's file size or last-modified date changes.

The monthly CSV on GOV.UK is a change file (additions, changes, deletions), so it is the wrong input for a median. Use the yearly file, or pass a CSV you already trust with `--file`.

The linked-data API at `landregistry.data.gov.uk` is not used. Its robots.txt disallows `/data` and `/sparql`.

Contains HM Land Registry data © Crown copyright and database right 2021. This data is licensed under the Open Government Licence v3.0.

Address fields include Royal Mail PAF and Ordnance Survey data. That address data may be used for personal and/or non-commercial use, and displayed to provide residential property price information. Any other use needs permission from Royal Mail: address.management@royalmail.com.

Need this at scale, scheduled, with alerts? Use the hosted version on Apify: https://imrawtrader.beehiiv.com/p/data

### companies and company

```bash
export COMPANIES_HOUSE_API_KEY=your-key   # do not commit this
ukopendata companies "roofing" --limit 10
ukopendata company 00445790
```

How to get the free key:

1. Open [developer.company-information.service.gov.uk](https://developer.company-information.service.gov.uk/) and register.
2. Create an application and copy the REST API key.
3. Export it as `COMPANIES_HOUSE_API_KEY`. The command sends it as HTTP Basic (the key is the username, the password is empty). It is not written to a file and it is not put in the URL.

The published limit is 600 requests in 5 minutes. Each command makes one. A numeric company number is padded to 8 digits.

Need this at scale, scheduled, with alerts? Use the hosted version on Apify: https://imrawtrader.beehiiv.com/p/data. The companies actor is listed on that page.

### biopharma-events

```bash
ukopendata biopharma-events --date 2026-10-22
ukopendata biopharma-events --date 2026-10-22 --query '"Phase 3" OR PDUFA' --limit 10
```

8-K and 6-K filings from the SEC EDGAR full-text search for one filing date. The default query looks for pharmaceutical, biotech, clinical-trial and FDA wording. When a filing has a SIC code, it is kept only if that code is 2833, 2834, 2835 or 2836. Exhibits of the same accession are collapsed to one row. The default date is yesterday.

Every request uses the User-Agent `ukopendata Dartiproductions@protonmail.com` and waits so the command stays under the SEC's 10 requests per second. **Not investment advice.**

Need this at scale, scheduled, with alerts? Use the hosted version on Apify: https://imrawtrader.beehiiv.com/p/data

### price-cap

```bash
ukopendata price-cap
```

The Ofgem headline cap for a typical Direct Debit household in England, Scotland and Wales, plus electricity and gas unit rates and standing charges for the current quarter and the one before it. Regional tables on the Ofgem page are loaded in the browser; this command reads the headline table in the published HTML.

Need this at scale, scheduled, with alerts? Use the hosted version on Apify: https://imrawtrader.beehiiv.com/p/data

### fuel

```bash
ukopendata fuel --weeks 8
```

The latest weeks of UK average petrol and diesel pump prices, duty and VAT, from the Department for Energy Security and Net Zero. The GOV.UK content API is used to find the current CSV, because the file id changes when the series is updated.

Need this at scale, scheduled, with alerts? Use the hosted version on Apify: https://imrawtrader.beehiiv.com/p/data

Newsletter: https://ukindustryandbills.substack.com · Data store: https://payhip.com/UKIndustryBills

## Sources and licences

| Command | Source | Access | Licence and attribution |
|---|---|---|---|
| `tenders` | [Contracts Finder search](https://www.contractsfinder.service.gov.uk/apidocumentation/) and [Find a Tender OCDS](https://www.find-tender.service.gov.uk/api/1.0/ocdsReleasePackages) | Keyless official APIs. A few pages per command. | Open Government Licence v3.0, Cabinet Office |
| `shorts` | [FCA current aggregated net short positions CSV](https://www.fca.org.uk/publication/documents/aggregated-current-net-short-positions.csv) | Keyless file. The URL has no query string; the FCA robots.txt disallows query-string URLs. | FCA publication. Attribute the FCA. Not investment advice. |
| `donations` | [Electoral Commission donations search](https://search.electoralcommission.org.uk/Search/Donations) | Keyless search the public site uses, one or a few pages. | Open Government Licence v3.0 |
| `house-prices` | [Price Paid yearly CSV](https://price-paid-data.publicdata.landregistry.gov.uk/pp-2026.csv) linked from [GOV.UK](https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads) | Keyless bulk file, cached locally. | OGL v3.0. Use the Land Registry attribution printed by the command. Address data: Royal Mail and Ordnance Survey conditions above. |
| `companies`, `company` | [Companies House public API](https://developer.company-information.service.gov.uk/) | Free key in `COMPANIES_HOUSE_API_KEY`. One request. 600 per 5 minutes. | Crown copyright, OGL, plus the Companies House API terms |
| `biopharma-events` | [EDGAR full-text search](https://efts.sec.gov/LATEST/search-index) | Keyless. User-Agent with a contact address. Under 10 requests/second. [Fair access](https://www.sec.gov/os/accessing-edgar-data). | US government work. Not investment advice. |
| `price-cap` | [Ofgem price cap page](https://www.ofgem.gov.uk/your-energy-supply/your-energy-bill/energy-price-cap-unit-rates-and-standing-charges) | Keyless HTML of the headline table. The page is allowed by Ofgem's robots.txt. | Attribute Ofgem |
| `fuel` | [Weekly road fuel prices](https://www.gov.uk/government/statistics/weekly-road-fuel-prices) via the [GOV.UK content API](https://www.gov.uk/api/content/government/statistics/weekly-road-fuel-prices) | Keyless. gov.uk robots.txt allows this path. | OGL v3.0. Accredited official statistics, DESNZ |

The code licence does not license the data. Details are in [LICENSING.md](LICENSING.md).

## What was left out

These are on the hosted side, or they are not a fit for a keyless official command:

| Source | Why it is not a command |
|---|---|
| Google Trends | Not an official open API. Automated access is outside Google's published terms. |
| BNPL shop checker | Reads private shop websites. robots.txt and terms differ by site. |
| The Gazette insolvency notices | No single documented keyless OGL bulk file or search API used here. |
| Visa sponsor register | The public spreadsheet is official, but the useful job is a diff of a large register, which needs stored state. |
| OPSS, FSA and MHRA recalls | Three sites, no shared keyless API or bulk file. |
| FSA food hygiene ratings | The FHRS API is official and keyless. It is a good next command; this first release stays with the sources above. |
| Land Registry linked data and SPARQL | `landregistry.data.gov.uk/robots.txt` disallows `/data` and `/sparql`. The yearly CSV is the allowed bulk file. |

## Schedule a CSV without hosting anything

[`.github/workflows/daily-tenders.example.yml`](.github/workflows/daily-tenders.example.yml) searches tenders and commits a CSV. It is `workflow_dispatch` only. It does not run on a timer, so a fork does not call the APIs every morning. Turn on a cron yourself if you want that, and keep the limit small.

## FAQ

**Is this legal?**
The commands call official APIs and bulk files that are published for reuse, and they skip paths disallowed by robots.txt. Most of the UK datasets are Open Government Licence v3.0. You still have to follow each source's conditions, in particular the Royal Mail and Ordnance Survey conditions on Price Paid address data, the Companies House API terms, and the SEC fair-access rules. You are responsible for what you do with personal data (UK GDPR), including names of donors.

**Not investment advice**
`shorts` and `biopharma-events` repeat figures that regulators already publish. They are not a recommendation to buy, sell or hold a security, and they are not a forecast. Short interest is an aggregated disclosure. An 8-K is the company's filing, not this project's opinion.

**How much does this cost?**
The CLI is free. Companies House needs a free API key and the other commands need none. The hosted actors on Apify are the paid, scheduled versions with alerts. Apify's free plan includes monthly credit.

**Does it phone home?**
No. There is no telemetry, analytics or tracking. The only network calls are the ones you asked for, to the public source. A User-Agent identifies the tool and, for EDGAR, the contact address the SEC requires.

**Can I get only new rows every day?**
Not in this CLI. That needs stored state and a schedule. The hosted actors do it, and the example GitHub workflow commits a tenders CSV when you run it.

**Where do the actor docs go?**
The pages in [`docs/`](docs/) describe the hosted actors. The CLI is the free, local version of the same idea, for the sources that can be read this way.

## Hosted actors

The same catalogue, when you want a schedule, a webhook, or a larger run. Prices are USD, pay per result. Hosted versions: see the [RawTrader UK data tools page](https://imrawtrader.beehiiv.com/p/data).

| Actor | What it does | Hosted |
|---|---|---|
| [UK Companies House feed](docs/uk-companies-house-feed.md) | New companies by SIC and region, plus status alerts | [uk-companies-house-feed](https://imrawtrader.beehiiv.com/p/data) |
| [UK public tenders](docs/uk-public-tenders-feed.md) | Find a Tender, Contracts Finder, optional TED | [uk-public-tenders-feed](https://imrawtrader.beehiiv.com/p/data) |
| [FCA short positions](docs/uk-fca-short-positions.md) | Short interest and change alerts | [uk-fca-short-positions](https://imrawtrader.beehiiv.com/p/data) |
| [Gazette insolvency notices](docs/uk-gazette-insolvency-notices.md) | Winding-up petitions, administrations, liquidations | [uk-gazette-insolvency-notices](https://imrawtrader.beehiiv.com/p/data) |
| [Visa sponsor register](docs/uk-visa-sponsor-register-monitor.md) | New, removed and downgraded sponsors | [uk-visa-sponsor-register-monitor](https://imrawtrader.beehiiv.com/p/data) |
| [Food hygiene ratings](docs/uk-food-hygiene-ratings.md) | FHRS search and new-restaurant leads | [uk-food-hygiene-ratings](https://imrawtrader.beehiiv.com/p/data) |
| [Product safety recalls](docs/uk-product-safety-recalls.md) | OPSS, FSA and MHRA alerts | [uk-product-safety-recalls](https://imrawtrader.beehiiv.com/p/data) |
| [Political donations](docs/uk-political-donations.md) | Electoral Commission donations and loans | [uk-political-donations](https://imrawtrader.beehiiv.com/p/data) |
| [Google Trends UK](docs/uk-google-trends.md) | Interest, regions and related queries | [uk-google-trends](https://imrawtrader.beehiiv.com/p/data) |
| [BNPL checker](docs/uk-bnpl-merchant-detector.md) | Klarna, Clearpay and PayPal Pay in 3 | [uk-bnpl-merchant-detector](https://imrawtrader.beehiiv.com/p/data) |

## Develop

```bash
pip install -e ".[dev]"
pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add a source, and for a suggested GitHub description and topic list.

---

Newsletter: [UK Industry & Bills](https://ukindustryandbills.substack.com) · Data store: [payhip.com/UKIndustryBills](https://payhip.com/UKIndustryBills)
