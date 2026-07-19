from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class ExposureBucket:
    dimension: str
    key: str
    weight: float
    monitoring_item_id: str
    provenance: str
    source_date: str | None


@dataclass(frozen=True)
class ExposureResult:
    buckets: tuple[ExposureBucket, ...]
    total_weight: float
    covered_weight: float
    uncovered_weight: float
    coverage_ratio: float

    def bucket_weight(self, dimension: str, key: str) -> float:
        return sum(
            row.weight
            for row in self.buckets
            if row.dimension == dimension and row.key == key
        )


def _value(source: Any, key: str, default: Any = None) -> Any:
    if isinstance(source, Mapping):
        return source.get(key, default)
    return getattr(source, key, default)


def _weight(item: Any) -> float:
    value = _value(item, "portfolio_weight", _value(item, "weight", 1.0))
    try:
        return max(float(value), 0.0)
    except (TypeError, ValueError):
        return 0.0


def _item_id(item: Any) -> str:
    return str(_value(item, "monitoring_item_id", _value(item, "source_ref", "unknown")))


def _result(
    item: Any,
    buckets: list[ExposureBucket],
    covered_weight: float,
) -> ExposureResult:
    total_weight = _weight(item)
    covered = min(max(covered_weight, 0.0), total_weight)
    uncovered = max(total_weight - covered, 0.0)
    return ExposureResult(
        buckets=tuple(buckets),
        total_weight=total_weight,
        covered_weight=covered,
        uncovered_weight=uncovered,
        coverage_ratio=(covered / total_weight if total_weight else 0.0),
    )


def _bucket(
    item: Any,
    dimension: str,
    key: Any,
    weight: float,
    provenance: str,
    source_date: Any,
) -> ExposureBucket | None:
    label = str(key or "").strip()
    if not label or weight <= 0:
        return None
    return ExposureBucket(
        dimension=dimension,
        key=label,
        weight=weight,
        monitoring_item_id=_item_id(item),
        provenance=provenance,
        source_date=(str(source_date) if source_date else None),
    )


def build_direct_stock_exposure(item: Any, asset_profile: Any) -> ExposureResult:
    """Project only persisted stock classifications; missing facts remain uncovered."""

    item_weight = _weight(item)
    if not isinstance(asset_profile, Mapping):
        return _result(item, [], 0.0)
    source_date = asset_profile.get("as_of_date")
    rows: list[ExposureBucket] = []
    for dimension in ("sector", "industry", "asset"):
        row = _bucket(
            item,
            dimension,
            asset_profile.get(dimension),
            item_weight,
            "direct_asset_profile",
            source_date,
        )
        if row is not None:
            rows.append(row)
    symbol = _value(item, "source_ref")
    symbol_row = _bucket(item, "symbol", symbol, item_weight, "direct_security", source_date)
    if symbol_row is not None:
        rows.append(symbol_row)
    covered = item_weight if rows else 0.0
    return _result(item, rows, covered)


def _lookthrough_rows(
    item: Any,
    entries: Sequence[Mapping[str, Any]],
    *,
    source_date: Any,
    provenance: str,
) -> tuple[list[ExposureBucket], float]:
    item_weight = _weight(item)
    rows: list[ExposureBucket] = []
    covered_fraction = 0.0
    for entry in entries:
        try:
            fraction = max(float(entry.get("weight", 0.0)), 0.0)
        except (TypeError, ValueError):
            continue
        if fraction <= 0:
            continue
        covered_fraction += fraction
        absolute_weight = item_weight * fraction
        for dimension in ("symbol", "sector", "industry", "asset"):
            row = _bucket(
                item,
                dimension,
                entry.get(dimension),
                absolute_weight,
                provenance,
                source_date,
            )
            if row is not None:
                rows.append(row)
    return rows, item_weight * min(covered_fraction, 1.0)


def build_etf_exposure(item: Any, holdings_snapshot: Any, exposure_snapshot: Any) -> ExposureResult:
    """Prefer stored holdings look-through; use top-level exposure only as fallback."""

    if isinstance(holdings_snapshot, Mapping) and isinstance(holdings_snapshot.get("holdings"), Sequence):
        entries = [row for row in holdings_snapshot["holdings"] if isinstance(row, Mapping)]
        if entries:
            rows, covered = _lookthrough_rows(
                item,
                entries,
                source_date=holdings_snapshot.get("as_of_date"),
                provenance="etf_holdings_lookthrough",
            )
            return _result(item, rows, covered)

    rows: list[ExposureBucket] = []
    covered_fraction = 0.0
    if isinstance(exposure_snapshot, Mapping):
        source_date = exposure_snapshot.get("as_of_date")
        for dimension, field in (("asset", "asset_weights"), ("sector", "sector_weights")):
            weights = exposure_snapshot.get(field)
            if not isinstance(weights, Mapping):
                continue
            dimension_total = 0.0
            for key, raw_weight in weights.items():
                try:
                    fraction = max(float(raw_weight), 0.0)
                except (TypeError, ValueError):
                    continue
                dimension_total += fraction
                row = _bucket(
                    item,
                    dimension,
                    key,
                    _weight(item) * fraction,
                    "etf_top_level_exposure",
                    source_date,
                )
                if row is not None:
                    rows.append(row)
            covered_fraction = max(covered_fraction, min(dimension_total, 1.0))
    return _result(item, rows, _weight(item) * covered_fraction)


def build_selected_strategy_exposure(item: Any, target_snapshot: Any) -> ExposureResult:
    targets = target_snapshot.get("targets") if isinstance(target_snapshot, Mapping) else None
    if not isinstance(targets, Sequence):
        return _result(item, [], 0.0)
    rows, covered = _lookthrough_rows(
        item,
        [row for row in targets if isinstance(row, Mapping)],
        source_date=target_snapshot.get("as_of_date"),
        provenance="selected_strategy_targets",
    )
    return _result(item, rows, covered)


def aggregate_group_exposure(items: Sequence[ExposureResult]) -> ExposureResult:
    total_weight = sum(row.total_weight for row in items)
    covered_weight = sum(row.covered_weight for row in items)
    uncovered_weight = sum(row.uncovered_weight for row in items)
    return ExposureResult(
        buckets=tuple(bucket for row in items for bucket in row.buckets),
        total_weight=total_weight,
        covered_weight=covered_weight,
        uncovered_weight=uncovered_weight,
        coverage_ratio=(covered_weight / total_weight if total_weight else 0.0),
    )
