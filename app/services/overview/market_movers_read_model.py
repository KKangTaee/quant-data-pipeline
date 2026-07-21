from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


CANONICAL_SECTORS: tuple[str, ...] = (
    "Communication Services",
    "Consumer Discretionary",
    "Consumer Staples",
    "Energy",
    "Financials",
    "Health Care",
    "Industrials",
    "Materials",
    "Real Estate",
    "Technology",
    "Utilities",
)

SECTOR_ALIASES: dict[str, str] = {
    "basic materials": "Materials",
    "communication services": "Communication Services",
    "consumer cyclical": "Consumer Discretionary",
    "consumer defensive": "Consumer Staples",
    "consumer discretionary": "Consumer Discretionary",
    "consumer staples": "Consumer Staples",
    "energy": "Energy",
    "financial services": "Financials",
    "financials": "Financials",
    "health care": "Health Care",
    "healthcare": "Health Care",
    "industrials": "Industrials",
    "information technology": "Technology",
    "materials": "Materials",
    "real estate": "Real Estate",
    "technology": "Technology",
    "utilities": "Utilities",
}


def canonical_sector(value: object) -> str:
    """Return one stable 11-sector display key for a provider label."""

    normalized = " ".join(str(value or "").split()).casefold()
    if not normalized:
        return "Unknown"
    return SECTOR_ALIASES.get(normalized, "Unknown")


def canonicalize_market_mover_row(row: Mapping[str, Any]) -> dict[str, Any]:
    """Copy a market-mover row while preserving its raw sector evidence."""

    result = dict(row)
    raw_sector = result.get("sector")
    result["sector_raw"] = raw_sector
    result["sector"] = canonical_sector(raw_sector)
    return result


def canonical_sector_options(rows: Sequence[Mapping[str, Any]]) -> list[str]:
    sectors = {canonical_sector(row.get("sector")) for row in rows}
    return ["All", *sorted(sectors)]


def filter_rows_by_canonical_sector(
    rows: Sequence[Mapping[str, Any]],
    sector: str | None,
) -> list[dict[str, Any]]:
    canonical_rows = [canonicalize_market_mover_row(row) for row in rows]
    requested = str(sector or "All").strip()
    if not requested or requested.casefold() == "all":
        return canonical_rows
    requested_sector = canonical_sector(requested)
    return [row for row in canonical_rows if row["sector"] == requested_sector]
