from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable

from finance.data.db.mysql import MySQLClient

from .decision_lifecycle import latest_final_decision_rows
from .schemas import SourceType


@dataclass(frozen=True)
class CatalogItem:
    source_type: str
    source_ref: str
    instrument_kind: str
    label: str
    metadata: dict[str, Any]
    readiness: str


_UNAVAILABLE_LISTING_STATUSES = {
    "inactive",
    "delisted",
    "not_found",
    "unknown",
    "error",
}


def _normalized_query(value: Any) -> str:
    return str(value or "").strip().upper()


def _bounded_limit(value: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = 20
    return max(1, min(parsed, 50))


def search_direct_securities(
    query: str,
    *,
    db_factory: Callable[[], MySQLClient],
    limit: int = 20,
) -> list[CatalogItem]:
    """Search stored U.S. stock/ETF catalogs without calling a provider."""

    clean_query = _normalized_query(query)
    bounded_limit = _bounded_limit(limit)
    search_pattern = f"%{clean_query}%"
    sql = """
        SELECT
          universe.symbol,
          universe.name,
          universe.kind,
          profile.long_name,
          profile.exchange,
          profile.sector,
          profile.industry,
          profile.fund_family,
          (
            SELECT lifecycle.listing_status
            FROM nyse_symbol_lifecycle lifecycle
            WHERE lifecycle.symbol = universe.symbol
              AND lifecycle.kind = universe.kind
            ORDER BY
              COALESCE(lifecycle.collected_at, lifecycle.updated_at, lifecycle.created_at) DESC,
              lifecycle.id DESC
            LIMIT 1
          ) AS listing_status
        FROM (
          SELECT symbol, name, 'stock' AS kind FROM nyse_stock
          UNION ALL
          SELECT symbol, name, 'etf' AS kind FROM nyse_etf
        ) universe
        LEFT JOIN nyse_asset_profile profile
          ON profile.symbol = universe.symbol
         AND profile.kind = universe.kind
        WHERE UPPER(universe.symbol) LIKE %s
           OR UPPER(COALESCE(profile.long_name, universe.name)) LIKE %s
        ORDER BY
          CASE
            WHEN UPPER(universe.symbol) = %s THEN 0
            WHEN UPPER(universe.symbol) LIKE %s THEN 1
            ELSE 2
          END ASC,
          universe.symbol ASC,
          universe.kind ASC
        LIMIT %s
    """
    db = db_factory()
    try:
        db.use_db("finance_meta")
        rows = db.query(
            sql,
            [search_pattern, search_pattern, clean_query, f"{clean_query}%", bounded_limit],
        )
    finally:
        db.close()

    results: list[CatalogItem] = []
    for row in rows:
        listing_status = str(row.get("listing_status") or "").strip().lower()
        if listing_status in _UNAVAILABLE_LISTING_STATUSES:
            continue
        symbol = str(row.get("symbol") or "").strip().upper()
        kind = str(row.get("kind") or "").strip().lower()
        if not symbol or kind not in {"stock", "etf"}:
            continue
        label = str(row.get("long_name") or row.get("name") or symbol).strip()
        results.append(
            CatalogItem(
                source_type=SourceType.DIRECT_SECURITY.value,
                source_ref=symbol,
                instrument_kind=kind,
                label=label,
                metadata={
                    "symbol": symbol,
                    "name": label,
                    "exchange": row.get("exchange"),
                    "sector": row.get("sector"),
                    "industry": row.get("industry"),
                    "fund_family": row.get("fund_family"),
                    "listing_status": listing_status or None,
                },
                readiness="READY" if listing_status == "active" else "CATALOG_ONLY",
            )
        )
    results.sort(
        key=lambda item: (
            0
            if clean_query and item.source_ref == clean_query
            else 1
            if clean_query and item.source_ref.startswith(clean_query)
            else 2
            if clean_query and item.label.upper().startswith(clean_query)
            else 3,
            item.source_ref,
            item.instrument_kind,
        )
    )
    return results[:bounded_limit]


def _default_decision_loader() -> list[dict[str, Any]]:
    from app.runtime.backtest.stores.portfolio_selection import (
        load_current_final_selection_decisions,
    )

    return load_current_final_selection_decisions(limit=250)


def list_monitoring_candidates(
    *,
    decision_loader: Callable[[], Iterable[dict[str, Any]]] | None = None,
) -> list[CatalogItem]:
    """Project only authoritative Final Review monitoring candidates."""

    load = decision_loader or _default_decision_loader
    results: list[CatalogItem] = []
    for source in latest_final_decision_rows(load()):
        row = dict(source or {})
        decision_id = str(row.get("decision_id") or "").strip()
        if row.get("monitoring_candidate") is not True or not decision_id:
            continue
        raw_decision = dict(row.get("raw_decision") or {})
        label = str(
            row.get("source_title")
            or raw_decision.get("source_title")
            or row.get("selection_source_id")
            or decision_id
        ).strip()
        results.append(
            CatalogItem(
                source_type=SourceType.SELECTED_STRATEGY.value,
                source_ref=decision_id,
                instrument_kind="strategy",
                label=label,
                metadata={
                    "decision_id": decision_id,
                    "decision_route": row.get("decision_route"),
                    "source_id": row.get("source_id") or raw_decision.get("source_id"),
                    "selection_source_id": row.get("selection_source_id"),
                    "updated_at": row.get("updated_at"),
                    "baseline_start": row.get("baseline_start"),
                },
                readiness="READY",
            )
        )
    return sorted(
        results,
        key=lambda item: (
            str(item.metadata.get("updated_at") or ""),
            item.source_ref,
        ),
        reverse=True,
    )


def search_monitoring_catalog(
    query: str,
    source_type: SourceType | str,
    *,
    db_factory: Callable[[], MySQLClient],
    decision_loader: Callable[[], Iterable[dict[str, Any]]] | None = None,
    limit: int = 20,
) -> list[CatalogItem]:
    normalized_source = str(getattr(source_type, "value", source_type)).strip()
    if normalized_source == SourceType.DIRECT_SECURITY.value:
        return search_direct_securities(query, db_factory=db_factory, limit=limit)
    if normalized_source != SourceType.SELECTED_STRATEGY.value:
        raise ValueError(f"Unsupported monitoring catalog source type: {source_type!r}")

    clean_query = str(query or "").strip().casefold()
    candidates = list_monitoring_candidates(decision_loader=decision_loader)
    if clean_query:
        candidates = [
            item
            for item in candidates
            if clean_query in item.source_ref.casefold()
            or clean_query in item.label.casefold()
            or clean_query in str(item.metadata.get("source_id") or "").casefold()
        ]
    return candidates[: _bounded_limit(limit)]
