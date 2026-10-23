# UK Insolvency Notices Scraper: Gazette Winding-Up Feed

> UK insolvency API from The Gazette: winding-up petitions, administrations and liquidations with company number, IP and postcode. Daily monitor.

**Run it on Apify:** [https://apify.com/seaf999ield/uk-gazette-insolvency-notices](https://apify.com/seaf999ield/uk-gazette-insolvency-notices) · **Price:** $3 per 1,000 notices; $10 per 1,000 new-notice alerts (USD, pay per result, no subscription)

## Use case

Daily UK insolvency notices from The Gazette: winding-up petitions and orders, administrations and liquidations, with company number and postcode.

- **Credit controllers and trade-credit insurers:** spot customers facing a winding-up petition before an order is made.
- **Insolvency practitioners, turnaround advisers and asset buyers:** a daily list of new administrations and liquidations by region.
- **Lenders, factoring and invoice-finance firms:** monitor portfolio and debtor risk.
- **Journalists and analysts:** track insolvencies by sector and area.

## Example output (real sample)

| noticeTypeLabel | companyName | companyNumber | publishedDate | postcode |
|---|---|---|---|---|
| Creditors' voluntary liquidation | HIMALAYAN RESTAURANT LTD | 12484472 | 2026-10-20 | GU15 2QN |
| Winding-up petition | MY BUILDER GROUP LTD | 13059359 | 2026-10-20 | HA9 6PL |
| Winding-up order | COURIER SOLUTIONS EDINBURGH LIMITED | SC660367 | 2026-10-20 | DD1 4QB |

Full field list, input options and FAQ: see the actor page on the [Apify Store](https://apify.com/seaf999ield/uk-gazette-insolvency-notices).

## Run it from Python

```python
from apify_client import ApifyClient

client = ApifyClient("YOUR_APIFY_TOKEN")  # from https://console.apify.com/settings/integrations
run = client.actor("seaf999ield/uk-gazette-insolvency-notices").call(run_input={})
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)
```

---

Related keywords: UK insolvency notices, Gazette winding-up petitions, liquidations list.

[← All UK open data scrapers](../README.md) · Free weekly newsletter: [UK Industry & Bills](https://imrawtrader.beehiiv.com) · [@ImRawTrader on X](https://x.com/ImRawTrader)
