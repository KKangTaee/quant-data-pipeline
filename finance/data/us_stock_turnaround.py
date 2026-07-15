from __future__ import annotations

from collections.abc import Collection, Iterable, Mapping, Sequence
from typing import Any

import pandas as pd


def _concept_priority(value: Any, concepts: Sequence[str]) -> int | None:
    text = str(value or "").strip()
    suffix = text.split(":", 1)[-1]
    for index, candidate in enumerate(concepts):
        normalized = str(candidate).strip()
        if text == normalized or suffix == normalized.split(":", 1)[-1]:
            return index
    return None


def _normalized_units(units: Collection[str]) -> set[str]:
    return {str(unit).strip().casefold() for unit in units}


def _primary_period_fact(row: Mapping[str, Any]) -> bool:
    period_end = pd.to_datetime(row.get("period_end"), errors="coerce")
    report_date = pd.to_datetime(row.get("report_date"), errors="coerce")
    if pd.isna(period_end):
        return False
    if not pd.isna(report_date):
        return pd.Timestamp(report_date).normalize() == pd.Timestamp(period_end).normalize()
    available_at = pd.to_datetime(row.get("available_at"), errors="coerce")
    if pd.isna(available_at):
        return False
    lag = (pd.Timestamp(available_at).normalize() - pd.Timestamp(period_end).normalize()).days
    return 0 <= int(lag) <= 180


def _normalized_rows(
    statement_rows: Iterable[Mapping[str, Any]],
    *,
    concepts: Sequence[str],
    units: Collection[str],
    as_of_date: str,
    source_period_type: str,
) -> list[dict[str, Any]]:
    cutoff = pd.Timestamp(as_of_date).normalize() + pd.Timedelta(days=1)
    allowed_units = _normalized_units(units)
    normalized: list[dict[str, Any]] = []
    for raw in statement_rows:
        row = dict(raw)
        priority = _concept_priority(row.get("concept"), concepts)
        available_at = pd.to_datetime(row.get("available_at"), errors="coerce")
        period_end = pd.to_datetime(row.get("period_end"), errors="coerce")
        period_start = pd.to_datetime(row.get("period_start"), errors="coerce")
        value = pd.to_numeric(row.get("value"), errors="coerce")
        if (
            priority is None
            or str(row.get("unit") or "").strip().casefold() not in allowed_units
            or str(row.get("source_period_type") or "").strip().casefold()
            != source_period_type.casefold()
            or pd.isna(available_at)
            or pd.Timestamp(available_at) >= cutoff
            or pd.isna(period_end)
            or pd.isna(value)
            or not _primary_period_fact(row)
        ):
            continue
        fiscal_year = pd.to_numeric(row.get("fiscal_year"), errors="coerce")
        fiscal_quarter = pd.to_numeric(row.get("fiscal_quarter"), errors="coerce")
        normalized.append(
            {
                **row,
                "concept_priority": priority,
                "period_start_ts": None if pd.isna(period_start) else pd.Timestamp(period_start),
                "period_end_ts": pd.Timestamp(period_end),
                "available_at_ts": pd.Timestamp(available_at),
                "value_number": float(value),
                "fiscal_year_number": None if pd.isna(fiscal_year) else int(fiscal_year),
                "fiscal_quarter_number": None if pd.isna(fiscal_quarter) else int(fiscal_quarter),
            }
        )
    return normalized


def _duration_kind(row: Mapping[str, Any]) -> str | None:
    start = row.get("period_start_ts")
    end = row.get("period_end_ts")
    if start is None or end is None:
        return None
    days = int((pd.Timestamp(end) - pd.Timestamp(start)).days) + 1
    period_type = str(row.get("period_type") or "").upper()
    quarter = row.get("fiscal_quarter_number")
    if period_type == "FY" or days >= 321:
        return "FY"
    if 60 <= days <= 140:
        return "DIRECT"
    if 141 <= days <= 230 and quarter in {2, None}:
        return "H1"
    if 231 <= days <= 320 and quarter in {3, None}:
        return "9M"
    return None


def _operand(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "accession_no": row.get("accession_no"),
        "concept": row.get("concept"),
        "unit": row.get("unit"),
        "period_start": (
            row.get("period_start_ts").strftime("%Y-%m-%d")
            if row.get("period_start_ts") is not None
            else None
        ),
        "period_end": row.get("period_end_ts").strftime("%Y-%m-%d"),
        "available_at": row.get("available_at_ts").strftime("%Y-%m-%d"),
        "value": float(row.get("value_number")),
    }


def _resolved_row(
    base: Mapping[str, Any],
    *,
    metric: str,
    fiscal_quarter: int,
    value: float,
    available_at: pd.Timestamp,
    derivation: str,
    operands: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "symbol": base.get("symbol"),
        "metric": metric,
        "concept": base.get("concept"),
        "unit": base.get("unit"),
        "fiscal_year": base.get("fiscal_year_number"),
        "fiscal_quarter": int(fiscal_quarter),
        "period_start": (
            base.get("period_start_ts").strftime("%Y-%m-%d")
            if base.get("period_start_ts") is not None
            else None
        ),
        "period_end": base.get("period_end_ts").strftime("%Y-%m-%d"),
        "value": float(value),
        "available_at": pd.Timestamp(available_at).strftime("%Y-%m-%d"),
        "accession_no": base.get("accession_no"),
        "source_period_type": "duration",
        "derivation": derivation,
        "concept_priority": int(base.get("concept_priority") or 0),
        "provenance": {
            "rule": derivation,
            "operands": [_operand(row) for row in operands],
        },
    }


def _latest(rows: Sequence[dict[str, Any]]) -> dict[str, Any] | None:
    if not rows:
        return None
    return sorted(
        rows,
        key=lambda row: (
            row["available_at_ts"],
            str(row.get("accession_no") or ""),
        ),
    )[-1]


def _resolved_as_operand(row: Mapping[str, Any]) -> dict[str, Any]:
    """Expose a derived quarter as one logical FY-subtraction operand."""
    return {
        "accession_no": row.get("accession_no"),
        "concept": row.get("concept"),
        "unit": row.get("unit"),
        "period_start_ts": pd.to_datetime(row.get("period_start"), errors="coerce"),
        "period_end_ts": pd.Timestamp(str(row.get("period_end"))),
        "available_at_ts": pd.Timestamp(str(row.get("available_at"))),
        "value_number": float(row.get("value") or 0.0),
    }


def resolve_discrete_quarters(
    statement_rows: Iterable[Mapping[str, Any]],
    *,
    metric: str,
    concepts: Sequence[str],
    units: Collection[str],
    as_of_date: str,
) -> list[dict[str, Any]]:
    rows = _normalized_rows(
        statement_rows,
        concepts=concepts,
        units=units,
        as_of_date=as_of_date,
        source_period_type="duration",
    )
    by_family: dict[tuple[Any, Any, Any, Any], list[dict[str, Any]]] = {}
    for row in rows:
        key = (
            row.get("symbol"),
            row.get("fiscal_year_number"),
            row.get("concept"),
            str(row.get("unit") or "").casefold(),
        )
        by_family.setdefault(key, []).append(row)

    candidates: list[dict[str, Any]] = []
    for family_rows in by_family.values():
        kinds: dict[str, list[dict[str, Any]]] = {"DIRECT": [], "H1": [], "9M": [], "FY": []}
        for row in family_rows:
            kind = _duration_kind(row)
            if kind:
                kinds[kind].append(row)
        direct: dict[int, dict[str, Any]] = {}
        for quarter in (1, 2, 3, 4):
            selected = _latest(
                [row for row in kinds["DIRECT"] if row.get("fiscal_quarter_number") == quarter]
            )
            if selected is not None:
                direct[quarter] = selected

        resolved: dict[int, dict[str, Any]] = {}
        for quarter, row in direct.items():
            resolved[quarter] = _resolved_row(
                row,
                metric=metric,
                fiscal_quarter=quarter,
                value=row["value_number"],
                available_at=row["available_at_ts"],
                derivation="reported_quarter",
                operands=[row],
            )

        q1 = direct.get(1)
        h1 = _latest(kinds["H1"])
        if 2 not in resolved and q1 is not None and h1 is not None:
            resolved[2] = _resolved_row(
                h1,
                metric=metric,
                fiscal_quarter=2,
                value=h1["value_number"] - q1["value_number"],
                available_at=max(h1["available_at_ts"], q1["available_at_ts"]),
                derivation="h1_minus_q1",
                operands=[h1, q1],
            )
        nine_months = _latest(kinds["9M"])
        if 3 not in resolved and h1 is not None and nine_months is not None:
            resolved[3] = _resolved_row(
                nine_months,
                metric=metric,
                fiscal_quarter=3,
                value=nine_months["value_number"] - h1["value_number"],
                available_at=max(nine_months["available_at_ts"], h1["available_at_ts"]),
                derivation="nine_months_minus_h1",
                operands=[nine_months, h1],
            )
        fiscal_year = _latest(kinds["FY"])
        if 4 not in resolved and fiscal_year is not None and set(resolved) >= {1, 2, 3}:
            q_values = [resolved[quarter]["value"] for quarter in (1, 2, 3)]
            logical_operands = [fiscal_year] + [
                _resolved_as_operand(resolved[quarter]) for quarter in (1, 2, 3)
            ]
            resolved[4] = _resolved_row(
                fiscal_year,
                metric=metric,
                fiscal_quarter=4,
                value=fiscal_year["value_number"] - sum(q_values),
                available_at=max(
                    [fiscal_year["available_at_ts"]]
                    + [pd.Timestamp(resolved[quarter]["available_at"]) for quarter in (1, 2, 3)]
                ),
                derivation="fy_minus_q1_q2_q3",
                operands=logical_operands,
            )
        candidates.extend(resolved.values())

    selected: dict[tuple[Any, Any, Any], dict[str, Any]] = {}
    for row in sorted(
        candidates,
        key=lambda item: (
            item["concept_priority"],
            0 if item["derivation"] == "reported_quarter" else 1,
            item["available_at"],
        ),
    ):
        key = (row.get("symbol"), row.get("fiscal_year"), row.get("fiscal_quarter"))
        selected.setdefault(key, row)
    return sorted(
        selected.values(),
        key=lambda row: (row["period_end"], row["available_at"], row["fiscal_quarter"]),
    )


def resolve_instant_facts(
    statement_rows: Iterable[Mapping[str, Any]],
    *,
    metric: str,
    concepts: Sequence[str],
    units: Collection[str],
    as_of_date: str,
) -> list[dict[str, Any]]:
    rows = _normalized_rows(
        statement_rows,
        concepts=concepts,
        units=units,
        as_of_date=as_of_date,
        source_period_type="instant",
    )
    selected: dict[tuple[Any, str], dict[str, Any]] = {}
    for row in sorted(
        rows,
        key=lambda item: (
            item["concept_priority"],
            item["available_at_ts"],
            str(item.get("accession_no") or ""),
        ),
    ):
        key = (row.get("symbol"), row["period_end_ts"].strftime("%Y-%m-%d"))
        if key in selected and selected[key]["concept_priority"] < row["concept_priority"]:
            continue
        selected[key] = row
    return [
        {
            "symbol": row.get("symbol"),
            "metric": metric,
            "concept": row.get("concept"),
            "unit": row.get("unit"),
            "fiscal_year": row.get("fiscal_year_number"),
            "fiscal_quarter": row.get("fiscal_quarter_number"),
            "period_end": row["period_end_ts"].strftime("%Y-%m-%d"),
            "value": row["value_number"],
            "available_at": row["available_at_ts"].strftime("%Y-%m-%d"),
            "accession_no": row.get("accession_no"),
            "source_period_type": "instant",
            "derivation": "reported_instant",
            "provenance": {"rule": "reported_instant", "operands": [_operand(row)]},
        }
        for row in sorted(selected.values(), key=lambda item: item["period_end_ts"])
    ]


def build_split_neutral_share_series(
    quarter_rows: Iterable[Mapping[str, Any]],
    price_rows: Iterable[Mapping[str, Any]],
    *,
    as_of_date: str,
) -> list[dict[str, Any]]:
    as_of = pd.Timestamp(as_of_date).normalize()
    splits: list[tuple[pd.Timestamp, float]] = []
    for raw in price_rows:
        split_date = pd.to_datetime(raw.get("date"), errors="coerce")
        factor = pd.to_numeric(raw.get("stock_splits"), errors="coerce")
        if (
            not pd.isna(split_date)
            and pd.Timestamp(split_date).normalize() <= as_of
            and not pd.isna(factor)
            and float(factor) > 0
        ):
            splits.append((pd.Timestamp(split_date).normalize(), float(factor)))
    resolved: list[dict[str, Any]] = []
    for raw in quarter_rows:
        row = dict(raw)
        available_at = pd.to_datetime(row.get("available_at"), errors="coerce")
        value = pd.to_numeric(row.get("value"), errors="coerce")
        if pd.isna(available_at) or pd.Timestamp(available_at).normalize() > as_of or pd.isna(value):
            continue
        factor = 1.0
        for split_date, split_value in splits:
            if pd.Timestamp(available_at).normalize() < split_date <= as_of:
                factor *= split_value
        resolved.append(
            {
                **row,
                "split_factor": factor,
                "split_neutral_value": float(value) * factor,
            }
        )
    return sorted(resolved, key=lambda row: (str(row.get("period_end") or ""), str(row.get("available_at") or "")))
