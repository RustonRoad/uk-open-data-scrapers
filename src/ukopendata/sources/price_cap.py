"""Ofgem energy price cap headline figures.

The consumer page publishes the Direct Debit average for England, Scotland
and Wales, including the previous quarter for comparison. Regional tables on
that page are loaded in the browser, so this command reads the headline
table in the HTML, which is the figure Ofgem leads with.

https://www.ofgem.gov.uk/your-energy-supply/your-energy-bill/energy-price-cap-unit-rates-and-standing-charges

Ofgem / Crown copyright. Reuse with attribution to Ofgem.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser

from ukopendata.errors import SourceError

PAGE_URL = (
    "https://www.ofgem.gov.uk/your-energy-supply/your-energy-bill/"
    "energy-price-cap-unit-rates-and-standing-charges"
)

COLUMNS = [
    "period",
    "typical_annual_gbp",
    "change_percent",
    "electricity_unit_p_per_kwh",
    "electricity_standing_p_per_day",
    "gas_unit_p_per_kwh",
    "gas_standing_p_per_day",
]


def fetch(client) -> tuple[list[dict], str]:
    body = client.get(PAGE_URL, headers={"Accept": "text/html"}, timeout=45)
    html = body.decode("utf-8", "replace")
    return parse_price_cap(html)


def parse_price_cap(html: str) -> tuple[list[dict], str]:
    text = _visible_text(html)
    annual = re.search(r"£\s*([\d,]+)\s+per year", text)
    change = re.search(r"gone\s+(up|down)\s+by\s+([\d.]+)\s*%", text, re.IGNORECASE)
    table = _rate_table(html)
    if annual is None or table is None:
        raise SourceError(
            "The Ofgem price cap page did not contain the headline table. "
            f"Read it at {PAGE_URL}"
        )
    periods, electricity, gas = table
    if len(periods) < 2 or len(electricity) < 2 or len(gas) < 2:
        raise SourceError("The Ofgem price cap table did not have two periods of electricity and gas rates.")
    typical = int(annual.group(1).replace(",", ""))
    change_percent: float | None = None
    if change:
        change_percent = float(change.group(2))
        if change_percent.is_integer():
            change_percent = int(change_percent)
        if change.group(1).casefold() == "down":
            change_percent = -change_percent
    # The page's last column is the current cap. The first rate column is the previous quarter.
    note = _vat_note(text)
    rows = [
        _row(periods[-1], typical, change_percent, electricity[-1], gas[-1]),
        _row(periods[-2], None, None, electricity[-2], gas[-2]),
    ]
    return rows, note


def _row(period, typical, change_percent, electricity, gas) -> dict:
    return {
        "period": period,
        "typical_annual_gbp": typical if typical is not None else "",
        "change_percent": change_percent if change_percent is not None else "",
        "electricity_unit_p_per_kwh": electricity[0],
        "electricity_standing_p_per_day": electricity[1],
        "gas_unit_p_per_kwh": gas[0],
        "gas_standing_p_per_day": gas[1],
    }


def _vat_note(text: str) -> str:
    match = re.search(r"Figures are rounded to two decimal places[^.]*\.", text)
    if not match:
        return "Direct Debit averages for England, Scotland and Wales, as published by Ofgem."
    return " ".join(match.group(0).split())


def _rate_table(html: str) -> tuple[list[str], list[tuple[float, float]], list[tuple[float, float]]] | None:
    for rows in _tables(html):
        flat = " ".join(cell for row in rows for cell in row)
        if "pence per kwh" not in flat.casefold():
            continue
        periods: list[str] = []
        electricity: list[tuple[float, float]] | None = None
        gas: list[tuple[float, float]] | None = None
        for row in rows:
            label = row[0].casefold() if row else ""
            cells = row[1:]
            if "electricity" in label:
                electricity = [_unit_and_standing(cell) for cell in cells]
            elif label.startswith("gas") or label.strip() == "gas":
                gas = [_unit_and_standing(cell) for cell in cells]
            elif any("to" in cell.casefold() and re.search(r"20\d\d", cell) for cell in cells):
                periods = [_period_label(cell) for cell in cells]
        if periods and electricity and gas:
            return periods, electricity, gas
    return None


def _period_label(cell: str) -> str:
    match = re.search(
        r"(\d{1,2}\s+\w+\s+to\s+\d{1,2}\s+\w+\s+20\d\d)",
        cell,
        re.IGNORECASE,
    )
    if match:
        return " ".join(match.group(1).split())
    return " ".join(cell.split())


def _unit_and_standing(cell: str) -> tuple[float, float]:
    numbers = [float(value) for value in re.findall(r"(\d+\.\d+)", cell)]
    if len(numbers) < 2:
        raise SourceError(f"Could not read a unit rate and standing charge from {cell!r}")
    return numbers[0], numbers[1]


class _TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tables: list[list[list[str]]] = []
        self._table: list[list[str]] | None = None
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._table = []
        elif tag == "tr" and self._table is not None:
            self._row = []
        elif tag in {"td", "th"} and self._row is not None:
            self._cell = []

    def handle_endtag(self, tag):
        if tag in {"td", "th"} and self._cell is not None and self._row is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._row is not None and self._table is not None:
            if any(cell.strip() for cell in self._row):
                self._table.append(self._row)
            self._row = None
        elif tag == "table" and self._table is not None:
            self.tables.append(self._table)
            self._table = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def _tables(html: str) -> list[list[list[str]]]:
    parser = _TableParser()
    parser.feed(html)
    parser.close()
    return parser.tables


def _visible_text(html: str) -> str:
    class Text(HTMLParser):
        def __init__(self) -> None:
            super().__init__(convert_charrefs=True)
            self.parts: list[str] = []
            self._skip = 0

        def handle_starttag(self, tag, attrs):
            if tag in {"script", "style"}:
                self._skip += 1

        def handle_endtag(self, tag):
            if tag in {"script", "style"} and self._skip:
                self._skip -= 1

        def handle_data(self, data):
            if not self._skip:
                self.parts.append(data)

    parser = Text()
    parser.feed(html)
    parser.close()
    return " ".join(" ".join(parser.parts).split())
