# UK Open Data Scrapers & APIs

**Ready-made scrapers and APIs for UK public data:** Companies House, public tenders, FCA short positions, Gazette insolvency notices, Home Office visa sponsors, FSA food hygiene ratings, product recalls, Electoral Commission donations, Google Trends UK and BNPL checkout detection. Each one runs on [Apify](https://apify.com/seaf999ield), returns clean JSON/CSV/Excel, and is priced per result.

## Why UK open data?

The UK publishes a lot of useful official data: new company registrations, government contracts, short-selling disclosures, insolvency notices, sponsor licences, hygiene inspections, safety recalls and political donations. It's spread across dozens of portals, though, and each has its own formats, rate limits and quirks. These actors turn those sources into structured, schedulable feeds for:

- **Lead generation:** new companies by SIC code and region, newly opened restaurants, newly licensed visa sponsors, open tenders in your CPV codes, shops without BNPL.
- **Research and journalism:** short interest, insolvencies, donations and recalls as clean datasets for analysis and stories.
- **Monitoring and compliance:** daily change alerts for suppliers, customers, portfolios, competitors and product categories.

Each actor can run on a schedule, has a REST API, and can push results to Google Sheets, webhooks, Make, Zapier, n8n, HubSpot or BigQuery.

## All actors

| Actor | What it does | Who it's for | Price per 1,000 results | Apify Store |
|---|---|---|---|---|
| [UK Companies House Scraper: New Companies Feed & Alerts](docs/uk-companies-house-feed.md) | Daily feed of new UK company incorporations from the official Companies House API, filtered by SIC code, region and postcode, plus liquidation, administration and dissolution alerts for a watchlist. | Accountants, insurers and brokers, banks and fintechs, agencies, credit control | $3 | [apify.com/seaf999ield/uk-companies-house-feed](https://apify.com/seaf999ield/uk-companies-house-feed) |
| [UK Tenders Scraper & API: Find a Tender, Contracts Finder, TED](docs/uk-public-tenders-feed.md) | New UK public-sector tenders and contract awards from Find a Tender and Contracts Finder, with optional EU TED. Filter by keyword, CPV code, value and region. | Bid and sales teams, agencies and consultancies, market researchers | $3 | [apify.com/seaf999ield/uk-public-tenders-feed](https://apify.com/seaf999ield/uk-public-tenders-feed) |
| [FCA Short Positions Scraper: UK Short Interest Tracker](docs/uk-fca-short-positions.md) | UK short interest from the official FCA net short positions report: short % by company and ISIN, new/increased/decreased/closed position alerts and issuer history. | Traders and investors, hedge funds and analysts, IR teams, financial journalists | $2 | [apify.com/seaf999ield/uk-fca-short-positions](https://apify.com/seaf999ield/uk-fca-short-positions) |
| [UK Insolvency Notices Scraper: Gazette Winding-Up Feed](docs/uk-gazette-insolvency-notices.md) | Daily UK insolvency notices from The Gazette: winding-up petitions and orders, administrations and liquidations, with company number and postcode. | Credit controllers, trade-credit insurers, insolvency practitioners, lenders, journalists | $3 | [apify.com/seaf999ield/uk-gazette-insolvency-notices](https://apify.com/seaf999ield/uk-gazette-insolvency-notices) |
| [UK Visa Sponsor Register Scraper & Monitor (Home Office)](docs/uk-visa-sponsor-register-monitor.md) | Tracks the Home Office Register of Licensed Sponsors: new sponsors, removals and A-to-B rating downgrades by town and visa route, with optional Companies House enrichment. | Recruitment agencies, sponsor job boards, HR and compliance, researchers | $1 (snapshot) / $10 (changes) | [apify.com/seaf999ield/uk-visa-sponsor-register-monitor](https://apify.com/seaf999ield/uk-visa-sponsor-register-monitor) |
| [UK Food Hygiene Ratings Scraper & New Restaurant Leads](docs/uk-food-hygiene-ratings.md) | Search FSA food hygiene ratings by council, postcode, business type or rating, get leads for newly opened restaurants and takeaways, and monitor rating changes. | Suppliers to hospitality, food safety consultants, landlords and franchisors, delivery apps | $2 | [apify.com/seaf999ield/uk-food-hygiene-ratings](https://apify.com/seaf999ield/uk-food-hygiene-ratings) |
| [UK Product Recalls Scraper: OPSS, FSA & MHRA Safety Alerts](docs/uk-product-safety-recalls.md) | One UK recall and safety-alert feed: OPSS product recalls (toys, baby, electrical), FSA food and allergy alerts, and MHRA medicine and device alerts. | Online sellers and marketplaces, retailers and importers, compliance/QA, pharmacies | $2 | [apify.com/seaf999ield/uk-product-safety-recalls](https://apify.com/seaf999ield/uk-product-safety-recalls) |
| [UK Political Donations Scraper: Electoral Commission API](docs/uk-political-donations.md) | UK political donations and loans from the Electoral Commission register: filter by party, donor, donor type, date and value, and monitor new donations. | Journalists, transparency researchers, public affairs and due-diligence teams, academics | $2 | [apify.com/seaf999ield/uk-political-donations](https://apify.com/seaf999ield/uk-political-donations) |
| [Google Trends Scraper UK: Interest, Regions & Related Queries](docs/uk-google-trends.md) | Google Trends for the UK and any country: interest over time, interest by region and nation (England, Scotland, Wales, NI), and rising/top related queries. | SEO and content teams, ecommerce sellers, marketers, journalists and analysts | $2 | [apify.com/seaf999ield/uk-google-trends](https://apify.com/seaf999ield/uk-google-trends) |
| [BNPL Checker UK: Klarna, Clearpay & PayPal Pay in 3 Detector](docs/uk-bnpl-merchant-detector.md) | Checks UK online shops for Klarna, Clearpay, PayPal Pay in 3, Laybuy and Zilch, and detects the platform (Shopify, WooCommerce). | BNPL and payments sales teams, Shopify/WooCommerce agencies, analysts, compliance | $3 | [apify.com/seaf999ield/uk-bnpl-merchant-detector](https://apify.com/seaf999ield/uk-bnpl-merchant-detector) |

Prices are in USD, pay-per-event, as listed on the Apify Store. Some actors also charge separately for change/alert events. See each docs page for details. Apify's free plan includes monthly credit for trying them.

**Coming soon:** amazon-uk-bestsellers · ebay-uk-listings-prices · uk-jobs-feed

## Stay updated: free weekly newsletter

📬 **[UK Industry & Bills](https://imrawtrader.beehiiv.com)** is a free weekly newsletter on UK industry, energy bills, regulation and the data behind them, with new scrapers announced first.
Follow on X: **[@ImRawTrader](https://x.com/ImRawTrader)**

## How to use

You need a free Apify account and your API token from [Console → Settings → Integrations](https://console.apify.com/settings/integrations). Don't commit your token. Keep it in an environment variable.

### Via API (curl)

```bash
# Run an actor synchronously and get the dataset items back as JSON
curl -X POST \
  "https://api.apify.com/v2/acts/seaf999ield~uk-companies-house-feed/run-sync-get-dataset-items" \
  -H "Authorization: Bearer $APIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mode":"new_companies","daysBack":1,"regions":["London"],"maxResults":100}'
```

### Python (apify-client)

```bash
pip install apify-client
```

```python
import os
from apify_client import ApifyClient

client = ApifyClient(os.environ["APIFY_TOKEN"])

run = client.actor("seaf999ield/uk-public-tenders-feed").call(run_input={
    "daysBack": 3,
    "keywords": ["software", "digital", "cloud"],
    "onlyOpen": True,
})

for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item["title"], item.get("buyerName"), item.get("valueGBP"))
```

### JavaScript / Node.js (apify-client)

```javascript
import { ApifyClient } from 'apify-client';

const client = new ApifyClient({ token: process.env.APIFY_TOKEN });
const run = await client.actor('seaf999ield/uk-fca-short-positions').call({ mode: 'current', minShortPct: 3 });
const { items } = await client.dataset(run.defaultDatasetId).listItems();
console.log(items);
```

### Make (Integromat)

1. Add the **Apify** app → **Run an Actor** module, and connect your Apify account.
2. Actor: `seaf999ield/uk-food-hygiene-ratings`; Run synchronously: **Yes**.
3. Input JSON: `{"mode":"new_businesses","localAuthorities":["Manchester"],"businessTypes":["restaurant","takeaway"],"monitorName":"manchester"}`
4. Add **Apify → Get Dataset Items** (use the run's `defaultDatasetId`), then send rows to Google Sheets, HubSpot or email.
5. Schedule the scenario daily or weekly.

### Zapier

1. Trigger: **Schedule by Zapier** (e.g. every weekday at 08:00).
2. Action: **Apify → Run Actor**, Actor `seaf999ield/uk-gazette-insolvency-notices`, with an input such as `{"mode":"new_notices"}`.
3. Action: **Apify → Fetch Dataset Items** (from the run), then **Google Sheets → Create Row** or **Slack → Send Message**.
4. Or schedule the actor in Apify and use the Zapier trigger **Apify → Finished Actor Run**.

## FAQ

**Is this data legal to use?**
These actors read official public sources such as Companies House, Find a Tender, Contracts Finder, the FCA, The Gazette, GOV.UK, the FSA, OPSS, MHRA and the Electoral Commission. Most of them are published under the Open Government Licence v3.0. You're responsible for how you use any personal data (UK GDPR, PECR), especially for outreach.

**How much does it cost?**
You pay per result, usually $2–$3 per 1,000 rows, plus a small per-event fee for change alerts on some actors. There's no subscription. Apify's free plan includes monthly credit.

**Can I get only new records each day?**
Yes. Most actors have a monitor/changes mode that saves state between runs and outputs only new or changed records. Schedule it daily in Apify.

**What formats can I export?**
JSON, CSV, Excel, XML, RSS or HTML tables from the Apify dataset. You can also call the API directly or use integrations (Google Sheets, webhooks, Make, Zapier, n8n).

**Do I need my own API keys (e.g. Companies House)?**
No. For very large runs, some actors accept your own free official API key as an optional input for a dedicated quota.

**Is the source code here?**
No. This repository is a documentation hub. The actors run on the Apify platform. Each page in [`docs/`](docs/) describes one actor with a real output sample.

**Can you build a scraper for another UK dataset?**
Open an issue in this repo with the source and the fields you need, or get in touch on [X](https://x.com/ImRawTrader).

## Docs pages

- [UK Companies House Scraper: New Companies Feed & Alerts](docs/uk-companies-house-feed.md)
- [UK Tenders Scraper & API: Find a Tender, Contracts Finder, TED](docs/uk-public-tenders-feed.md)
- [FCA Short Positions Scraper: UK Short Interest Tracker](docs/uk-fca-short-positions.md)
- [UK Insolvency Notices Scraper: Gazette Winding-Up Feed](docs/uk-gazette-insolvency-notices.md)
- [UK Visa Sponsor Register Scraper & Monitor (Home Office)](docs/uk-visa-sponsor-register-monitor.md)
- [UK Food Hygiene Ratings Scraper & New Restaurant Leads](docs/uk-food-hygiene-ratings.md)
- [UK Product Recalls Scraper: OPSS, FSA & MHRA Safety Alerts](docs/uk-product-safety-recalls.md)
- [UK Political Donations Scraper: Electoral Commission API](docs/uk-political-donations.md)
- [Google Trends Scraper UK: Interest, Regions & Related Queries](docs/uk-google-trends.md)
- [BNPL Checker UK: Klarna, Clearpay & PayPal Pay in 3 Detector](docs/uk-bnpl-merchant-detector.md)

---

*Keywords: UK open data, UK government data API, Companies House scraper, UK tenders API, FCA short positions, Gazette insolvency data, UK visa sponsor list, food hygiene ratings API, UK product recalls, political donations data, Google Trends UK, BNPL checker, lead generation UK.*
