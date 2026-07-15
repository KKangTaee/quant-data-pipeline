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


def _resolved_fact_operand(metric: str, row: Mapping[str, Any]) -> dict[str, Any]:
    """Keep one resolved metric result as structured timeline provenance."""
    return {
        "metric": metric,
        "accession_no": row.get("accession_no"),
        "concept": row.get("concept"),
        "unit": row.get("unit"),
        "period_start": row.get("period_start"),
        "period_end": row.get("period_end"),
        "available_at": row.get("available_at"),
        "value": row.get("value"),
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

    # SEC taxonomy names can change within one fiscal year. Only after exact-concept
    # resolution fails, combine operands from the caller's explicit metric family.
    fiscal_year_families: dict[tuple[Any, int, str], list[dict[str, Any]]] = {}
    for row in rows:
        fiscal_year = row.get("fiscal_year_number")
        if fiscal_year is None or _duration_kind(row) != "FY":
            continue
        family_key = (
            row.get("symbol"),
            int(fiscal_year),
            str(row.get("unit") or "").casefold(),
        )
        fiscal_year_families.setdefault(family_key, []).append(row)

    for (symbol, fiscal_year, unit), fiscal_year_rows in fiscal_year_families.items():
        q4_key = (symbol, fiscal_year, 4)
        if q4_key in selected:
            continue
        quarter_rows = [selected.get((symbol, fiscal_year, quarter)) for quarter in (1, 2, 3)]
        if any(row is None for row in quarter_rows):
            continue
        complete_quarters = [row for row in quarter_rows if row is not None]
        if any(str(row.get("unit") or "").casefold() != unit for row in complete_quarters):
            continue
        minimum_priority = min(
            int(row.get("concept_priority") or 0) for row in fiscal_year_rows
        )
        fiscal_year_row = _latest(
            [
                row
                for row in fiscal_year_rows
                if int(row.get("concept_priority") or 0) == minimum_priority
            ]
        )
        if fiscal_year_row is None:
            continue
        logical_operands = [fiscal_year_row] + [
            _resolved_as_operand(row) for row in complete_quarters
        ]
        selected[q4_key] = _resolved_row(
            fiscal_year_row,
            metric=metric,
            fiscal_quarter=4,
            value=float(fiscal_year_row["value_number"])
            - sum(float(row["value"]) for row in complete_quarters),
            available_at=max(
                [fiscal_year_row["available_at_ts"]]
                + [pd.Timestamp(row["available_at"]) for row in complete_quarters]
            ),
            derivation="fy_minus_q1_q2_q3",
            operands=logical_operands,
        )
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


TURNAROUND_CONCEPT_FAMILIES: dict[str, tuple[str, ...]] = {
    "revenue": (
        "us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax",
        "us-gaap:Revenues",
        "us-gaap:SalesRevenueNet",
    ),
    "gross_profit": ("us-gaap:GrossProfit",),
    "cost_of_revenue": (
        "us-gaap:CostOfRevenue",
        "us-gaap:CostOfGoodsAndServicesSold",
        "us-gaap:CostOfGoodsSold",
    ),
    "operating_income": ("us-gaap:OperatingIncomeLoss",),
    "net_income": ("us-gaap:NetIncomeLoss", "us-gaap:ProfitLoss"),
    "ocf": ("us-gaap:NetCashProvidedByUsedInOperatingActivities",),
    "capex": ("us-gaap:PaymentsToAcquirePropertyPlantAndEquipment",),
    "diluted_eps": (
        "us-gaap:EarningsPerShareDiluted",
        "us-gaap:EarningsPerShareBasicAndDiluted",
        "ifrs-full:DilutedEarningsLossPerShare",
    ),
    "diluted_shares": (
        "us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding",
        "us-gaap:WeightedAverageNumberOfShareOutstandingBasicAndDiluted",
    ),
    "interest_expense": (
        "us-gaap:InterestExpenseNonOperating",
        "us-gaap:InterestAndDebtExpense",
        "us-gaap:InterestExpense",
    ),
    "da": (
        "us-gaap:DepreciationDepletionAndAmortization",
        "us-gaap:DepreciationDepletionAndAmortizationPropertyPlantAndEquipment",
    ),
}

_TURNAROUND_METRIC_UNITS: dict[str, tuple[str, ...]] = {
    **{
        metric: ("USD",)
        for metric in (
            "revenue",
            "gross_profit",
            "cost_of_revenue",
            "operating_income",
            "net_income",
            "ocf",
            "capex",
            "interest_expense",
            "da",
        )
    },
    "diluted_eps": ("USD per share", "USD/shares", "USD/share"),
    "diluted_shares": ("shares",),
}

TURNAROUND_INSTANT_CONCEPT_FAMILIES: dict[str, tuple[str, ...]] = {
    "cash": ("us-gaap:CashAndCashEquivalentsAtCarryingValue",),
    "short_term_investments": (
        "us-gaap:ShortTermInvestments",
        "us-gaap:MarketableSecuritiesCurrent",
    ),
    "debt_direct": (
        "us-gaap:LongTermDebtAndFinanceLeaseObligations",
        "us-gaap:DebtAndCapitalLeaseObligations",
    ),
    "debt_current": (
        "us-gaap:LongTermDebtAndFinanceLeaseObligationsCurrent",
        "us-gaap:LongTermDebtCurrent",
        "us-gaap:ShortTermBorrowings",
    ),
    "debt_noncurrent": (
        "us-gaap:LongTermDebtAndFinanceLeaseObligationsNoncurrent",
        "us-gaap:LongTermDebtNoncurrent",
    ),
}

_INSTANT_CONCEPT_FAMILIES = TURNAROUND_INSTANT_CONCEPT_FAMILIES

_TTM_METRICS = (
    "revenue",
    "gross_profit",
    "operating_income",
    "net_income",
    "ocf",
    "capex",
    "diluted_eps",
    "interest_expense",
    "da",
)


def _slot_ordinal(fiscal_year: int, fiscal_quarter: int) -> int:
    return int(fiscal_year) * 4 + int(fiscal_quarter) - 1


def _slot_identity(ordinal: int) -> tuple[int, int]:
    return int(ordinal // 4), int(ordinal % 4) + 1


def _metric_map(rows: Iterable[Mapping[str, Any]]) -> dict[tuple[int, int], dict[str, Any]]:
    mapped: dict[tuple[int, int], dict[str, Any]] = {}
    for raw in rows:
        row = dict(raw)
        year = row.get("fiscal_year")
        quarter = row.get("fiscal_quarter")
        if year is None or quarter not in {1, 2, 3, 4}:
            continue
        mapped[(int(year), int(quarter))] = row
    return mapped


def _sum_window(
    timeline: Sequence[Mapping[str, Any]],
    *,
    index: int,
    metric: str,
) -> float | None:
    if index < 3:
        return None
    values = [timeline[position].get(metric) for position in range(index - 3, index + 1)]
    if any(value is None for value in values):
        return None
    return float(sum(float(value) for value in values))


def _pct_change(current: Any, previous: Any) -> float | None:
    if current is None or previous is None:
        return None
    denominator = float(previous)
    if denominator == 0:
        return None
    return (float(current) / denominator - 1.0) * 100.0


def _build_current_balance(
    statements: Sequence[Mapping[str, Any]],
    *,
    as_of_date: str,
) -> dict[str, Any]:
    instant_rows = {
        metric: resolve_instant_facts(
            statements,
            metric=metric,
            concepts=concepts,
            units=("USD",),
            as_of_date=as_of_date,
        )
        for metric, concepts in _INSTANT_CONCEPT_FAMILIES.items()
    }
    latest = {
        metric: sorted(rows, key=lambda item: (item["period_end"], item["available_at"]))[-1]
        for metric, rows in instant_rows.items()
        if rows
    }
    balance: dict[str, Any] = {
        metric: row.get("value")
        for metric, row in latest.items()
        if metric in {"cash", "short_term_investments"}
    }
    debt_sources: list[dict[str, Any]] = []
    if "debt_direct" in latest:
        balance["total_debt"] = latest["debt_direct"].get("value")
        debt_sources = [latest["debt_direct"]]
    elif {"debt_current", "debt_noncurrent"}.issubset(latest):
        current = latest["debt_current"]
        noncurrent = latest["debt_noncurrent"]
        if (
            current.get("period_end") == noncurrent.get("period_end")
            and current.get("accession_no") == noncurrent.get("accession_no")
        ):
            balance["total_debt"] = float(current.get("value") or 0.0) + float(
                noncurrent.get("value") or 0.0
            )
            debt_sources = [current, noncurrent]
    used_sources = [
        row
        for metric, row in latest.items()
        if metric in {"cash", "short_term_investments"}
    ] + debt_sources
    if used_sources:
        component_keys = {
            (str(row.get("period_end") or ""), str(row.get("accession_no") or ""))
            for row in used_sources
        }
        balance.update(
            {
                "currency": "USD",
                "basis_date": max(row["period_end"] for row in used_sources),
                "available_at": max(row["available_at"] for row in used_sources),
                "accession_no": max(
                    (str(row.get("accession_no") or "") for row in used_sources),
                    default=None,
                )
                or None,
                "component_alignment": len(component_keys) == 1,
            }
        )
    return balance


def build_turnaround_quarterly_series(
    statement_rows: Iterable[Mapping[str, Any]],
    price_rows: Iterable[Mapping[str, Any]],
    *,
    as_of_date: str,
) -> dict[str, Any]:
    """Build a gap-preserving fiscal-quarter timeline from stored filing facts."""
    statements = [dict(row) for row in statement_rows]
    prices = [dict(row) for row in price_rows]
    current_balance = _build_current_balance(statements, as_of_date=as_of_date)
    resolved: dict[str, list[dict[str, Any]]] = {
        metric: resolve_discrete_quarters(
            statements,
            metric=metric,
            concepts=concepts,
            units=_TURNAROUND_METRIC_UNITS[metric],
            as_of_date=as_of_date,
        )
        for metric, concepts in TURNAROUND_CONCEPT_FAMILIES.items()
    }
    resolved["diluted_shares"] = build_split_neutral_share_series(
        resolved["diluted_shares"],
        prices,
        as_of_date=as_of_date,
    )
    maps = {metric: _metric_map(rows) for metric, rows in resolved.items()}
    keys = {
        key
        for metric_rows in maps.values()
        for key in metric_rows
    }
    if not keys:
        return {
            "status": "BLOCKED",
            "timeline": [],
            "series": [],
            "current_balance": current_balance,
            "currency": "USD",
        }
    ordinals = [_slot_ordinal(year, quarter) for year, quarter in keys]
    timeline: list[dict[str, Any]] = []
    for ordinal in range(min(ordinals), max(ordinals) + 1):
        year, quarter = _slot_identity(ordinal)
        key = (year, quarter)
        metric_reasons: dict[str, str] = {}
        row: dict[str, Any] = {
            "slot_index": len(timeline),
            "slot_key": f"{year}-Q{quarter}",
            "fiscal_year": year,
            "fiscal_quarter": quarter,
            "status": "MISSING",
            "metric_reasons": metric_reasons,
            "metric_provenance": {},
            "derived_metrics": [],
        }
        evidence_rows: list[dict[str, Any]] = []
        for metric in TURNAROUND_CONCEPT_FAMILIES:
            fact = maps[metric].get(key)
            value_key = (
                "split_neutral_value" if metric == "diluted_shares" else "value"
            )
            value = None if fact is None else fact.get(value_key)
            if metric == "capex" and value is not None:
                value = abs(float(value))
            row[metric] = None if value is None else float(value)
            if fact is not None:
                evidence_rows.append(fact)
                derivation = str(fact.get("derivation") or "reported_quarter")
                source_kind = (
                    "REPORTED" if derivation == "reported_quarter" else "FILING_DERIVED"
                )
                row["metric_provenance"][metric] = {
                    "source_kind": source_kind,
                    "rule": derivation,
                    "operands": list(
                        dict(fact.get("provenance") or {}).get("operands") or []
                    ),
                }
                if source_kind == "FILING_DERIVED":
                    row["derived_metrics"].append(metric)
        if row["gross_profit"] is None and row["revenue"] is not None and row["cost_of_revenue"] is not None:
            revenue_fact = maps["revenue"].get(key) or {}
            cost_fact = maps["cost_of_revenue"].get(key) or {}
            compatible = (
                revenue_fact.get("accession_no") == cost_fact.get("accession_no")
                and str(revenue_fact.get("unit") or "").casefold()
                == str(cost_fact.get("unit") or "").casefold()
            )
            if compatible:
                row["gross_profit"] = float(row["revenue"]) - float(row["cost_of_revenue"])
                row["gross_profit_derivation"] = "revenue_minus_cost"
                row["metric_provenance"]["gross_profit"] = {
                    "source_kind": "FILING_DERIVED",
                    "rule": "revenue_minus_cost",
                    "operands": [
                        _resolved_fact_operand("revenue", revenue_fact),
                        _resolved_fact_operand("cost_of_revenue", cost_fact),
                    ],
                }
                row["derived_metrics"].append("gross_profit")
            else:
                metric_reasons["gross_profit"] = "INCOMPATIBLE_REVENUE_COST_PROVENANCE"
        row["derived_metrics"] = sorted(set(row["derived_metrics"]))
        available_dates = [pd.to_datetime(item.get("available_at"), errors="coerce") for item in evidence_rows]
        available_dates = [pd.Timestamp(value) for value in available_dates if not pd.isna(value)]
        period_ends = [str(item.get("period_end")) for item in evidence_rows if item.get("period_end")]
        row["available_at"] = max(available_dates).strftime("%Y-%m-%d") if available_dates else None
        row["period_end"] = max(period_ends) if period_ends else None
        if any(row.get(metric) is not None for metric in ("revenue", "operating_income", "ocf", "diluted_eps")):
            row["status"] = "AVAILABLE"
        timeline.append(row)

    for index, row in enumerate(timeline):
        row["ttm_derived_metrics"] = (
            sorted(
                {
                    metric
                    for position in range(index - 3, index + 1)
                    for metric in timeline[position].get("derived_metrics", [])
                }
            )
            if index >= 3
            else []
        )
        for metric in _TTM_METRICS:
            ttm_key = f"ttm_{metric}"
            row[ttm_key] = _sum_window(timeline, index=index, metric=metric)
            if index >= 3 and row[ttm_key] is None:
                row["metric_reasons"][ttm_key] = "MISSING_QUARTER_IN_WINDOW"
        row["ttm_eps"] = row.get("ttm_diluted_eps")
        if row["ttm_ocf"] is not None and row["ttm_capex"] is not None:
            row["ttm_fcf"] = float(row["ttm_ocf"]) - float(row["ttm_capex"])
        else:
            row["ttm_fcf"] = None
        revenue = row.get("ttm_revenue")
        if revenue is not None and float(revenue) > 0:
            row["ttm_gross_margin_pct"] = (
                float(row["ttm_gross_profit"]) / float(revenue) * 100.0
                if row.get("ttm_gross_profit") is not None
                else None
            )
            row["ttm_operating_margin_pct"] = (
                float(row["ttm_operating_income"]) / float(revenue) * 100.0
                if row.get("ttm_operating_income") is not None
                else None
            )
        else:
            row["ttm_gross_margin_pct"] = None
            row["ttm_operating_margin_pct"] = None
        if index >= 4:
            previous = timeline[index - 4]
            row["revenue_yoy_pct"] = _pct_change(row.get("revenue"), previous.get("revenue"))
            row["ttm_revenue_yoy_pct"] = _pct_change(row.get("ttm_revenue"), previous.get("ttm_revenue"))
            current_margin = row.get("ttm_operating_margin_pct")
            previous_margin = previous.get("ttm_operating_margin_pct")
            row["operating_margin_yoy_delta_pp"] = (
                float(current_margin) - float(previous_margin)
                if current_margin is not None and previous_margin is not None
                else None
            )
        else:
            row["revenue_yoy_pct"] = None
            row["ttm_revenue_yoy_pct"] = None
            row["operating_margin_yoy_delta_pp"] = None
        row["split_neutral_diluted_shares"] = row.get("diluted_shares")

    available_series = [dict(row) for row in timeline if row["status"] == "AVAILABLE"]
    core_ready = len(timeline) >= 8 and any(
        row.get("ttm_revenue") is not None and row.get("ttm_ocf") is not None
        for row in timeline[-1:]
    )
    return {
        "status": "READY" if core_ready else "PARTIAL",
        "timeline": timeline,
        "series": available_series,
        "current_balance": current_balance,
        "currency": "USD",
    }


def _milestone(status: str, **evidence: Any) -> dict[str, Any]:
    return {"status": status, "evidence": evidence}


def classify_turnaround_milestones(
    series: Mapping[str, Any],
    *,
    per_status: str,
) -> dict[str, Any]:
    """Classify independent evidence milestones without funnel auto-passing."""
    timeline = [
        dict(row)
        for row in series.get("timeline") or []
        if str(row.get("status") or "AVAILABLE") == "AVAILABLE"
    ]
    names = (
        "LOSS_BASELINE",
        "OPERATING_IMPROVEMENT",
        "CASH_FLOW_TURN",
        "EARNINGS_TURN",
        "PER_CANDIDATE",
        "PER_READY",
    )
    if len(timeline) < 8:
        return {
            "status": "PARTIAL",
            "headline": "UNCONFIRMED",
            "milestones": {name: _milestone("UNKNOWN") for name in names},
            "evidence": {"quarter_count": len(timeline), "required_quarters": 8},
        }

    latest = timeline[-1]
    previous = timeline[-2]
    prior_year = timeline[-5]
    current_growth = latest.get("ttm_revenue_yoy_pct")
    previous_growth = previous.get("ttm_revenue_yoy_pct")
    revenue_direction = bool(
        current_growth is not None
        and (
            float(current_growth) > 0
            or (
                previous_growth is not None
                and float(current_growth) - float(previous_growth) >= 1.0
            )
        )
    )
    gross_margin = latest.get("ttm_gross_margin_pct")
    prior_gross_margin = prior_year.get("ttm_gross_margin_pct")
    gross_improvement = bool(
        latest.get("ttm_gross_profit") is not None
        and float(latest.get("ttm_gross_profit") or 0) > 0
        and gross_margin is not None
        and prior_gross_margin is not None
        and float(gross_margin) - float(prior_gross_margin) >= 1.0
    )
    operating_deltas = [
        float(row["operating_margin_yoy_delta_pp"])
        for row in timeline[-3:]
        if row.get("operating_margin_yoy_delta_pp") is not None
    ]
    operating_margin = latest.get("ttm_operating_margin_pct")
    prior_operating_margin = prior_year.get("ttm_operating_margin_pct")
    recent_operating_improvement_count = sum(
        delta >= 1.0 for delta in operating_deltas
    )
    latest_operating_margin_yoy_delta_pp = latest.get(
        "operating_margin_yoy_delta_pp"
    )
    operating_improvement = bool(
        recent_operating_improvement_count >= 2
        and operating_margin is not None
        and prior_operating_margin is not None
        and float(operating_margin) - float(prior_operating_margin) >= 1.0
    )
    operating_evidence_count = sum(
        (revenue_direction, gross_improvement, operating_improvement)
    )
    operating_met = operating_evidence_count >= 2

    ocf_values = [row.get("ttm_ocf") for row in timeline[-2:]]
    cash_met = len(ocf_values) == 2 and all(
        value is not None and float(value) > 0 for value in ocf_values
    )
    recent_eps = [row.get("diluted_eps") for row in timeline[-3:]]
    current_ttm_eps = latest.get("ttm_eps")
    earnings_met = (
        sum(value is not None and float(value) > 0 for value in recent_eps) >= 2
        and (current_ttm_eps is None or float(current_ttm_eps) <= 0)
    )
    per_candidate = current_ttm_eps is not None and float(current_ttm_eps) > 0
    recent_ttm_eps = [row.get("ttm_eps") for row in timeline[-4:]]
    per_ready = (
        str(per_status).upper() == "READY"
        and len(recent_ttm_eps) == 4
        and all(value is not None and float(value) > 0 for value in recent_ttm_eps)
    )
    improvement_present = operating_met or cash_met or earnings_met or per_candidate
    loss_baseline = (
        (current_ttm_eps is None or float(current_ttm_eps) <= 0)
        and not improvement_present
    )
    prior_ocf = prior_year.get("ttm_ocf")
    prior_fcf = prior_year.get("ttm_fcf")
    burn_improving = bool(
        (
            latest.get("ttm_ocf") is not None
            and prior_ocf is not None
            and float(latest["ttm_ocf"]) > float(prior_ocf)
        )
        or (
            latest.get("ttm_fcf") is not None
            and prior_fcf is not None
            and float(latest["ttm_fcf"]) > float(prior_fcf)
        )
    )
    milestones = {
        "LOSS_BASELINE": _milestone("MET" if loss_baseline else "NOT_MET"),
        "OPERATING_IMPROVEMENT": _milestone(
            "MET" if operating_met else "NOT_MET",
            revenue_direction=revenue_direction,
            gross_margin_improvement=gross_improvement,
            operating_margin_improvement=operating_improvement,
            current_operating_margin_pct=operating_margin,
            latest_operating_margin_yoy_delta_pp=latest_operating_margin_yoy_delta_pp,
            recent_operating_improvement_count=recent_operating_improvement_count,
            evidence_count=operating_evidence_count,
        ),
        "CASH_FLOW_TURN": _milestone(
            "MET" if cash_met else "NOT_MET",
            consecutive_positive_ttm_ocf=cash_met,
            fcf_confirmed=(
                latest.get("ttm_fcf") is not None and float(latest["ttm_fcf"]) > 0
            ),
        ),
        "EARNINGS_TURN": _milestone(
            "MET" if earnings_met else "NOT_MET",
            recent_positive_quarters=sum(
                value is not None and float(value) > 0 for value in recent_eps
            ),
            current_ttm_eps=current_ttm_eps,
        ),
        "PER_CANDIDATE": _milestone("MET" if per_candidate else "NOT_MET"),
        "PER_READY": _milestone("MET" if per_ready else "NOT_MET"),
    }
    headline = next(
        (
            name
            for name in (
                "PER_READY",
                "PER_CANDIDATE",
                "EARNINGS_TURN",
                "CASH_FLOW_TURN",
                "OPERATING_IMPROVEMENT",
                "LOSS_BASELINE",
            )
            if milestones[name]["status"] == "MET"
        ),
        "LOSS_BASELINE",
    )
    return {
        "status": "READY",
        "headline": headline,
        "milestones": milestones,
        "evidence": {
            "quarter_count": len(timeline),
            "burn_improving": burn_improving,
            "current_ttm_eps": current_ttm_eps,
        },
    }


def _number(value: Any) -> float | None:
    number = pd.to_numeric(value, errors="coerce")
    return None if pd.isna(number) else float(number)


def evaluate_turnaround_risks(series: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate survival and capital risks independently of operating stage."""
    timeline = [dict(row) for row in series.get("timeline") or []]
    latest = timeline[-1] if timeline else {}
    balance = dict(series.get("current_balance") or {})
    cash = _number(balance.get("cash"))
    investments = _number(balance.get("short_term_investments"))
    debt = _number(balance.get("total_debt"))
    liquidity = (
        float(cash or 0.0) + float(investments or 0.0)
        if cash is not None or investments is not None
        else None
    )
    ttm_fcf = _number(latest.get("ttm_fcf"))
    runway_quarters = (
        4.0 * float(liquidity) / abs(float(ttm_fcf))
        if liquidity is not None and ttm_fcf is not None and ttm_fcf < 0
        else None
    )
    runway_status = (
        "HIGH_RISK"
        if runway_quarters is not None and runway_quarters < 4
        else "WATCH"
        if runway_quarters is not None and runway_quarters < 8
        else "OK"
        if runway_quarters is not None
        else "NOT_APPLICABLE"
    )

    operating_income = _number(latest.get("ttm_operating_income"))
    interest = _number(latest.get("ttm_interest_expense"))
    coverage = (
        float(operating_income) / float(interest)
        if operating_income is not None
        and operating_income > 0
        and interest is not None
        and interest > 0
        else None
    )
    debt_status = (
        "NOT_MEANINGFUL"
        if operating_income is not None and operating_income <= 0
        else "UNKNOWN"
        if coverage is None
        else "HIGH_RISK"
        if coverage < 1.0
        else "WATCH"
        if coverage < 2.0
        else "OK"
    )

    current_shares = _number(latest.get("split_neutral_diluted_shares"))
    prior_shares = (
        _number(timeline[-5].get("split_neutral_diluted_shares"))
        if len(timeline) >= 5
        else None
    )
    dilution_yoy = _pct_change(current_shares, prior_shares)
    dilution_status = (
        "HIGH_RISK"
        if dilution_yoy is not None and dilution_yoy >= 10.0 - 1e-9
        else "WATCH"
        if dilution_yoy is not None and dilution_yoy >= 5.0 - 1e-9
        else "OK"
        if dilution_yoy is not None
        else "UNKNOWN"
    )
    net_debt = (
        float(debt) - float(cash or 0.0) - float(investments or 0.0)
        if debt is not None and liquidity is not None
        else None
    )
    ttm_ocf = _number(latest.get("ttm_ocf"))
    flags: list[str] = []
    if net_debt is not None and net_debt > 0 and ttm_ocf is not None and ttm_ocf <= 0:
        flags.append("NET_DEBT_WITH_NEGATIVE_OCF")
    return {
        "cash_runway": {
            "status": runway_status,
            "quarters": runway_quarters,
            "liquidity": liquidity,
            "ttm_fcf": ttm_fcf,
        },
        "debt_service": {
            "status": debt_status,
            "interest_coverage": coverage,
            "net_debt": net_debt,
        },
        "dilution": {"status": dilution_status, "yoy_pct": dilution_yoy},
        "flags": flags,
    }


_UNSUPPORTED_VALUATION_SECTOR_TERMS = (
    "bank",
    "insurance",
    "reit",
    "biotechnology",
    "oil & gas",
    "metals & mining",
)


def _valuation_block(reason_code: str, *, method: str | None = None) -> dict[str, Any]:
    return {
        "status": "BLOCKED",
        "method": method,
        "reason_code": reason_code,
        "multiple": None,
        "yield_pct": None,
    }


def route_turnaround_valuation(
    *,
    series: Mapping[str, Any],
    profile: Mapping[str, Any],
    latest_price: Mapping[str, Any] | None,
    per_status: str,
    as_of_date: str,
) -> dict[str, Any]:
    """Expose only the highest-priority stage-appropriate valuation method."""
    if str(per_status).upper() == "READY":
        return {
            "status": "READY",
            "method": "P_E_HANDOFF",
            "reason_code": None,
            "multiple": None,
            "yield_pct": None,
            "handoff": "PER 상대가치",
        }
    timeline = [dict(row) for row in series.get("timeline") or []]
    latest = timeline[-1] if timeline else {}
    balance = dict(series.get("current_balance") or {})
    market_cap = _number(profile.get("market_cap"))
    profile_date = pd.to_datetime(profile.get("last_collected_at"), errors="coerce")
    price_date = pd.to_datetime((latest_price or {}).get("date"), errors="coerce")
    if market_cap is None or market_cap <= 0 or pd.isna(profile_date) or pd.isna(price_date):
        return _valuation_block("COMPONENT_MISSING")
    if abs((pd.Timestamp(profile_date).normalize() - pd.Timestamp(price_date).normalize()).days) > 7:
        return _valuation_block("INPUT_STALE")
    currency_values = (
        profile.get("currency"),
        (latest_price or {}).get("currency"),
        series.get("currency") or balance.get("currency"),
    )
    if any(str(value or "").strip().upper() != "USD" for value in currency_values):
        return _valuation_block("UNIT_UNVERIFIED")
    sector_text = " ".join(
        str(profile.get(key) or "").strip().lower() for key in ("sector", "industry")
    )
    if profile.get("valuation_method_supported") is False or any(
        term in sector_text for term in _UNSUPPORTED_VALUATION_SECTOR_TERMS
    ):
        return _valuation_block("SECTOR_METHOD_UNSUPPORTED")

    base = {
        "status": "READY",
        "reason_code": None,
        "market_cap": market_cap,
        "market_cap_basis_date": pd.Timestamp(profile_date).strftime("%Y-%m-%d"),
        "price_basis_date": pd.Timestamp(price_date).strftime("%Y-%m-%d"),
        "statement_basis_date": balance.get("basis_date"),
        "as_of_date": pd.Timestamp(as_of_date).strftime("%Y-%m-%d"),
    }
    ttm_fcf = _number(latest.get("ttm_fcf"))
    if ttm_fcf is not None and ttm_fcf > 0:
        return {
            **base,
            "method": "P_FCF",
            "multiple": market_cap / ttm_fcf,
            "yield_pct": ttm_fcf / market_cap * 100.0,
            "denominator": ttm_fcf,
        }
    ttm_ocf = _number(latest.get("ttm_ocf"))
    if ttm_ocf is not None and ttm_ocf > 0:
        return {
            **base,
            "method": "P_OCF",
            "multiple": market_cap / ttm_ocf,
            "yield_pct": ttm_ocf / market_cap * 100.0,
            "denominator": ttm_ocf,
        }

    required_balance_keys = {"cash", "short_term_investments", "total_debt"}
    if (
        not required_balance_keys.issubset(balance)
        or balance.get("basis_date") is None
        or balance.get("component_alignment") is False
    ):
        return _valuation_block("COMPONENT_MISSING")
    cash = _number(balance.get("cash"))
    investments = _number(balance.get("short_term_investments"))
    debt = _number(balance.get("total_debt"))
    if cash is None or investments is None or debt is None:
        return _valuation_block("COMPONENT_MISSING")
    enterprise_value = market_cap + debt - cash - investments
    if enterprise_value <= 0:
        return _valuation_block("NEGATIVE_OR_ZERO_NUMERATOR")
    ttm_operating_income = _number(latest.get("ttm_operating_income"))
    ttm_da = _number(latest.get("ttm_da"))
    ebitda = (
        ttm_operating_income + ttm_da
        if ttm_operating_income is not None and ttm_da is not None
        else None
    )
    if ebitda is not None and ebitda > 0 and ttm_da is not None and ttm_da > 0:
        return {
            **base,
            "method": "EV_EBITDA",
            "multiple": enterprise_value / ebitda,
            "yield_pct": None,
            "enterprise_value": enterprise_value,
            "denominator": ebitda,
        }
    ttm_gross_profit = _number(latest.get("ttm_gross_profit"))
    if ttm_gross_profit is not None and ttm_gross_profit > 0:
        return {
            **base,
            "method": "EV_GROSS_PROFIT",
            "multiple": enterprise_value / ttm_gross_profit,
            "yield_pct": None,
            "enterprise_value": enterprise_value,
            "denominator": ttm_gross_profit,
        }
    ttm_revenue = _number(latest.get("ttm_revenue"))
    if ttm_revenue is not None and ttm_revenue > 0:
        return {
            **base,
            "method": "EV_SALES",
            "multiple": enterprise_value / ttm_revenue,
            "yield_pct": None,
            "enterprise_value": enterprise_value,
            "denominator": ttm_revenue,
        }
    return _valuation_block("NEGATIVE_OR_ZERO_DENOMINATOR")


def build_turnaround_analysis(
    *,
    statement_rows: Iterable[Mapping[str, Any]],
    price_rows: Iterable[Mapping[str, Any]],
    profile: Mapping[str, Any],
    latest_price: Mapping[str, Any] | None,
    per_status: str,
    as_of_date: str,
) -> dict[str, Any]:
    """Compose the pure selected-company turnaround analysis contract."""
    series = build_turnaround_quarterly_series(
        statement_rows,
        price_rows,
        as_of_date=as_of_date,
    )
    milestones = classify_turnaround_milestones(series, per_status=per_status)
    risks = evaluate_turnaround_risks(series)
    valuation = route_turnaround_valuation(
        series=series,
        profile=profile,
        latest_price=latest_price,
        per_status=per_status,
        as_of_date=as_of_date,
    )
    timeline = list(series.get("timeline") or [])
    latest = dict(timeline[-1]) if timeline else {}
    operating_ready = (
        len(timeline) >= 8
        and latest.get("ttm_revenue") is not None
        and latest.get("ttm_operating_income") is not None
    )
    cash_ready = (
        len(timeline) >= 8
        and latest.get("ttm_ocf") is not None
        and latest.get("ttm_fcf") is not None
    )
    sections = {
        "operating_chart": {
            "status": "READY" if operating_ready else "BLOCKED",
            "reason_code": None if operating_ready else "INSUFFICIENT_QUARTERS",
        },
        "cash_chart": {
            "status": "READY" if cash_ready else "BLOCKED",
            "reason_code": None if cash_ready else "INSUFFICIENT_QUARTERS",
        },
        "risks": {
            "status": "READY" if series.get("current_balance") else "PARTIAL",
        },
        "valuation": {
            "status": "READY" if valuation.get("status") == "READY" else "BLOCKED",
            "reason_code": valuation.get("reason_code"),
        },
    }
    overall_status = (
        "READY"
        if operating_ready and cash_ready and milestones.get("status") == "READY"
        else "PARTIAL"
        if timeline
        else "BLOCKED"
    )
    return {
        "status": overall_status,
        "series": series,
        "milestones": milestones,
        "risks": risks,
        "valuation": valuation,
        "sections": sections,
    }
