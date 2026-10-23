"""Render rows as a text table, CSV or JSON. Data only: no footer in the payload."""

from __future__ import annotations

import csv
import io
import json
from typing import Iterable


def render(
    rows: list[dict],
    columns: list[str],
    fmt: str,
    *,
    truncate: dict[str, int] | None = None,
    json_document: dict | None = None,
) -> str:
    if fmt == "json":
        payload: object = json_document if json_document is not None else rows
        return json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if fmt == "csv":
        return _csv(rows, columns)
    if fmt == "table":
        return _table(rows, columns, truncate or {})
    raise ValueError(f"unknown format {fmt}")


def _csv(rows: Iterable[dict], columns: list[str]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\n", extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow({column: _plain(row.get(column)) for column in columns})
    return buffer.getvalue()


def _table(rows: list[dict], columns: list[str], truncate: dict[str, int]) -> str:
    display = [{column: _clip(_plain(row.get(column)), truncate.get(column)) for column in columns} for row in rows]
    widths = {column: len(column) for column in columns}
    for row in display:
        for column in columns:
            widths[column] = max(widths[column], len(row[column]))

    def line(row: dict[str, str]) -> str:
        return "  ".join(row[column].ljust(widths[column]) for column in columns)

    header = {column: column for column in columns}
    rules = {column: "-" * widths[column] for column in columns}
    lines = [line(header), line(rules)]
    lines.extend(line(row) for row in display)
    return "\n".join(lines) + "\n"


def _plain(value: object) -> str:
    if value is None:
        return ""
    return str(value)


def _clip(value: str, limit: int | None) -> str:
    if limit is None or len(value) <= limit:
        return value
    if limit <= 1:
        return value[:limit]
    return value[: limit - 1] + "…"
