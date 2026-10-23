# UK Visa Sponsor Register Scraper & Monitor (Home Office)

> UK visa sponsor licence list API: Home Office Register of Licensed Sponsors. Get new, removed and A-to-B downgraded sponsors. Skilled Worker leads.

**Run it on Apify:** [https://apify.com/seaf999ield/uk-visa-sponsor-register-monitor](https://apify.com/seaf999ield/uk-visa-sponsor-register-monitor) · **Price:** $10 per 1,000 detected changes; $1 per 1,000 snapshot rows; $4 per 1,000 Companies House-enriched rows (optional) (USD, pay per result, no subscription)

## Use case

Tracks the Home Office Register of Licensed Sponsors: new sponsors, removals and A-to-B rating downgrades by town and visa route, with optional Companies House enrichment.

- **Recruitment and talent agencies:** find newly licensed employers who can sponsor visas. They are hot leads for international hiring.
- **Job boards and sponsor-job sites:** keep "visa sponsor" badges accurate and remove revoked sponsors automatically.
- **HR, compliance and due-diligence teams:** watch your clients, suppliers or portfolio companies for downgrades and removals.
- **Researchers and journalists:** track licence revocations by sector, town or route over time.

## Example input

```json
{
  "monitorName": "london-skilled-worker",
  "towns": [
    "London"
  ],
  "routes": [
    "Skilled Worker"
  ],
  "changeTypes": [
    "SPONSOR_ADDED",
    "RATING_CHANGED"
  ],
  "organisationsOnly": true,
  "outputSnapshotOnFirstRun": false
}
```

## Example output (real sample)

| changeType | organisationName | town | route | newRating | severity |
|---|---|---|---|---|---|
| RATING_CHANGED | Alium Consultancy Ltd | London | Skilled Worker | Worker (B rating) | high |
| RATING_CHANGED | HOUSE OF CARDS LTD | London | Skilled Worker | Worker (A rating) | info |
| RATING_CHANGED | ETERNIQUE LIMITED | LONDON | Skilled Worker | Worker (A rating) | info |

Full field list, input options and FAQ: see the actor page on the [Apify Store](https://apify.com/seaf999ield/uk-visa-sponsor-register-monitor).

## Run it from Python

```python
from apify_client import ApifyClient

client = ApifyClient("YOUR_APIFY_TOKEN")  # from https://console.apify.com/settings/integrations
run = client.actor("seaf999ield/uk-visa-sponsor-register-monitor").call(run_input={'monitorName': 'london-skilled-worker', 'towns': ['London'], 'routes': ['Skilled Worker'], 'changeTypes': ['SPONSOR_ADDED', 'RATING_CHANGED'], 'organisationsOnly': True, 'outputSnapshotOnFirstRun': False})
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)
```

---

Related keywords: UK visa sponsor list, licensed sponsors register, Skilled Worker sponsors.

[← All UK open data scrapers](../README.md) · Free weekly newsletter: [UK Industry & Bills](https://imrawtrader.beehiiv.com) · [@ImRawTrader on X](https://x.com/ImRawTrader)
