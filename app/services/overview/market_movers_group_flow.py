from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any, Literal

from app.services.overview.market_movers_read_model import canonical_sector


INDUSTRY_ALIASES: dict[str, str] = {
    "software - infrastructure": "Software—Infrastructure",
    "semiconductors": "Semiconductors",
}

_NON_EQUITY_QUOTE_TYPES = {"ETF", "ETN", "MUTUALFUND", "FUND", "INDEX"}


def _number(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number


def _row_value(row: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in row:
            return row.get(key)
    return None


def normalize_industry(value: object) -> str:
    """Return a stable display key without claiming a historical taxonomy."""

    text = " ".join(str(value or "").split())
    if not text or text.casefold() == "unknown":
        return "Unknown"
    lookup = re.sub(r"\s*[-–—]\s*", " - ", text.casefold())
    if lookup in INDUSTRY_ALIASES:
        return INDUSTRY_ALIASES[lookup]
    if text.isupper() or text.islower():
        return text.title()
    return text


def _group_name(row: Mapping[str, Any], group_by: Literal["sector", "industry"]) -> str:
    value = row.get(group_by)
    return canonical_sector(value) if group_by == "sector" else normalize_industry(value)


def _is_equity_issuer(row: Mapping[str, Any]) -> tuple[bool, bool]:
    kind = str(row.get("asset_kind") or "").strip().lower()
    quote_type = str(row.get("quote_type") or "").strip().upper()
    if kind:
        return kind == "stock" and quote_type not in _NON_EQUITY_QUOTE_TYPES, False
    if quote_type in _NON_EQUITY_QUOTE_TYPES:
        return False, False
    return True, True


def build_market_cap_bellwethers(
    rows: Sequence[Mapping[str, Any]],
    *,
    group_by: Literal["sector", "industry"],
    top_n: int = 3,
) -> dict[str, dict[str, Any]]:
    """Rank equity issuers by current market cap, independently of return rank."""

    if group_by not in {"sector", "industry"}:
        raise ValueError(f"Unsupported group_by: {group_by!r}")
    grouped: dict[str, list[dict[str, Any]]] = {}
    non_equity_counts: dict[str, int] = {}
    assumed_counts: dict[str, int] = {}
    for source in rows:
        row = dict(source)
        group = _group_name(row, group_by)
        eligible, assumed = _is_equity_issuer(row)
        if not eligible:
            non_equity_counts[group] = non_equity_counts.get(group, 0) + 1
            continue
        if assumed:
            assumed_counts[group] = assumed_counts.get(group, 0) + 1
        grouped.setdefault(group, []).append(row)

    result: dict[str, dict[str, Any]] = {}
    for group in sorted(grouped):
        candidates = grouped[group]
        valid = [
            row
            for row in candidates
            if (_number(row.get("market_cap")) or 0.0) > 0
        ]
        valid.sort(
            key=lambda row: (
                -float(_number(row.get("market_cap")) or 0.0),
                str(row.get("symbol") or ""),
            )
        )
        denominator = sum(float(_number(row.get("market_cap")) or 0.0) for row in valid)
        group_return = (
            sum(
                float(_number(row.get("market_cap")) or 0.0)
                * float(_number(row.get("return_pct")) or 0.0)
                for row in valid
            )
            / denominator
            if denominator > 0
            else None
        )
        leader_rows: list[dict[str, Any]] = []
        for rank, row in enumerate(valid[: max(1, int(top_n))], start=1):
            return_pct = _number(row.get("return_pct"))
            leader_rows.append(
                {
                    "rank": rank,
                    "symbol": str(row.get("symbol") or "").strip().upper(),
                    "name": row.get("name") or row.get("long_name") or "-",
                    "market_cap": _number(row.get("market_cap")),
                    "return_pct": return_pct,
                    "relative_to_group_pp": round(return_pct - group_return, 2)
                    if return_pct is not None and group_return is not None
                    else None,
                }
            )
        result[group] = {
            "eligible_count": len(candidates),
            "market_cap_valid_count": len(valid),
            "market_cap_excluded_count": len(candidates) - len(valid),
            "non_equity_excluded_count": non_equity_counts.get(group, 0),
            "kind_assumed_count": assumed_counts.get(group, 0),
            "rows": leader_rows,
        }
    return result


def build_group_flow_state(
    *,
    current_rows: Sequence[Mapping[str, Any]],
    previous_rows: Sequence[Mapping[str, Any]],
    market_return_pct: float | None,
    group_by: Literal["sector", "industry"],
) -> list[dict[str, Any]]:
    """Describe current breadth/relative-strength evidence without forecasting."""

    if group_by not in {"sector", "industry"}:
        raise ValueError(f"Unsupported group_by: {group_by!r}")
    previous_by_group = {
        str(_row_value(row, "group", "Group") or "Unknown"): row
        for row in previous_rows
    }
    output: list[dict[str, Any]] = []
    for current in current_rows:
        group = str(_row_value(current, "group", "Group") or "Unknown")
        previous = previous_by_group.get(group, {})
        symbols = int(_number(_row_value(current, "symbols", "Symbols")) or 0)
        breadth = _number(
            _row_value(current, "positive_symbol_share", "Positive Symbol Share %")
        )
        equal_return = _number(
            _row_value(current, "equal_weight_return", "Equal Weight Return %")
        )
        cap_return = _number(
            _row_value(current, "market_cap_weighted_return", "Market Cap Weighted Return %")
        )
        previous_breadth = _number(
            _row_value(previous, "positive_symbol_share", "Positive Symbol Share %")
        )
        previous_cap = _number(
            _row_value(previous, "market_cap_weighted_return", "Market Cap Weighted Return %")
        )
        breadth_change = (
            round(breadth - previous_breadth, 2)
            if breadth is not None and previous_breadth is not None
            else None
        )
        relative_strength = (
            round(cap_return - float(market_return_pct), 2)
            if cap_return is not None and market_return_pct is not None
            else None
        )

        if symbols < 5:
            state = "SPARSE"
            next_observation = "구성 종목 수가 5개 이상인지 확인"
        elif (
            breadth is not None
            and breadth >= 50
            and breadth_change is not None
            and breadth_change > 0
            and relative_strength is not None
            and relative_strength > 0
        ):
            state = "BROADENING_STRENGTH"
            next_observation = "상승 종목 비중과 시장 대비 강도 유지 여부 확인"
        elif (
            cap_return is not None
            and cap_return > 0
            and equal_return is not None
            and equal_return <= 0
            and breadth is not None
            and breadth < 50
        ):
            state = "NARROW_CAP_LED"
            next_observation = "동일가중 수익률과 상승 종목 비중의 확산 여부 확인"
        elif (
            breadth_change is not None
            and breadth_change < 0
            and relative_strength is not None
            and relative_strength <= 0
        ):
            state = "WEAKENING"
            next_observation = "breadth 하락 중단과 상대강도 회복 여부 확인"
        elif (
            cap_return is not None
            and previous_cap is not None
            and cap_return * previous_cap < 0
        ):
            state = "REVERSAL_WATCH"
            next_observation = "수익률 방향 전환이 다음 기간에도 유지되는지 확인"
        else:
            state = "MIXED"
            next_observation = "breadth와 상대강도가 같은 방향으로 정렬되는지 확인"

        output.append(
            {
                "group": group,
                "group_type": group_by,
                "symbols": symbols,
                "state": state,
                "positive_symbol_share_pct": breadth,
                "breadth_change_pp": breadth_change,
                "equal_weight_return_pct": equal_return,
                "market_cap_weighted_return_pct": cap_return,
                "relative_strength_pp": relative_strength,
                "cap_vs_equal_gap_pp": round(cap_return - equal_return, 2)
                if cap_return is not None and equal_return is not None
                else None,
                "next_observation": next_observation,
            }
        )
    return output
