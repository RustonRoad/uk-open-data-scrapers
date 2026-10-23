# UK Product Recalls Scraper: OPSS, FSA & MHRA Safety Alerts

> UK product recall API: OPSS product recalls, FSA food and allergy alerts, MHRA drug and device alerts in one feed. Filter, or monitor new alerts.

**Run it on Apify:** [https://apify.com/seaf999ield/uk-product-safety-recalls](https://apify.com/seaf999ield/uk-product-safety-recalls) · **Price:** $2 per 1,000 alerts; $8 per 1,000 new-alert detections (USD, pay per result, no subscription)

## Use case

One UK recall and safety-alert feed: OPSS product recalls (toys, baby, electrical), FSA food and allergy alerts, and MHRA medicine and device alerts.

- **Online sellers and marketplaces (Amazon, eBay, Etsy, TikTok Shop):** check your listings against new recalls and OPSS marketplace reports.
- **Retailers, importers and brand owners:** monitor your category and your competitors.
- **Compliance, QA and insurance teams:** a product-liability and recall-risk feed.
- **Parents' sites, consumer journalists and allergy groups:** toy, baby and allergen alerts.
- **Pharmacies and clinics:** MHRA medicine recalls and device safety notices.

## Example output (real sample)

| source | date | category | product | hazard | riskLevel |
|---|---|---|---|---|---|
| opss | 2026-10-16 | toys | Soft Plastic Alien Mask | asphyxiation | serious |
| opss | 2026-10-13 | toys | Toddler Ghost Costume | strangulation and asphyxiation | serious |
| opss | 2026-10-13 | baby | Baby Electric Soothing Palm Sleep Pillow | asphyxiation | serious |

Full field list, input options and FAQ: see the actor page on the [Apify Store](https://apify.com/seaf999ield/uk-product-safety-recalls).

## Run it from Python

```python
from apify_client import ApifyClient

client = ApifyClient("YOUR_APIFY_TOKEN")  # from https://console.apify.com/settings/integrations
run = client.actor("seaf999ield/uk-product-safety-recalls").call(run_input={})
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)
```

---

Related keywords: UK product recalls API, OPSS recalls, FSA allergy alerts, MHRA drug alerts.

[← All UK open data scrapers](../README.md) · Free weekly newsletter: [UK Industry & Bills](https://imrawtrader.beehiiv.com) · [@ImRawTrader on X](https://x.com/ImRawTrader)
