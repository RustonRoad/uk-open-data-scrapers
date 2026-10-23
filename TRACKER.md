# Actor tracker

Actor rows for the seaf999ield Apify account. [docs/actors.json](docs/actors.json) is the source of truth. The table below mirrors those rows. Pricing, build, users, and runs are from the tracker draft (Apify API, 23 Oct 2026, 12:20 UK).

## How to update after publish day

1. Edit `docs/actors.json` first. That file holds the actor rows.
2. Refresh the table in this file so every cell matches the JSON. Do not type a different figure in the markdown.
3. Serve the `docs` folder and open `index.html`. The page fetches `actors.json` next to itself.

Keep these JSON fields and the table columns on the same values: `status`, `statusSource`, `plannedPublish`, `date`, `pricing`, `build`, `users`, `runs`, `store`, `created`, `modified`, `title`, `what`. `id` (the Apify actor id from the draft) stays in the JSON only. `date` is `2026-10-24`, `2026-10-25`, `2026-10-26`, or empty. `plannedPublish` is the draft's date label for that same fact.

Status labels in the table:

- `live` — public actors. Planned publish `Already public`.
- `Scheduled 24 Oct 10:00 UK` — the 24 Oct 10:00 UK batch, in this order: `uk-ofgem-price-cap`, `amazon-uk-bestsellers`, `ebay-uk-listings-prices`, `uk-jobs-feed`, `uk-planning-applications`. `date` is `2026-10-24`. Planned publish is `24 Oct 10:00 UK`.
- `scheduled 25 Oct 2026` — `uk-nhs-prescribing-data`.
- `scheduled 26 Oct 2026` — `biotech-catalyst-tracker`.
- `private test` — `gtrends-proxy-test` only. Internal prototype. Planned publish `Not scheduled`. It is not in the 24 Oct batch.

A blank cell means the draft had no value.

## Gaps and conflicts

- **Pricing not set.** `gtrends-proxy-test` is `No pricing set` in the draft.
- **Store URL blank** for every actor whose draft `store` is empty (the eight that are not public). The draft screen shows "Not public yet" when that URL is empty. The cell here is blank.
- **Prices vs per-actor docs.** For the 10 public actors, `docs/<name>.md` states per-1,000 prices equal to these per-event prices times 1,000, including the separate alert events. No price figure disagreed. `docs/uk-google-trends.md` also says error and no-data rows are free. The draft price line does not mention that. The result-row price is the same on both sides (`$0.002`, `$2` per 1,000).
- **Wording vs per-actor docs.** The table keeps the draft sentence. The doc sentence is quoted here and is not merged into the row.
  - `uk-public-tenders-feed` — draft: "Pulls new UK public-sector tenders and contract awards from Find a Tender, Contracts Finder and EU TED into one dataset." `docs/uk-public-tenders-feed.md`: "New UK public-sector tenders and contract awards from Find a Tender and Contracts Finder, with optional EU TED."
  - `uk-google-trends` — draft: "Fetches Google Trends interest over time, by UK region and related queries for up to 5 keywords." `docs/uk-google-trends.md`: "Google Trends for the UK and any country: interest over time, interest by region and nation (England, Scotland, Wales, NI), and rising/top related queries." The doc line does not state a 5-keyword cap.
  - `uk-companies-house-feed` — draft: "Daily feed of newly incorporated UK companies plus liquidation and dissolution alerts from Companies House." `docs/uk-companies-house-feed.md`: "Daily feed of new UK company incorporations from the official Companies House API, filtered by SIC code, region and postcode, plus liquidation, administration and dissolution alerts for a watchlist."
- **No doc page** for `ebay-uk-listings-prices`, `gtrends-proxy-test`, `amazon-uk-bestsellers`, `uk-ofgem-price-cap`, `uk-jobs-feed`, `uk-planning-applications`, `uk-nhs-prescribing-data`, or `biotech-catalyst-tracker`. README "Coming soon" names `amazon-uk-bestsellers`, `ebay-uk-listings-prices`, and `uk-jobs-feed`, with no prices, builds, users, runs, or dates.

The other public doc pages add filters or examples. Those details are not entered as separate figures.

## Reading the counts

The draft says users and runs are lifetime totals from Apify and include the account's own test runs. Build is the version tagged `latest`. Every priced actor uses pay per event.

## Actors

| Actor | Title | What it does | Status | Status in source | Planned publish | Per-event pricing (USD) | Build | Users | Runs | Created (UK) | Modified (UK) | Store |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uk-public-tenders-feed | UK Tenders Scraper & API: Find a Tender, Contracts Finder, TED | Pulls new UK public-sector tenders and contract awards from Find a Tender, Contracts Finder and EU TED into one dataset. | live | Public | Already public | Tender notice $0.003 | 0.2.1 | 2 | 15 | 20 Oct 2026 12:29 | 23 Oct 2026 11:36 | https://apify.com/seaf999ield/uk-public-tenders-feed |
| uk-visa-sponsor-register-monitor | UK Visa Sponsor Register Scraper & Monitor (Home Office) | Watches the Home Office licensed sponsor register and reports employers added, removed or downgraded since the last run. | live | Public | Already public | Sponsor change $0.01; Snapshot row $0.001; Companies House enriched row $0.004 | 0.2.4 | 2 | 9 | 20 Oct 2026 12:29 | 23 Oct 2026 10:05 | https://apify.com/seaf999ield/uk-visa-sponsor-register-monitor |
| ebay-uk-listings-prices | eBay UK Listings & Price Comps (GBP) | Lists live ebay.co.uk listings for a keyword with £ prices and a median/range price-comp summary. | Scheduled 24 Oct 10:00 UK | Scheduled 24 Oct 10:00 UK | 24 Oct 10:00 UK | Listing row $0.002; Price summary $0.01 | 0.2.1 | 1 | 7 | 20 Oct 2026 13:48 | 23 Oct 2026 09:45 |  |
| gtrends-proxy-test | Google Trends proxy-cost probe (internal prototype) | Internal test measuring Google Trends success rate and proxy cost; not meant for the Store. | private test | Private, unscheduled | Not scheduled | No pricing set | 0.1.2 | 1 | 8 | 20 Oct 2026 13:53 | 20 Oct 2026 14:04 |  |
| uk-google-trends | Google Trends Scraper UK: Interest, Regions & Related Queries | Fetches Google Trends interest over time, by UK region and related queries for up to 5 keywords. | live | Public | Already public | Trends result row $0.002 | 0.1.6 | 2 | 8 | 20 Oct 2026 14:22 | 23 Oct 2026 10:05 | https://apify.com/seaf999ield/uk-google-trends |
| uk-companies-house-feed | UK Companies House Scraper: New Companies Feed & Alerts | Daily feed of newly incorporated UK companies plus liquidation and dissolution alerts from Companies House. | live | Public | Already public | Company record $0.003; Status change alert $0.01 | 0.1.5 | 2 | 10 | 20 Oct 2026 14:50 | 23 Oct 2026 10:05 | https://apify.com/seaf999ield/uk-companies-house-feed |
| uk-fca-short-positions | FCA Short Positions Scraper: UK Short Interest Tracker | Tracks UK short interest from the FCA net short positions report, with daily change alerts. | live | Public | Already public | Position row $0.002; Position change $0.01 | 0.1.4 | 2 | 11 | 20 Oct 2026 15:08 | 23 Oct 2026 10:05 | https://apify.com/seaf999ield/uk-fca-short-positions |
| uk-political-donations | UK Political Donations Scraper: Electoral Commission API | Searches Electoral Commission donations and loans to UK parties and politicians, and flags new ones. | live | Public | Already public | Donation or loan record $0.002 | 0.1.5 | 2 | 7 | 20 Oct 2026 15:14 | 23 Oct 2026 10:05 | https://apify.com/seaf999ield/uk-political-donations |
| uk-bnpl-merchant-detector | BNPL Checker UK: Klarna, Clearpay & PayPal Pay in 3 Detector | Checks UK online shops for Klarna, Clearpay, PayPal Pay in 3 and other buy-now-pay-later options and their platform. | live | Public | Already public | Merchant checked $0.003 | 0.1.4 | 2 | 2 | 20 Oct 2026 15:26 | 23 Oct 2026 10:05 | https://apify.com/seaf999ield/uk-bnpl-merchant-detector |
| uk-food-hygiene-ratings | UK Food Hygiene Ratings Scraper & New Restaurant Leads | Searches FSA food hygiene ratings and flags newly listed food businesses and rating changes. | live | Public | Already public | Establishment row $0.002; New business lead $0.005; Rating change $0.01 | 0.1.4 | 2 | 6 | 20 Oct 2026 15:34 | 23 Oct 2026 10:05 | https://apify.com/seaf999ield/uk-food-hygiene-ratings |
| uk-gazette-insolvency-notices | UK Insolvency Notices Scraper: Gazette Winding-Up Feed | Daily feed of UK winding-up petitions, administrations and liquidations from The Gazette. | live | Public | Already public | Notice row $0.003; New notice $0.01 | 0.1.8 | 2 | 11 | 20 Oct 2026 15:52 | 23 Oct 2026 10:05 | https://apify.com/seaf999ield/uk-gazette-insolvency-notices |
| uk-product-safety-recalls | UK Product Recalls Scraper: OPSS, FSA & MHRA Safety Alerts | Combines OPSS product recalls, FSA food alerts and MHRA medicine and device alerts in one feed. | live | Public | Already public | Alert row $0.002; New alert $0.008 | 0.1.4 | 2 | 5 | 20 Oct 2026 15:54 | 23 Oct 2026 10:05 | https://apify.com/seaf999ield/uk-product-safety-recalls |
| amazon-uk-bestsellers | Amazon UK Best Sellers, Movers & Shakers & New Releases Tracker | Scrapes Amazon UK Best Sellers, Movers & Shakers and New Releases lists and flags rank changes. | Scheduled 24 Oct 10:00 UK | Scheduled 24 Oct 10:00 UK | 24 Oct 10:00 UK | Best seller row $0.002; Rank change $0.005 | 0.1.3 | 1 | 4 | 23 Oct 2026 09:34 | 23 Oct 2026 09:38 |  |
| uk-ofgem-price-cap | UK Ofgem Energy Price Cap: Rates by Region + Forecast | Returns official Ofgem energy price cap rates and standing charges for every GB region, with optional forecasts. | Scheduled 24 Oct 10:00 UK | Scheduled 24 Oct 10:00 UK | 24 Oct 10:00 UK | Price check $0.03; Actor Start $0.00005 | 0.1.1 | 1 | 1 | 23 Oct 2026 09:43 | 23 Oct 2026 09:45 |  |
| uk-jobs-feed | UK Jobs Feed: NHS Jobs, DWP Find a Job & Company Careers Pages | One de-duplicated UK jobs feed from NHS Jobs, DWP Find a Job and Greenhouse, Lever and Workable boards. | Scheduled 24 Oct 10:00 UK | Scheduled 24 Oct 10:00 UK | 24 Oct 10:00 UK | Job row $0.002; New job $0.005 | 0.1.6 | 1 | 6 | 23 Oct 2026 09:50 | 23 Oct 2026 09:56 |  |
| uk-planning-applications | UK Planning Applications Scraper: Council Planning Data & Leads | Collects new UK planning applications from council portals, filterable by council, date and keyword. | Scheduled 24 Oct 10:00 UK | Scheduled 24 Oct 10:00 UK | 24 Oct 10:00 UK | Planning application row $0.003; New planning application $0.008 | 0.1.3 | 1 | 6 | 23 Oct 2026 10:08 | 23 Oct 2026 10:22 |  |
| uk-nhs-prescribing-data | UK NHS Prescribing Data: GP Drug Trends for All 4 Nations | Monthly GP prescribing figures for any drug across all four UK nations, with biggest movers. | scheduled 25 Oct 2026 | Private, scheduled 25 Oct | 25 Oct 2026 | Actor Start $0.02; Trend row $0.002; Mover alert $0.01 | 0.1.3 | 1 | 1 | 23 Oct 2026 11:06 | 23 Oct 2026 11:11 |  |
| biotech-catalyst-tracker | Biotech Catalyst Tracker: FDA & MHRA Approvals, Trials, AdComs | Feed of FDA and MHRA approvals, FDA rejections, advisory meetings and clinical-trial changes from official sources. | scheduled 26 Oct 2026 | Private, scheduled 26 Oct | 26 Oct 2026 | Catalyst row $0.003 | 0.1.3 | 1 | 3 | 23 Oct 2026 11:28 | 23 Oct 2026 11:33 |  |
