# Google Trends Scraper UK: Interest, Regions & Related Queries

> Google Trends scraper & API for the UK and any country: interest over time, by region (England, Scotland, Wales, NI), related queries & topics.

**Run it on Apify:** [https://apify.com/seaf999ield/uk-google-trends](https://apify.com/seaf999ield/uk-google-trends) · **Price:** $2 per 1,000 result rows (error and no-data rows are free) (USD, pay per result, no subscription)

## Use case

Google Trends for the UK and any country: interest over time, interest by region and nation (England, Scotland, Wales, NI), and rising/top related queries.

- **SEO and content teams:** find rising UK search terms and seasonal peaks before competitors.
- **Ecommerce sellers and resellers:** time stock and promotions (Black Friday, Vinted, seasonal products) with UK demand data.
- **Journalists and analysts:** chart public interest in the energy price cap, cost of living, redundancies or elections by UK nation.
- **Marketers and agencies:** compare brands or products on one 0–100 scale across England, Scotland, Wales and Northern Ireland.
- **Researchers and data teams:** schedule recurring pulls into Sheets, BigQuery or dashboards via the API.

## Example input

```json
{
  "searchTerms": [
    "energy price cap"
  ],
  "geos": [
    "GB"
  ],
  "ukNationsBundle": true,
  "timeframe": "today 3-m"
}
```

## Example output (real sample)

| termsText | geoName | term | average | latest | peak | peakDate | recentChangePct |
|---|---|---|---|---|---|---|---|
| energy price cap vs ofgem vs energy bills | Scotland | energy price cap | 13 | 13 | 52 | 2026-09-13 | -38.8 |
| energy price cap vs ofgem vs energy bills | United Kingdom | energy price cap | 24 | 14 | 61 | 2026-05-24 | -48.4 |
| energy price cap | United Kingdom | energy price cap | 40.1 | 24 | 100 | 2026-05-24 | -48.7 |

Full field list, input options and FAQ: see the actor page on the [Apify Store](https://apify.com/seaf999ield/uk-google-trends).

## Run it from Python

```python
from apify_client import ApifyClient

client = ApifyClient("YOUR_APIFY_TOKEN")  # from https://console.apify.com/settings/integrations
run = client.actor("seaf999ield/uk-google-trends").call(run_input={'searchTerms': ['energy price cap'], 'geos': ['GB'], 'ukNationsBundle': True, 'timeframe': 'today 3-m'})
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)
```

---

Related keywords: Google Trends scraper UK, Google Trends API, UK search interest by region.

[← All UK open data scrapers](../README.md) · Free weekly newsletter: [UK Industry & Bills](https://imrawtrader.beehiiv.com) · [@ImRawTrader on X](https://x.com/ImRawTrader)
