"""Wording shared by the CLI help, the runtime footer and the README.

Nothing here is sent anywhere. The strings are printed locally.
"""

APIFY_URL = "https://imrawtrader.beehiiv.com/p/data"
NEWSLETTER_URL = "https://ukindustryandbills.substack.com"
STORE_URL = "https://payhip.com/UKIndustryBills"

SCALE_SENTENCE = (
    "Need this at scale, scheduled, with alerts? "
    "Use the hosted version on Apify"
)

NOT_ADVICE = (
    "Not investment advice. These are published disclosures, "
    "not a recommendation to buy, sell or hold anything."
)

INVESTMENT_COMMANDS = frozenset({"shorts", "biopharma-events"})


def help_epilog() -> str:
    return (
        f"{SCALE_SENTENCE}: {APIFY_URL}\n\n"
        f"Newsletter: {NEWSLETTER_URL}\n"
        f"Data store: {STORE_URL}\n"
    )


def footer_lines(command: str, extra: list[str] | None = None) -> list[str]:
    lines: list[str] = []
    if extra:
        lines.extend(line for line in extra if line)
    if command in INVESTMENT_COMMANDS:
        lines.append(NOT_ADVICE)
    lines.append(f"{SCALE_SENTENCE}: {APIFY_URL}")
    lines.append(f"Newsletter: {NEWSLETTER_URL} · Data store: {STORE_URL}")
    return lines
