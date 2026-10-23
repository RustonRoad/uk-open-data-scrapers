# UK Tenders Scraper & API: Find a Tender, Contracts Finder, TED

> UK tenders API: new Find a Tender & Contracts Finder notices, contract awards and EU TED. Filter by keyword, CPV, value, region. Daily bid leads.

**Run it on Apify:** [https://apify.com/seaf999ield/uk-public-tenders-feed](https://apify.com/seaf999ield/uk-public-tenders-feed) · **Price:** $3 per 1,000 tender or award notices (USD, pay per result, no subscription)

## Use case

New UK public-sector tenders and contract awards from Find a Tender and Contracts Finder, with optional EU TED. Filter by keyword, CPV code, value and region.

- **Bid and sales teams:** a daily alert for new tenders in your CPV codes, value band and region.
- **Agencies and consultancies:** track the councils, NHS trusts and universities you sell to.
- **Market research:** see who is winning which contracts and at what value. Uses award notices.
- **CRM and BI:** schedule a run every morning and push it into HubSpot, Sheets or BigQuery.

## Example input

```json
{
  "daysBack": 3,
  "keywords": [
    "software",
    "digital",
    "cloud",
    "data",
    "IT"
  ],
  "matchTitleOnly": true,
  "onlyOpen": true,
  "noticeTypes": [
    "tender"
  ]
}
```

## Example output (real sample)

| source | title | buyerName | valueGBP | deadline | cpvCodes |
|---|---|---|---|---|---|
| Contracts Finder | Short Breaks for 1324785 | East Riding of Yorkshire Council | 4000 | 2026-08-21 | 85000000 |
| Find a Tender | Estate Agency Services for Herefordshire Council's Commerci… | Herefordshire Council | 450000 | 2026-10-26 | – |
| Contracts Finder | 021352 - Videography for the Knowsley Business Awards | Knowsley Council | 52725 | 2026-09-03 | 79416200, 79952000 |

Full field list, input options and FAQ: see the actor page on the [Apify Store](https://apify.com/seaf999ield/uk-public-tenders-feed).

## Run it from Python

```python
from apify_client import ApifyClient

client = ApifyClient("YOUR_APIFY_TOKEN")  # from https://console.apify.com/settings/integrations
run = client.actor("seaf999ield/uk-public-tenders-feed").call(run_input={'daysBack': 3, 'keywords': ['software', 'digital', 'cloud', 'data', 'IT'], 'matchTitleOnly': True, 'onlyOpen': True, 'noticeTypes': ['tender']})
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)
```

---

Related keywords: UK tenders API, Contracts Finder scraper, Find a Tender API, public sector bid leads.

[← All UK open data scrapers](../README.md) · Free weekly newsletter: [UK Industry & Bills](https://imrawtrader.beehiiv.com) · [@ImRawTrader on X](https://x.com/ImRawTrader)
