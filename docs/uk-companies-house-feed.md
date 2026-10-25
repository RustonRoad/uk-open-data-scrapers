# UK Companies House Scraper: New Companies Feed & Alerts

> Companies House API feed: daily new UK company incorporations by SIC code, region & postcode, plus liquidation and dissolution alerts. B2B leads.

**Hosted versions:** see the [RawTrader UK data tools page](https://imrawtrader.beehiiv.com/p/data) · **Price:** $3 per 1,000 company records; $10 per 1,000 status-change alerts (USD, pay per result, no subscription)

## Use case

Daily feed of new UK company incorporations from the official Companies House API, filtered by SIC code, region and postcode, plus liquidation, administration and dissolution alerts for a watchlist.

- **Accountants and bookkeepers:** every new Ltd in your town each morning. They all need a year-end, a confirmation statement and a bank account, and you get the accounts due dates with each record.
- **Business insurers and brokers:** new companies by SIC code (construction, hospitality, haulage, care) for public liability, fleet and professional indemnity cover.
- **Banks, fintechs and payment providers:** a new-business acquisition feed for business accounts, card terminals and lending.
- **Web, marketing and IT agencies:** new businesses by region that need a website, domain, branding and IT.
- **New-business prospecting by SIC and region:** e.g. all new restaurants (56101) in Greater Manchester, or all new software companies (62012) in Scotland.
- **Supplier and customer due diligence / credit control:** watch your suppliers, customers or portfolio companies. Get alerted on liquidation, administration, strike-off and overdue accounts before you ship goods or extend credit.
- **Insolvency, turnaround and asset-recovery firms:** a daily list of companies entering administration or receivership and of new dissolutions.

## Example input

```json
{
  "mode": "new_companies",
  "daysBack": 1,
  "sicCodes": [
    "62012",
    "62020",
    "62090"
  ],
  "regions": [
    "London",
    "South East"
  ],
  "maxResults": 500
}
```

## Example output (real sample)

| companyNumber | companyName | incorporationDate | sicCodes | postcode | region |
|---|---|---|---|---|---|
| 17527344 | TAJ & RAFIQUE LTD | 2026-10-19 | 86210 | WA15 0LR | North West |
| SC906275 | MCDONALD DELIVERY LTD | 2026-10-19 | 49410 | ML1 4BY | Scotland |
| 17527340 | LARD ETC LTD | 2026-10-19 | 56101 | OX1 2HP | South East |

Full field list, input options and FAQ: see the [RawTrader UK data tools page](https://imrawtrader.beehiiv.com/p/data).

## Run it from Python

```python
from apify_client import ApifyClient

client = ApifyClient("YOUR_APIFY_TOKEN")  # from https://console.apify.com/settings/integrations
# Actor id: see the RawTrader UK data tools page https://imrawtrader.beehiiv.com/p/data
run = client.actor("uk-companies-house-feed").call(run_input={'mode': 'new_companies', 'daysBack': 1, 'sicCodes': ['62012', '62020', '62090'], 'regions': ['London', 'South East'], 'maxResults': 500})
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)
```

---

Related keywords: Companies House API, new UK companies list, SIC code leads, company liquidation alerts.

[← All UK open data scrapers](../README.md) · Free weekly newsletter: [UK Industry & Bills](https://imrawtrader.beehiiv.com) · [@ImRawTrader on X](https://x.com/ImRawTrader)
