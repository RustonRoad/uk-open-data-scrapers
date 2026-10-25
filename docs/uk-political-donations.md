# UK Political Donations Scraper: Electoral Commission API

> UK political donations & loans API from the Electoral Commission register: filter by party, donor, date and value; monitor new donations.

**Hosted versions:** see the [RawTrader UK data tools page](https://imrawtrader.beehiiv.com/p/data) · **Price:** $2 per 1,000 donation or loan records (USD, pay per result, no subscription)

## Use case

UK political donations and loans from the Electoral Commission register: filter by party, donor, donor type, date and value, and monitor new donations.

- **Journalists and newsrooms:** the biggest new donors to each party the day the Commission publishes.
- **Transparency researchers and campaigners:** company, trust and unincorporated-association donors, repeat donors, and loans.
- **Public affairs, lobbying and due-diligence teams:** check whether a company, director or client funds a party or MP.
- **Academics and data analysts:** clean JSON/CSV/Excel exports for analysis.

## Example input

```json
{
  "mode": "search",
  "kind": "donations",
  "daysBack": 180,
  "entityTypes": [
    "pp"
  ],
  "donorTypes": [
    "Company"
  ],
  "minValue": 50000
}
```

## Example output (real sample)

| recipientName | donorName | donorType | valueGbp | acceptedDate |
|---|---|---|---|---|
| The Rt Hon David Davis MP | Trailfinders Ltd | Company | 55000 | 2026-07-22 |
| Conservative and Unionist Party | Flowidea Limited | Company | 250000 | 2026-06-11 |
| Labour Party | Unite the Union | Trade Union | 217625 | 2026-05-01 |

Full field list, input options and FAQ: see the [RawTrader UK data tools page](https://imrawtrader.beehiiv.com/p/data).

## Run it from Python

```python
from apify_client import ApifyClient

client = ApifyClient("YOUR_APIFY_TOKEN")  # from https://console.apify.com/settings/integrations
# Actor id: see the RawTrader UK data tools page https://imrawtrader.beehiiv.com/p/data
run = client.actor("uk-political-donations").call(run_input={'mode': 'search', 'kind': 'donations', 'daysBack': 180, 'entityTypes': ['pp'], 'donorTypes': ['Company'], 'minValue': 50000})
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)
```

---

Related keywords: UK political donations data, Electoral Commission API, party donors.

[← All UK open data scrapers](../README.md) · Free weekly newsletter: [UK Industry & Bills](https://imrawtrader.beehiiv.com) · [@ImRawTrader on X](https://x.com/ImRawTrader)
