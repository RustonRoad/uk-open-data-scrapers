# UK Food Hygiene Ratings Scraper & New Restaurant Leads

> FSA food hygiene ratings API: search UK restaurants and takeaways by council, postcode or rating; get new-business leads and rating alerts.

**Run it on Apify:** [https://apify.com/seaf999ield/uk-food-hygiene-ratings](https://apify.com/seaf999ield/uk-food-hygiene-ratings) · **Price:** $2 per 1,000 establishments; $5 per 1,000 new-business leads; $10 per 1,000 rating changes (USD, pay per result, no subscription)

## Use case

Search FSA food hygiene ratings by council, postcode, business type or rating, get leads for newly opened restaurants and takeaways, and monitor rating changes.

- **Suppliers to restaurants and takeaways:** food and drink wholesalers, EPOS and card terminals, delivery platforms, packaging, waste, pest control, insurance, signage and recruitment. Reach new openings first.
- **Food safety consultants and trainers:** premises rated 0-2, and new businesses awaiting their first inspection.
- **Landlords, investors, franchise and brand owners:** monitor the hygiene ratings of your sites, tenants or franchisees.
- **Delivery apps, review sites and journalists:** bulk ratings data by area.

## Example input

```json
{
  "mode": "new_businesses",
  "localAuthorities": [
    "Manchester"
  ],
  "businessTypes": [
    "restaurant",
    "takeaway"
  ],
  "monitorName": "manchester"
}
```

## Example output (real sample)

| recordType | businessName | businessType | postcode | localAuthority | ratingValue |
|---|---|---|---|---|---|
| newBusiness | 10 Dining Street | Restaurant/Cafe/Canteen | LE15 6BA | Rutland | 5 |
| newBusiness | A Simpler Life | Retailers - other | LE15 9QB | Rutland | 5 |
| newBusiness | All You Can Treat | Retailers - other | LE15 | Rutland | AwaitingInspection |

Full field list, input options and FAQ: see the actor page on the [Apify Store](https://apify.com/seaf999ield/uk-food-hygiene-ratings).

## Run it from Python

```python
from apify_client import ApifyClient

client = ApifyClient("YOUR_APIFY_TOKEN")  # from https://console.apify.com/settings/integrations
run = client.actor("seaf999ield/uk-food-hygiene-ratings").call(run_input={'mode': 'new_businesses', 'localAuthorities': ['Manchester'], 'businessTypes': ['restaurant', 'takeaway'], 'monitorName': 'manchester'})
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)
```

---

Related keywords: FSA food hygiene ratings API, new restaurant leads UK, FHRS data.

[← All UK open data scrapers](../README.md) · Free weekly newsletter: [UK Industry & Bills](https://imrawtrader.beehiiv.com) · [@ImRawTrader on X](https://x.com/ImRawTrader)
