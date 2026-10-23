# Licensing

The `ukopendata` software (everything under `src/`, `tests/` and the
packaging files) is MIT licensed. See [LICENSE](LICENSE).

The actor documentation that was already in `docs/` is available under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), which is how this
repository described it before the CLI was added.

Data you download with the CLI is not covered by either of those licences.
Each publisher keeps its own terms. The README table lists them. In short:

- Contracts Finder, Find a Tender, the Electoral Commission donations
  register, Price Paid Data, the weekly road fuel prices and most Companies
  House company data are Open Government Licence v3.0, with the attributions
  the commands print.
- Price Paid address fields also include Royal Mail PAF and Ordnance Survey
  data. Personal and non-commercial use, and display for residential property
  price information, is permitted. Other use of the address data needs
  permission from Royal Mail.
- FCA short-position figures are the FCA's published aggregated disclosures.
  Attribute them to the FCA.
- Ofgem price cap figures should be attributed to Ofgem.
- SEC EDGAR filings are US government works.
- Companies House API use also follows the Companies House API terms, and
  needs the free key you create yourself.

Do not commit API keys. `COMPANIES_HOUSE_API_KEY` stays in the environment.
