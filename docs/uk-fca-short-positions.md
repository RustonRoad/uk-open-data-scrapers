# FCA Short Positions Scraper: UK Short Interest Tracker

> UK short interest API from the official FCA net short positions report: short % by company and ISIN, daily change alerts and issuer history.

**Hosted versions:** see the [RawTrader UK data tools page](https://imrawtrader.beehiiv.com/p/data) · **Price:** $2 per 1,000 position rows; $10 per 1,000 change alerts (USD, pay per result, no subscription)

## Use case

UK short interest from the official FCA net short positions report: short % by company and ISIN, new/increased/decreased/closed position alerts and issuer history.

- **Traders and investors:** spot the most shorted UK stocks (FTSE 100, FTSE 250, AIM) and short squeezes in the making.
- **Hedge funds and analysts:** a clean daily UK short-interest feed for models, screens and dashboards.
- **Investor relations teams:** get alerted the day short interest in your company changes.
- **Financial journalists:** daily "most shorted UK shares" and "biggest increases in short interest" stories.
- **Risk and compliance:** monitor short pressure on holdings and counterparties.

## Example input

```json
{
  "mode": "current",
  "minShortPct": 3,
  "sortBy": "netShortPct"
}
```

## Example output (real sample)

| issuerName | isin | changeType | oldShortPct | newShortPct | reportDate |
|---|---|---|---|---|---|
| 80 Mile Plc | GB00BFD3VF20 | new | – | 0.9 | 2026-10-20 |
| 3I GROUP PLC | GB00B1YW4409 | increased | 0.77 | 1.07 | 2026-10-20 |
| 4IMPRINT GROUP PLC | GB0006640972 | decreased | 0.5 | 0.2 | 2026-10-20 |

Full field list, input options and FAQ: see the [RawTrader UK data tools page](https://imrawtrader.beehiiv.com/p/data).

## Run it from Python

```python
from apify_client import ApifyClient

client = ApifyClient("YOUR_APIFY_TOKEN")  # from https://console.apify.com/settings/integrations
# Actor id: see the RawTrader UK data tools page https://imrawtrader.beehiiv.com/p/data
run = client.actor("uk-fca-short-positions").call(run_input={'mode': 'current', 'minShortPct': 3, 'sortBy': 'netShortPct'})
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)
```

---

Related keywords: FCA short positions, most shorted UK stocks, UK short interest API.

[← All UK open data scrapers](../README.md) · Free weekly newsletter: [UK Industry & Bills](https://imrawtrader.beehiiv.com) · [@ImRawTrader on X](https://x.com/ImRawTrader)
