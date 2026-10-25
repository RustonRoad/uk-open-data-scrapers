# BNPL Checker UK: Klarna, Clearpay & PayPal Pay in 3 Detector

> Check UK online shops for Klarna, Clearpay, PayPal Pay in 3, Laybuy and Zilch, plus Shopify/WooCommerce platform. Fintech sales leads.

**Hosted versions:** see the [RawTrader UK data tools page](https://imrawtrader.beehiiv.com/p/data) · **Price:** $3 per 1,000 shops checked (USD, pay per result, no subscription)

## Use case

Checks UK online shops for Klarna, Clearpay, PayPal Pay in 3, Laybuy and Zilch, and detects the platform (Shopify, WooCommerce).

- **BNPL and payments sales teams:** find merchants without Klarna or Clearpay, or merchants that use a competitor, and build target lists.
- **Agencies and Shopify / WooCommerce developers:** qualify leads by platform and checkout stack.
- **Analysts and investors:** measure BNPL adoption across UK retail categories.
- **Compliance teams:** track which retailers promote BNPL now that UK BNPL regulation applies.

## Example input

```json
{
  "urls": [
    "https://www.oliverbonas.com",
    "boohoo.com",
    "gymshark.com"
  ],
  "checkProductPage": true,
  "onlyWithBnpl": false
}
```

## Example output (real sample)

| domain | platform | hasBnpl | bnplProviders | status |
|---|---|---|---|---|
| boohoo.com | – | true | Clearpay, Klarna | ok |
| gymshark.com | Shopify | true | Klarna | ok |
| allbirds.co.uk | Shopify | false | – | ok |

Full field list, input options and FAQ: see the [RawTrader UK data tools page](https://imrawtrader.beehiiv.com/p/data).

## Run it from Python

```python
from apify_client import ApifyClient

client = ApifyClient("YOUR_APIFY_TOKEN")  # from https://console.apify.com/settings/integrations
# Actor id: see the RawTrader UK data tools page https://imrawtrader.beehiiv.com/p/data
run = client.actor("uk-bnpl-merchant-detector").call(run_input={'urls': ['https://www.oliverbonas.com', 'boohoo.com', 'gymshark.com'], 'checkProductPage': True, 'onlyWithBnpl': False})
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(item)
```

---

Related keywords: BNPL checker, Klarna merchant list UK, Clearpay retailers, fintech leads.

[← All UK open data scrapers](../README.md) · Free weekly newsletter: [UK Industry & Bills](https://imrawtrader.beehiiv.com) · [@ImRawTrader on X](https://x.com/ImRawTrader)
