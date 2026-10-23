# Contributing

`ukopendata` is a small CLI. A command should do one job, call an official
source that allows automated access, and stay small (one request, or a few
pages, or one bulk file filtered locally).

## Run the tests

```bash
pip install -e ".[dev]"
pytest
```

The tests use recorded fixtures. They must not call a live source. `tests/conftest.py`
blocks `socket.create_connection` for that reason. A manual smoke test against
the live sources is separate, and it should use the same small limits as the
commands (do not download `pp-complete.csv`, and do not page through an entire
register).

## Add a source

Only if all of these are true:

- The publisher provides an official API or a bulk file, and documents that
  automated access is allowed.
- It is keyless, or it uses a free key the user creates and stores in an
  environment variable. Never commit a key, a token or a sample `.env`.
- `robots.txt` does not disallow the path. If it does, do not fetch that path.
  The Land Registry linked-data API is the example: `landregistry.data.gov.uk`
  disallows `/data` and `/sparql`, so Price Paid is read from the yearly CSV
  instead.
- The published rate limit is respected. SEC EDGAR is at most 10 requests per
  second, with a User-Agent that includes a contact address.
- The command prints the publisher's licence and the attribution they ask for.
  The code licence (MIT) does not replace the data licence.
- Unit tests parse a small fixture. They do not open a socket.

Skip a source, and say why in the pull request, when the only way to read it
is to scrape a site whose terms or robots.txt do not allow it.

## Do not add

- Telemetry, analytics, phone-home or tracking of any kind.
- Retries that hide a 429 or a 403. Print the error and stop.
- A default schedule in GitHub Actions. The tenders workflow is
  `workflow_dispatch` only so the repository does not call the source every day.

## Suggested GitHub description

Paste this into the repository description (Settings → General):

```
Free MIT-licensed Python CLI for official UK open data: public tenders, FCA short positions, political donations, Land Registry prices, Companies House, the Ofgem price cap and weekly road fuel prices.
```

## Suggested GitHub topics

```
uk-open-data
open-data
open-government-licence
python
cli
government-data
public-procurement
contracts-finder
companies-house
land-registry
price-paid-data
fca
ofgem
sec-edgar
```

These are suggestions for the repository settings. This file does not change
them on its own.
