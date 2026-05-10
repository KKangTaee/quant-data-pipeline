from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import pandas as pd
import streamlit as st

from app.web.runtime import (
    FINAL_SELECTION_DECISION_V2_SCHEMA_VERSION,
    PORTFOLIO_SELECTION_SOURCE_SCHEMA_VERSION,
    PRACTICAL_VALIDATION_RESULT_SCHEMA_VERSION,
    append_portfolio_selection_source,
    append_practical_validation_result,
    load_backtest_run_history,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STRESS_WINDOW_FILE = PROJECT_ROOT / ".note" / "finance" / "research" / "practical_validation_stress_windows_v1.json"

VALIDATION_PROFILE_OPTIONS = {
    "conservative_defensive": {
        "label": "방어형",
        "description": "손실 방어와 안정성 우선",
        "rolling_window_months": 24,
        "equity_exposure_review": 70.0,
        "max_weight_review": 60.0,
        "mdd_review_line": -15.0,
        "cost_interpretation": "엄격",
    },
    "balanced_core": {
        "label": "균형형",
        "description": "수익과 위험 균형",
        "rolling_window_months": 36,
        "equity_exposure_review": 85.0,
        "max_weight_review": 75.0,
        "mdd_review_line": -25.0,
        "cost_interpretation": "보통",
    },
    "growth_aggressive": {
        "label": "성장형",
        "description": "성장과 upside 우선",
        "rolling_window_months": 60,
        "equity_exposure_review": 95.0,
        "max_weight_review": 90.0,
        "mdd_review_line": -35.0,
        "cost_interpretation": "보통",
    },
    "hedged_tactical": {
        "label": "전술 / 헤지형",
        "description": "hedge 또는 tactical exposure 확인",
        "rolling_window_months": 24,
        "equity_exposure_review": 85.0,
        "max_weight_review": 70.0,
        "mdd_review_line": -25.0,
        "cost_interpretation": "turnover / slippage 엄격",
    },
    "custom": {
        "label": "사용자 지정",
        "description": "질문 답변 기반 사용자 기준",
        "rolling_window_months": 36,
        "equity_exposure_review": 85.0,
        "max_weight_review": 75.0,
        "mdd_review_line": -25.0,
        "cost_interpretation": "사용자 지정",
    },
}

VALIDATION_PROFILE_QUESTIONS = {
    "primary_goal": {
        "label": "이 포트폴리오를 어떤 목적으로 검증할까요?",
        "options": {
            "balanced": "수익과 위험의 균형",
            "defensive": "손실 방어 중심",
            "growth": "성장 중심",
            "aggressive": "공격적 수익 추구",
            "hedged_tactical": "헤지 또는 전술적 대응",
        },
        "default": "balanced",
    },
    "drawdown_tolerance": {
        "label": "어느 정도의 손실까지 감내할 수 있나요?",
        "options": {
            "dd_20": "-20% 내외",
            "dd_10": "-10% 내외",
            "dd_35": "-35% 내외",
            "dd_above_35": "그 이상도 가능",
        },
        "default": "dd_20",
    },
    "holding_period": {
        "label": "이 포트폴리오를 어느 기간 동안 운용할 생각인가요?",
        "options": {
            "1_to_3y": "1~3년",
            "6_to_12m": "6~12개월",
            "gt_3y": "3년 이상",
            "lt_3m": "3개월 미만",
        },
        "default": "1_to_3y",
    },
    "complexity_allowance": {
        "label": "어떤 상품과 운용 복잡도까지 허용하나요?",
        "options": {
            "sector_theme_allowed": "섹터·테마 ETF까지 허용",
            "broad_etf_only": "광범위 ETF만",
            "inverse_leverage_limited": "인버스·레버리지 ETF를 제한적으로 허용",
            "tactical_high_turnover_allowed": "높은 회전율·전술 리밸런싱도 허용",
        },
        "default": "sector_theme_allowed",
    },
    "alternative_success_metric": {
        "label": "단순 대안보다 무엇이 더 좋아야 하나요?",
        "options": {
            "better_risk_adjusted": "Sharpe·안정성이 좋아야 함",
            "lower_mdd": "손실이 더 작아야 함",
            "higher_return": "수익률이 더 높아야 함",
            "better_downside_defense": "하락장에서 더 잘 버텨야 함",
            "target_exposure": "특정 자산·섹터·테마 노출이 목적임",
        },
        "default": "better_risk_adjusted",
    },
}

PRIMARY_TICKER_BUCKETS = {
    "SPY": "equity",
    "VOO": "equity",
    "VTI": "equity",
    "IVV": "equity",
    "QQQ": "equity",
    "DIA": "equity",
    "IWM": "equity",
    "VEA": "equity",
    "EFA": "equity",
    "EEM": "equity",
    "VWO": "equity",
    "TLT": "bond",
    "IEF": "bond",
    "SHY": "bond",
    "BND": "bond",
    "AGG": "bond",
    "LQD": "bond",
    "HYG": "bond",
    "TIP": "bond",
    "BIL": "cash",
    "SHV": "cash",
    "SGOV": "cash",
    "TBIL": "cash",
    "GLD": "gold",
    "IAU": "gold",
    "SGOL": "gold",
    "DBC": "commodity",
    "PDBC": "commodity",
    "USO": "commodity",
}
SECTOR_TICKERS = {
    "XLB",
    "XLC",
    "XLE",
    "XLF",
    "XLI",
    "XLK",
    "XLP",
    "XLRE",
    "XLU",
    "XLV",
    "XLY",
    "SMH",
    "SOXX",
    "IBB",
    "XBI",
    "IYR",
}
LEVERAGED_TICKERS = {"TQQQ", "UPRO", "SPXL", "SSO", "QLD", "TECL", "SOXL", "TMF"}
INVERSE_TICKERS = {"SH", "PSQ", "SDS", "QID", "SQQQ", "SPXU", "TZA", "DOG", "DXD"}
TOKEN_PATTERN = re.compile(r"\b[A-Z]{2,6}\b")


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(numeric):
        return None
    return numeric


def _slug(value: Any, default: str = "source") -> str:
    raw = str(value or default).strip().lower()
    cleaned = "".join(char if char.isalnum() else "_" for char in raw)
    return "_".join(part for part in cleaned.split("_") if part) or default


def _now_text() -> str:
    return datetime.now().isoformat(timespec="seconds")


def build_validation_profile(profile_id: str | None, answers: dict[str, Any] | None = None) -> dict[str, Any]:
    """Resolve user-facing profile answers into thresholds used by Practical Diagnostics."""
    profile_key = str(profile_id or "balanced_core")
    if profile_key not in VALIDATION_PROFILE_OPTIONS:
        profile_key = "balanced_core"
    profile_config = dict(VALIDATION_PROFILE_OPTIONS[profile_key])
    normalized_answers = {
        key: str((answers or {}).get(key) or question["default"])
        for key, question in VALIDATION_PROFILE_QUESTIONS.items()
    }
    if normalized_answers.get("drawdown_tolerance") == "dd_10":
        profile_config["mdd_review_line"] = -10.0
    elif normalized_answers.get("drawdown_tolerance") == "dd_35":
        profile_config["mdd_review_line"] = min(float(profile_config["mdd_review_line"]), -35.0)
    elif normalized_answers.get("drawdown_tolerance") == "dd_above_35":
        profile_config["mdd_review_line"] = -45.0
    if normalized_answers.get("holding_period") == "lt_3m":
        profile_config["rolling_window_months"] = min(int(profile_config["rolling_window_months"]), 12)
    elif normalized_answers.get("holding_period") == "gt_3y" and profile_key == "growth_aggressive":
        profile_config["rolling_window_months"] = max(int(profile_config["rolling_window_months"]), 60)
    return {
        "profile_id": profile_key,
        "profile_label": profile_config["label"],
        "profile_description": profile_config["description"],
        "answers": normalized_answers,
        "answer_labels": {
            key: VALIDATION_PROFILE_QUESTIONS[key]["options"].get(value, value)
            for key, value in normalized_answers.items()
        },
        "thresholds": {
            "rolling_window_months": int(profile_config["rolling_window_months"]),
            "rolling_step_months": 1,
            "equity_exposure_review": float(profile_config["equity_exposure_review"]),
            "max_weight_review": float(profile_config["max_weight_review"]),
            "mdd_review_line": float(profile_config["mdd_review_line"]),
            "one_way_cost_bps": 10,
            "cost_interpretation": profile_config["cost_interpretation"],
        },
        "invariant_blockers": [
            "Data Trust hard blocker",
            "active weight 합계 오류",
            "핵심 가격 부재",
            "거래 불가",
            "execution boundary 위반",
            "큰 leveraged / inverse exposure의 목적 부재",
        ],
    }


def _metric_snapshot_from_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "cagr": _optional_float(result.get("cagr")),
        "mdd": _optional_float(result.get("maximum_drawdown") or result.get("mdd")),
        "sharpe": _optional_float(result.get("sharpe_ratio") or result.get("sharpe")),
        "end_balance": _optional_float(result.get("end_balance")),
    }


def build_selection_source_from_candidate_draft(draft: dict[str, Any]) -> dict[str, Any]:
    """Convert a single run / compare draft into the Clean V2 selection-source contract."""
    created_at = _now_text()
    source_kind = str(draft.get("source_kind") or "latest_backtest_run")
    strategy_name = str(draft.get("strategy_name") or draft.get("strategy_key") or "Strategy")
    source_id = f"selection_{_slug(source_kind)}_{_slug(strategy_name)}_{uuid4().hex[:8]}"
    result = dict(draft.get("result_snapshot") or {})
    settings = dict(draft.get("settings_snapshot") or {})
    data_trust = dict(draft.get("data_trust_snapshot") or {})
    real_money = dict(draft.get("real_money_signal") or {})
    return {
        "schema_version": PORTFOLIO_SELECTION_SOURCE_SCHEMA_VERSION,
        "selection_source_id": source_id,
        "created_at": created_at,
        "updated_at": created_at,
        "source_kind": source_kind,
        "source_title": strategy_name,
        "source_status": "selected_for_practical_validation",
        "period": {
            "start": result.get("start_date"),
            "end": result.get("end_date"),
            "actual_start": result.get("start_date") or data_trust.get("actual_result_start"),
            "actual_end": result.get("end_date") or data_trust.get("actual_result_end"),
        },
        "summary": _metric_snapshot_from_result(result),
        "data_trust": {
            "status": data_trust.get("price_freshness_status") or "snapshot",
            "requested_end": data_trust.get("requested_end"),
            "actual_result_start": data_trust.get("actual_result_start"),
            "actual_result_end": data_trust.get("actual_result_end"),
            "result_rows": data_trust.get("result_rows"),
            "warning_count": data_trust.get("warning_count"),
            "excluded_tickers": list(data_trust.get("excluded_tickers") or []),
        },
        "real_money_signal": real_money,
        "components": [
            {
                "component_id": f"{source_id}_component_1",
                "registry_id": draft.get("registry_id"),
                "title": strategy_name,
                "strategy_family": draft.get("strategy_key") or source_kind,
                "strategy_key": draft.get("strategy_key"),
                "strategy_name": strategy_name,
                "target_weight": 100.0,
                "benchmark": settings.get("benchmark_ticker") or "-",
                "universe": settings.get("tickers") or [],
                "baseline_cagr": _optional_float(result.get("cagr")),
                "baseline_mdd": _optional_float(result.get("maximum_drawdown")),
                "baseline_sharpe": _optional_float(result.get("sharpe_ratio")),
                "data_trust_status": data_trust.get("price_freshness_status") or "snapshot",
                "promotion": real_money.get("promotion"),
                "deployment": real_money.get("deployment"),
                "period_start": result.get("start_date"),
                "period_end": result.get("end_date"),
                "replay_contract": {
                    "settings_snapshot": settings,
                    "source_kind": source_kind,
                },
            }
        ],
        "construction": {
            "source": "single_strategy" if source_kind != "compare_focused_strategy" else "compare_focused_strategy",
            "target_weight_total": 100.0,
            "rebalance_cadence": settings.get("rebalance_freq") or settings.get("factor_freq"),
        },
        "source_snapshot": draft,
        "notes": "Clean V2 selection source. It is not a live approval or an investment recommendation.",
    }


def build_selection_source_from_saved_mix_prefill(prefill: dict[str, Any]) -> dict[str, Any]:
    """Convert a weighted mix prefill into the Clean V2 selection-source contract."""
    created_at = _now_text()
    source_kind = str(prefill.get("source_kind") or "saved_portfolio_mix")
    source_ref_id = str(
        prefill.get("saved_portfolio_id")
        or prefill.get("weighted_portfolio_id")
        or prefill.get("portfolio_id")
        or source_kind
    )
    source_name = str(
        prefill.get("saved_portfolio_name")
        or prefill.get("weighted_portfolio_name")
        or prefill.get("portfolio_name")
        or source_ref_id
    )
    construction_source = "weighted_mix" if source_kind == "weighted_portfolio_mix" else "saved_mix"
    source_id = f"selection_{_slug(source_kind)}_{_slug(source_ref_id)}_{uuid4().hex[:8]}"
    weighted_summary = dict(prefill.get("weighted_summary") or {})
    weighted_period = dict(prefill.get("weighted_period") or {})
    components: list[dict[str, Any]] = []
    for idx, raw_component in enumerate(list(prefill.get("components") or [])):
        component = dict(raw_component or {})
        component_id = str(component.get("registry_id") or f"{source_id}_component_{idx + 1}")
        components.append(
            {
                "component_id": component_id,
                "registry_id": component.get("registry_id"),
                "title": component.get("title") or component.get("strategy_name") or component_id,
                "strategy_family": component.get("strategy_family"),
                "strategy_key": component.get("strategy_key") or component.get("strategy_family"),
                "strategy_name": component.get("strategy_name"),
                "proposal_role": component.get("proposal_role"),
                "target_weight": _optional_float(component.get("target_weight")) or 0.0,
                "benchmark": component.get("benchmark") or "-",
                "universe": component.get("universe") or [],
                "baseline_cagr": _optional_float(component.get("cagr")),
                "baseline_mdd": _optional_float(component.get("mdd")),
                "data_trust_status": component.get("data_trust_status") or "snapshot",
                "promotion": component.get("promotion"),
                "deployment": component.get("deployment"),
                "period_start": dict(component.get("period") or {}).get("start"),
                "period_end": dict(component.get("period") or {}).get("end"),
                "replay_contract": {
                    "contract": dict(component.get("contract") or {}),
                    "compare_evidence": dict(component.get("compare_evidence") or {}),
                    "source_kind": source_kind,
                    "source_ref_id": source_ref_id,
                },
            }
        )
    target_weight_total = round(
        sum((_optional_float(component.get("target_weight")) or 0.0) for component in components),
        4,
    )
    return {
        "schema_version": PORTFOLIO_SELECTION_SOURCE_SCHEMA_VERSION,
        "selection_source_id": source_id,
        "created_at": created_at,
        "updated_at": created_at,
        "source_kind": source_kind,
        "source_title": source_name,
        "source_status": "selected_for_practical_validation",
        "period": {
            "start": weighted_period.get("start"),
            "end": weighted_period.get("end"),
            "actual_start": weighted_period.get("start"),
            "actual_end": weighted_period.get("end"),
        },
        "summary": {
            "cagr": _optional_float(weighted_summary.get("cagr")),
            "mdd": _optional_float(weighted_summary.get("mdd")),
            "sharpe": _optional_float(weighted_summary.get("sharpe_ratio") or weighted_summary.get("sharpe")),
            "end_balance": _optional_float(weighted_summary.get("end_balance")),
        },
        "data_trust": {
            "status": prefill.get("data_trust_status") or f"{construction_source}_snapshot",
            "warning_count": 0,
        },
        "real_money_signal": {
            "route": f"{construction_source}_component_snapshot",
            "blockers": [],
            "review_gaps": [],
        },
        "components": components,
        "construction": {
            "source": construction_source,
            "source_ref_id": source_ref_id,
            "saved_portfolio_id": prefill.get("saved_portfolio_id"),
            "weighted_portfolio_id": prefill.get("weighted_portfolio_id"),
            "target_weight_total": target_weight_total,
            "date_policy": dict(prefill.get("portfolio_context") or {}).get("date_policy"),
        },
        "source_snapshot": prefill,
        "notes": "Clean V2 weighted mix selection source. It is not a live approval or an investment recommendation.",
    }


def build_selection_source_from_weighted_mix_prefill(prefill: dict[str, Any]) -> dict[str, Any]:
    """Convert the just-built weighted portfolio mix into a Practical Validation source."""
    row = dict(prefill or {})
    row.setdefault("source_kind", "weighted_portfolio_mix")
    return build_selection_source_from_saved_mix_prefill(row)


def queue_practical_validation_source(source: dict[str, Any], *, persist: bool = True) -> None:
    """Send a selected source into the Practical Validation stage and optionally persist it."""
    source_row = dict(source or {})
    if persist:
        append_portfolio_selection_source(source_row)
    st.session_state.backtest_practical_validation_source = source_row
    st.session_state.backtest_practical_validation_notice = (
        f"`{source_row.get('source_title') or source_row.get('selection_source_id')}`를 Practical Validation으로 보냈습니다. "
        "이 기록은 후보 검증 자료이며 live approval이나 주문 지시가 아닙니다."
    )
    st.session_state.backtest_practical_validation_mode = "Selected Source"
    st.session_state.backtest_requested_panel = "Practical Validation"


def _component_title(component: dict[str, Any]) -> str:
    return str(component.get("title") or component.get("strategy_name") or component.get("component_id") or "-")


def _component_weight(component: dict[str, Any]) -> float:
    return _optional_float(component.get("target_weight")) or 0.0


def _extract_ticker_tokens(value: Any) -> list[str]:
    tokens: list[str] = []
    if isinstance(value, (list, tuple, set)):
        raw_values = [str(item or "") for item in value]
    else:
        raw_values = [str(value or "")]
    for raw in raw_values:
        for token in TOKEN_PATTERN.findall(raw.upper()):
            if token in PRIMARY_TICKER_BUCKETS or token in SECTOR_TICKERS or token in LEVERAGED_TICKERS or token in INVERSE_TICKERS:
                tokens.append(token)
    return sorted(set(tokens))


def _component_tickers(component: dict[str, Any]) -> list[str]:
    tokens: list[str] = []
    for field in ("universe", "benchmark", "title", "strategy_name", "strategy_family", "strategy_key"):
        tokens.extend(_extract_ticker_tokens(component.get(field)))
    return sorted(set(tokens))


def _component_primary_buckets(component: dict[str, Any]) -> tuple[list[str], list[str]]:
    tickers = _component_tickers(component)
    buckets: list[str] = []
    flags: list[str] = []
    for ticker in tickers:
        if ticker in LEVERAGED_TICKERS:
            flags.append("leveraged")
            buckets.append("equity")
        elif ticker in INVERSE_TICKERS:
            flags.append("inverse")
            buckets.append("equity")
        elif ticker in SECTOR_TICKERS:
            flags.append("sector_theme")
            buckets.append("equity")
        else:
            bucket = PRIMARY_TICKER_BUCKETS.get(ticker)
            if bucket:
                buckets.append(bucket)
    text = " ".join(str(component.get(key) or "") for key in ("title", "strategy_family", "strategy_key")).lower()
    if not buckets:
        if any(term in text for term in ("sector", "growth", "equal", "relative", "spy", "qqq")):
            buckets.append("equity")
        elif any(term in text for term in ("gold", "commodity")):
            buckets.append("gold")
        elif any(term in text for term in ("bond", "treasury", "cash")):
            buckets.append("bond")
        elif "gtaa" in text:
            buckets.append("multi_asset")
    return sorted(set(buckets)), sorted(set(flags))


def _build_exposure_summary(active_components: list[dict[str, Any]]) -> dict[str, Any]:
    asset_exposure = {
        "equity": 0.0,
        "bond": 0.0,
        "cash": 0.0,
        "gold": 0.0,
        "commodity": 0.0,
        "multi_asset": 0.0,
        "unknown": 0.0,
    }
    flag_exposure = {"sector_theme": 0.0, "leveraged": 0.0, "inverse": 0.0}
    component_rows: list[dict[str, Any]] = []
    for component in active_components:
        weight = _component_weight(component)
        buckets, flags = _component_primary_buckets(component)
        if not buckets:
            buckets = ["unknown"]
        bucket_weight = weight / len(buckets) if buckets else weight
        for bucket in buckets:
            asset_exposure[bucket] = asset_exposure.get(bucket, 0.0) + bucket_weight
        for flag in flags:
            flag_exposure[flag] = flag_exposure.get(flag, 0.0) + weight
        component_rows.append(
            {
                "Component": _component_title(component),
                "Weight": weight,
                "Tickers": ", ".join(_component_tickers(component)) or "-",
                "Primary Buckets": ", ".join(buckets),
                "Flags": ", ".join(flags) or "-",
            }
        )
    known_weight = sum(value for bucket, value in asset_exposure.items() if bucket != "unknown")
    return {
        "asset_exposure": {key: round(value, 4) for key, value in asset_exposure.items()},
        "flag_exposure": {key: round(value, 4) for key, value in flag_exposure.items()},
        "known_weight": round(known_weight, 4),
        "unknown_weight": round(asset_exposure.get("unknown", 0.0), 4),
        "component_rows": component_rows,
    }


def _domain_result(
    *,
    domain: str,
    title: str,
    status: str,
    summary: str,
    origin: str,
    key_metric: Any = "-",
    metrics: dict[str, Any] | None = None,
    evidence_rows: list[dict[str, Any]] | None = None,
    limitations: list[str] | None = None,
    next_action: str = "",
    profile_effect: str = "",
) -> dict[str, Any]:
    return {
        "domain": domain,
        "title": title,
        "status": status,
        "origin": origin,
        "key_metric": key_metric,
        "summary": summary,
        "metrics": dict(metrics or {}),
        "evidence_rows": list(evidence_rows or []),
        "limitations": list(limitations or []),
        "next_action": next_action,
        "profile_effect": profile_effect,
    }


def _diagnostic_display_rows(diagnostics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "Domain": item.get("title"),
            "Status": item.get("status"),
            "Key Metric": item.get("key_metric"),
            "Reason": item.get("summary"),
            "Origin": item.get("origin"),
            "Profile Effect": item.get("profile_effect") or "-",
            "Next Action": item.get("next_action") or "-",
        }
        for item in diagnostics
    ]


def _status_counts(diagnostics: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"PASS": 0, "REVIEW": 0, "BLOCKED": 0, "NOT_RUN": 0}
    for item in diagnostics:
        status = str(item.get("status") or "NOT_RUN")
        counts[status] = counts.get(status, 0) + 1
    return counts


def _diagnostic_score(diagnostics: list[dict[str, Any]], hard_blockers: list[str]) -> float:
    if hard_blockers:
        return 0.0
    weights = {"PASS": 1.0, "REVIEW": 0.65, "NOT_RUN": 0.35, "BLOCKED": 0.0}
    if not diagnostics:
        return 0.0
    score = sum(weights.get(str(item.get("status") or "NOT_RUN"), 0.35) for item in diagnostics)
    return round(score / len(diagnostics) * 10.0, 1)


def _parse_date(value: Any) -> pd.Timestamp | None:
    if value in (None, ""):
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed


def _load_static_stress_windows() -> list[dict[str, Any]]:
    if not STRESS_WINDOW_FILE.exists():
        return []
    try:
        payload = json.loads(STRESS_WINDOW_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [dict(row or {}) for row in list(payload.get("windows") or []) if isinstance(row, dict)]


def _stress_window_rows(source_period: dict[str, Any]) -> list[dict[str, Any]]:
    actual_start = _parse_date(source_period.get("actual_start") or source_period.get("start"))
    actual_end = _parse_date(source_period.get("actual_end") or source_period.get("end"))
    rows: list[dict[str, Any]] = []
    for window in _load_static_stress_windows():
        start = _parse_date(window.get("start"))
        end = _parse_date(window.get("end"))
        if actual_start is None or actual_end is None or start is None or end is None:
            coverage = "UNKNOWN"
            result_status = "NOT_RUN"
        elif actual_end < start or actual_start > end:
            coverage = "NOT_COVERED"
            result_status = "NOT_RUN"
        else:
            coverage = "COVERED"
            result_status = "NOT_RUN"
        rows.append(
            {
                "Scenario": window.get("label") or window.get("id"),
                "Window": f"{window.get('start')} -> {window.get('end')}",
                "Category": window.get("category"),
                "Coverage": coverage,
                "Result Status": result_status,
                "Expected Check": "return / MDD / benchmark spread",
                "Judgment": "curve replay 필요" if coverage == "COVERED" else "기간 미포함",
                "Decision Use": "Stress / scenario evidence",
            }
        )
    return rows


def _build_overfit_audit(source_row: dict[str, Any], active_components: list[dict[str, Any]]) -> dict[str, Any]:
    strategy_keys = {
        str(component.get("strategy_key") or component.get("strategy_family") or "").strip()
        for component in active_components
        if str(component.get("strategy_key") or component.get("strategy_family") or "").strip()
    }
    source_title = str(source_row.get("source_title") or "").lower()
    try:
        history_rows = load_backtest_run_history(limit=500)
    except Exception:
        history_rows = []
    matched: list[dict[str, Any]] = []
    for row in history_rows:
        strategy_key = str(row.get("strategy_key") or "").strip()
        selected_strategies = {
            str(item or "").strip()
            for item in list(dict(row.get("context") or {}).get("selected_strategies") or [])
            if str(item or "").strip()
        }
        title_match = source_title and source_title in str(row.get("strategy_name") or row.get("preset_name") or "").lower()
        if strategy_key in strategy_keys or strategy_keys.intersection(selected_strategies) or title_match:
            matched.append(row)
    if not matched:
        return {
            "audit_source": "local_run_history_summary",
            "status": "NOT_RUN",
            "trial_count": 0,
            "interpretation": "관련 run_history 자동 매칭이 없어 선택 과정 audit을 실행하지 못했습니다.",
        }
    period_variants = {
        (str(row.get("input_start") or ""), str(row.get("input_end") or ""))
        for row in matched
    }
    weight_variants = {
        json.dumps(dict(row.get("context") or {}).get("weights_percent") or {}, sort_keys=True, default=str)
        for row in matched
        if dict(row.get("context") or {}).get("weights_percent")
    }
    strategy_variants = {
        str(row.get("strategy_key") or tuple(dict(row.get("context") or {}).get("selected_strategies") or []))
        for row in matched
    }
    trial_count = len(matched)
    status = "REVIEW" if trial_count > 30 else "PASS"
    return {
        "audit_source": "local_run_history_summary",
        "status": status,
        "trial_count": trial_count,
        "unique_strategy_variants": len(strategy_variants),
        "unique_weight_variants": len(weight_variants),
        "unique_period_variants": len(period_variants),
        "run_history_window": "latest_500_local_rows",
        "interpretation": "관련 실험 횟수가 많아 sensitivity 검증을 강화해야 합니다."
        if status == "REVIEW"
        else "관련 local trial count가 과도하게 높지는 않습니다.",
    }


def _baseline_rows() -> list[dict[str, Any]]:
    return [
        {"Baseline": "SPY", "Purpose": "미국 대형주 broad equity 단순 대안", "Priority": "MVP", "Result Status": "NOT_RUN"},
        {"Baseline": "QQQ", "Purpose": "성장 / Nasdaq 노출 단순 대안", "Priority": "MVP", "Result Status": "NOT_RUN"},
        {"Baseline": "60/40 proxy", "Purpose": "주식 + 채권 균형 대안", "Priority": "MVP", "Result Status": "NOT_RUN"},
        {"Baseline": "cash-aware baseline", "Purpose": "현금 또는 단기채를 섞은 방어형 대안", "Priority": "MVP", "Result Status": "NOT_RUN"},
        {"Baseline": "All Weather-like proxy", "Purpose": "regime 분산형 대리 비교군", "Priority": "Future", "Result Status": "NOT_RUN"},
    ]


def _sensitivity_rows(active_components: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = [
        {"Scenario": "Window perturbation", "Scope": "start/end, recent 3y/5y", "Result Status": "NOT_RUN", "Expected Check": "CAGR / MDD / Sharpe dispersion"},
    ]
    if len(active_components) > 1:
        rows.extend(
            [
                {"Scenario": "Mix weight +/- 5%p", "Scope": "component weights", "Result Status": "NOT_RUN", "Expected Check": "60:40 등 특정 비중 의존성"},
                {"Scenario": "Drop-one component", "Scope": "remove one component and renormalize", "Result Status": "NOT_RUN", "Expected Check": "특정 component 의존성"},
            ]
        )
    strategy_keys = {str(component.get("strategy_key") or component.get("strategy_family") or "").lower() for component in active_components}
    if any("gtaa" in key for key in strategy_keys):
        rows.append({"Scenario": "GTAA parameter perturbation", "Scope": "interval / MA window / rebalance day", "Result Status": "NOT_RUN", "Expected Check": "cadence 민감도"})
    if any("equal" in key for key in strategy_keys):
        rows.append({"Scenario": "Equal Weight perturbation", "Scope": "rebalance frequency / ticker subset", "Result Status": "NOT_RUN", "Expected Check": "ticker set 민감도"})
    if any("relative" in key or "grs" in key for key in strategy_keys):
        rows.append({"Scenario": "Relative Strength perturbation", "Scope": "lookback / top_n / skip period", "Result Status": "NOT_RUN", "Expected Check": "momentum window 민감도"})
    return rows


def build_practical_validation_result(
    source: dict[str, Any],
    validation_profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the structured Practical Validation result used by Final Review V2."""
    now = _now_text()
    source_row = dict(source or {})
    profile_row = build_validation_profile(
        str((validation_profile or {}).get("profile_id") or "balanced_core"),
        dict((validation_profile or {}).get("answers") or {}),
    )
    thresholds = dict(profile_row.get("thresholds") or {})
    answers = dict(profile_row.get("answers") or {})
    source_id = str(source_row.get("selection_source_id") or "").strip()
    components = [dict(item or {}) for item in list(source_row.get("components") or [])]
    active_components = [
        component
        for component in components
        if (_optional_float(component.get("target_weight")) or 0.0) > 0.0
    ]
    target_weight_total = round(
        sum((_optional_float(component.get("target_weight")) or 0.0) for component in active_components),
        4,
    )
    data_trust = dict(source_row.get("data_trust") or {})
    real_money = dict(source_row.get("real_money_signal") or {})
    hard_blockers: list[str] = []
    review_gaps: list[str] = []
    source_period = dict(source_row.get("period") or {})
    source_summary = dict(source_row.get("summary") or {})
    source_title = source_row.get("source_title") or source_id

    if not source_id:
        hard_blockers.append("selection_source_id 없음")
    if not active_components:
        hard_blockers.append("active component 없음")
    if active_components and abs(target_weight_total - 100.0) > 0.01:
        hard_blockers.append(f"target weight 합계가 100%가 아님: {target_weight_total:.2f}%")
    if str(data_trust.get("status") or "").lower() in {"error", "blocked"}:
        hard_blockers.append(f"Data Trust blocked: {data_trust.get('status')}")
    if real_money.get("deployment") in {"blocked", "deployment_blocked"}:
        hard_blockers.append("Real-Money deployment blocked")

    if data_trust.get("warning_count"):
        review_gaps.append(f"Data Trust warning {data_trust.get('warning_count')}개")
    has_benchmark = any(str(component.get("benchmark") or "").strip() not in {"", "-"} for component in active_components)
    if not has_benchmark:
        review_gaps.append("benchmark snapshot 부족")

    input_checks = [
        {
            "Criteria": "Selection source",
            "Ready": bool(source_id),
            "Current": source_id or "-",
            "Meaning": "Backtest Analysis에서 선택한 Clean V2 source가 있는지 봅니다.",
        },
        {
            "Criteria": "Active components",
            "Ready": bool(active_components),
            "Current": str(len(active_components)),
            "Meaning": "실전 검증할 component가 있는지 봅니다.",
        },
        {
            "Criteria": "Target weight total",
            "Ready": bool(active_components) and abs(target_weight_total - 100.0) <= 0.01,
            "Current": f"{target_weight_total:.2f}%",
            "Meaning": "포트폴리오 비중 합계가 100%인지 봅니다.",
        },
        {
            "Criteria": "Data Trust",
            "Ready": str(data_trust.get("status") or "").lower() not in {"error", "blocked"},
            "Current": data_trust.get("status") or "snapshot",
            "Meaning": "원본 실행 결과의 Data Trust가 차단 상태인지 봅니다.",
        },
        {
            "Criteria": "Execution boundary",
            "Ready": True,
            "Current": "live approval disabled / order instruction disabled",
            "Meaning": "이 검증은 후보 자료이며 주문이나 자동매매가 아닙니다.",
        },
    ]

    exposure_summary = _build_exposure_summary(active_components)
    asset_exposure = dict(exposure_summary.get("asset_exposure") or {})
    flag_exposure = dict(exposure_summary.get("flag_exposure") or {})
    exposure_rows = list(exposure_summary.get("component_rows") or [])
    known_weight = _optional_float(exposure_summary.get("known_weight")) or 0.0
    unknown_weight = _optional_float(exposure_summary.get("unknown_weight")) or 0.0
    equity_exposure = _optional_float(asset_exposure.get("equity")) or 0.0
    max_weight = max([_component_weight(component) for component in active_components], default=0.0)
    repeated_benchmarks = {
        str(component.get("benchmark") or "").strip().upper()
        for component in active_components
        if str(component.get("benchmark") or "").strip() not in {"", "-"}
    }
    duplicate_benchmark_count = max(0, len(active_components) - len(repeated_benchmarks)) if active_components else 0
    complexity_allows_inverse = answers.get("complexity_allowance") in {
        "inverse_leverage_limited",
        "tactical_high_turnover_allowed",
    }
    complexity_restricts_broad = answers.get("complexity_allowance") == "broad_etf_only"

    input_status = "BLOCKED" if hard_blockers else "REVIEW" if review_gaps else "PASS"
    diagnostics: list[dict[str, Any]] = [
        _domain_result(
            domain="input_evidence_layer",
            title="1. Input Evidence Layer",
            status=input_status,
            origin="existing_evidence",
            key_metric=f"{len(active_components)} components / {target_weight_total:.2f}%",
            summary="원본 source, 비중 합계, Data Trust, 실행 경계 조건을 확인했습니다.",
            evidence_rows=input_checks,
            limitations=[] if input_status == "PASS" else hard_blockers + review_gaps,
            next_action="BLOCKED 항목이 있으면 Backtest Analysis에서 source를 다시 구성합니다.",
        )
    ]

    if not active_components:
        allocation_status = "BLOCKED"
        allocation_summary = "검증할 component가 없어 자산배분 적합성을 판단할 수 없습니다."
    elif known_weight <= 0.0:
        allocation_status = "NOT_RUN"
        allocation_summary = "ticker / 자산군 look-through coverage가 없어 proxy 분류를 실행하지 못했습니다."
    elif unknown_weight > 50.0:
        allocation_status = "REVIEW"
        allocation_summary = f"자산군 미분류 비중이 {unknown_weight:.1f}%라 look-through 보강이 필요합니다."
    elif equity_exposure > (_optional_float(thresholds.get("equity_exposure_review")) or 85.0):
        allocation_status = "REVIEW"
        allocation_summary = f"주식성 노출이 {equity_exposure:.1f}%로 {profile_row['profile_label']} 기준보다 높습니다."
    else:
        allocation_status = "PASS"
        allocation_summary = "현재 proxy 기준 자산군 분산은 프로필 기준 안에 있습니다."
    diagnostics.append(
        _domain_result(
            domain="asset_allocation_fit",
            title="2. Asset Allocation Fit",
            status=allocation_status,
            origin="new_diagnostic",
            key_metric=f"equity {equity_exposure:.1f}% / unknown {unknown_weight:.1f}%",
            summary=allocation_summary,
            metrics=exposure_summary,
            evidence_rows=exposure_rows,
            limitations=["holdings look-through 데이터가 없으면 ticker/proxy 분류로만 판단합니다."],
            next_action="미분류 또는 과도한 주식성 노출이 있으면 ETF 구성과 목적을 재확인합니다.",
            profile_effect=f"{profile_row['profile_label']} equity review line {thresholds.get('equity_exposure_review')}%",
        )
    )

    if not active_components:
        concentration_status = "BLOCKED"
        concentration_summary = "검증할 component가 없어 집중도를 판단할 수 없습니다."
    elif max_weight > (_optional_float(thresholds.get("max_weight_review")) or 75.0):
        concentration_status = "REVIEW"
        concentration_summary = f"최대 component 비중이 {max_weight:.1f}%로 프로필 기준을 넘었습니다."
    elif complexity_restricts_broad and (flag_exposure.get("sector_theme", 0.0) or 0.0) > 0.0:
        concentration_status = "REVIEW"
        concentration_summary = "사용자 프로필은 broad ETF를 선호하지만 sector/theme 노출이 있습니다."
    else:
        concentration_status = "PASS"
        concentration_summary = "component 비중 집중도와 proxy exposure가 즉시 차단 수준은 아닙니다."
    diagnostics.append(
        _domain_result(
            domain="concentration_overlap_exposure",
            title="3. Concentration / Overlap / Exposure",
            status=concentration_status,
            origin="new_diagnostic",
            key_metric=f"max component {max_weight:.1f}%",
            summary=concentration_summary,
            metrics={
                "max_component_weight": round(max_weight, 4),
                "duplicate_benchmark_count": duplicate_benchmark_count,
                "flag_exposure": flag_exposure,
            },
            evidence_rows=exposure_rows,
            limitations=["ETF holdings-level overlap은 아직 계산하지 않고 ticker/proxy signal로 먼저 표시합니다."],
            next_action="중복 benchmark 또는 sector/theme 집중이 있으면 단순 대안과 목적을 비교합니다.",
            profile_effect=f"{profile_row['profile_label']} max weight review line {thresholds.get('max_weight_review')}%",
        )
    )

    if len(active_components) <= 1:
        diversification_status = "REVIEW"
        diversification_summary = "단일 component 후보라 component 간 상관 / 위험기여 분산을 확인할 수 없습니다."
    else:
        diversification_status = "NOT_RUN"
        diversification_summary = "component별 수익률 replay matrix가 아직 없어 correlation / risk contribution은 후속 계산이 필요합니다."
    diagnostics.append(
        _domain_result(
            domain="correlation_diversification_risk_contribution",
            title="4. Correlation / Diversification / Risk Contribution",
            status=diversification_status,
            origin="new_diagnostic",
            key_metric=f"{len(active_components)} components",
            summary=diversification_summary,
            evidence_rows=[
                {
                    "Component": _component_title(component),
                    "Weight": _component_weight(component),
                    "Benchmark": component.get("benchmark") or "-",
                    "Replay Contract": "present" if component.get("replay_contract") else "missing",
                }
                for component in active_components
            ],
            limitations=["실제 상관계수와 위험기여도는 component daily/monthly return matrix가 붙은 뒤 계산합니다."],
            next_action="mix 후보라면 component별 return curve replay를 붙여 위험기여도를 계산합니다.",
        )
    )

    diagnostics.append(
        _domain_result(
            domain="regime_macro_suitability",
            title="5. Regime / Macro Suitability",
            status="NOT_RUN",
            origin="future_connector",
            key_metric="macro connector pending",
            summary="금리, 인플레이션, 경기 국면 데이터 connector가 아직 붙지 않아 macro suitability는 기록만 남깁니다.",
            limitations=["FRED 등 macro connector가 붙기 전에는 hard blocker로 사용하지 않습니다."],
            next_action="core Practical Validation 이후 FRED 기반 regime snapshot을 추가합니다.",
        )
    )
    diagnostics.append(
        _domain_result(
            domain="sentiment_risk_on_off_overlay",
            title="6. Sentiment / Risk-On-Off Overlay",
            status="NOT_RUN",
            origin="future_connector",
            key_metric="sentiment connector pending",
            summary="VIX, Fear & Greed, credit spread / yield curve 보조지표는 이번 core 구현 범위에서 제외합니다.",
            limitations=["시장 분위기 지표는 보조지표이며 단독 hard blocker로 쓰지 않습니다."],
            next_action="core 개발 후 FRED 기반 VIX / credit spread / yield curve snapshot부터 붙입니다.",
        )
    )

    stress_rows = _stress_window_rows(source_period)
    covered_stress_count = sum(1 for row in stress_rows if row.get("Coverage") == "COVERED")
    if not stress_rows:
        stress_status = "NOT_RUN"
        stress_summary = "static stress window calendar를 읽지 못했습니다."
    elif covered_stress_count > 0:
        stress_status = "REVIEW"
        stress_summary = f"백테스트 기간에 포함된 stress window {covered_stress_count}개가 있어 구간 replay가 필요합니다."
    else:
        stress_status = "NOT_RUN"
        stress_summary = "현재 source 기간에 포함된 static stress window가 없어 별도 stress 결과가 없습니다."
    diagnostics.append(
        _domain_result(
            domain="stress_scenario_diagnostics",
            title="7. Stress / Scenario Diagnostics",
            status=stress_status,
            origin="new_diagnostic",
            key_metric=f"{covered_stress_count} covered windows",
            summary=stress_summary,
            evidence_rows=stress_rows,
            limitations=["현재 단계는 이벤트 구간 coverage 확인까지이며, 구간별 수익률/MDD replay는 후속 계산입니다."],
            next_action="covered window가 있으면 해당 구간의 후보 대비 benchmark 성과를 계산합니다.",
        )
    )

    alternative_rows = _baseline_rows()
    diagnostics.append(
        _domain_result(
            domain="alternative_portfolio_challenge",
            title="8. Alternative Portfolio Challenge",
            status="NOT_RUN",
            origin="new_diagnostic",
            key_metric="SPY / QQQ / 60-40 / cash-aware pending",
            summary="단순 대안 baseline 목록은 생성했지만 baseline replay 비교는 아직 실행하지 않았습니다.",
            evidence_rows=alternative_rows,
            limitations=["미래 수익 보장이 아니라 단순 대안보다 복잡한 후보를 선택할 근거를 점검하는 용도입니다."],
            next_action="후속 구현에서 baseline curve를 같은 기간으로 replay해 risk-adjusted 비교를 추가합니다.",
            profile_effect=profile_row["answer_labels"].get("alternative_success_metric", "-"),
        )
    )

    leveraged_exposure = (_optional_float(flag_exposure.get("leveraged")) or 0.0) + (
        _optional_float(flag_exposure.get("inverse")) or 0.0
    )
    if leveraged_exposure > 20.0 and not complexity_allows_inverse:
        leveraged_status = "BLOCKED"
        leveraged_summary = f"레버리지/인버스 proxy 노출이 {leveraged_exposure:.1f}%인데 사용자 프로필에서 허용되지 않았습니다."
    elif leveraged_exposure > 0.0:
        leveraged_status = "REVIEW"
        leveraged_summary = f"레버리지/인버스 proxy 노출 {leveraged_exposure:.1f}%는 운용 목적과 기간 확인이 필요합니다."
    else:
        leveraged_status = "PASS"
        leveraged_summary = "레버리지/인버스 ETF proxy 노출이 감지되지 않았습니다."
    diagnostics.append(
        _domain_result(
            domain="leveraged_inverse_etf_suitability",
            title="9. Leveraged / Inverse ETF Suitability",
            status=leveraged_status,
            origin="new_diagnostic",
            key_metric=f"{leveraged_exposure:.1f}%",
            summary=leveraged_summary,
            metrics={"leveraged_inverse_exposure": round(leveraged_exposure, 4), "flag_exposure": flag_exposure},
            evidence_rows=exposure_rows,
            limitations=["레버리지/인버스 적합성은 ticker proxy 기반이며 holding 목적과 rebalancing cadence를 함께 봐야 합니다."],
            next_action="노출이 있으면 Final Review에서 목적, 보유기간, 손실 감내, 재검토 trigger를 명시합니다.",
            profile_effect=profile_row["answer_labels"].get("complexity_allowance", "-"),
        )
    )

    excluded_tickers = list(data_trust.get("excluded_tickers") or [])
    if str(data_trust.get("status") or "").lower() in {"error", "blocked"}:
        operability_status = "BLOCKED"
        operability_summary = "Data Trust가 차단되어 가격/운용 가능성 판단을 진행할 수 없습니다."
    elif excluded_tickers or unknown_weight > 50.0:
        operability_status = "REVIEW"
        operability_summary = "제외 ticker 또는 미분류 비중이 있어 ETF 운용성 확인이 필요합니다."
    else:
        operability_status = "REVIEW"
        operability_summary = "기본 source는 있으나 expense ratio, spread, ADV, turnover coverage는 아직 별도 확인이 필요합니다."
    diagnostics.append(
        _domain_result(
            domain="operability_cost_liquidity",
            title="10. Operability / Cost / Liquidity",
            status=operability_status,
            origin="new_diagnostic",
            key_metric=f"one-way {thresholds.get('one_way_cost_bps')} bps assumption",
            summary=operability_summary,
            metrics={
                "one_way_cost_bps": thresholds.get("one_way_cost_bps"),
                "excluded_tickers": excluded_tickers,
                "cost_interpretation": thresholds.get("cost_interpretation"),
            },
            evidence_rows=[
                {
                    "Item": "Cost assumption",
                    "Current": f"one-way {thresholds.get('one_way_cost_bps')} bps",
                    "Meaning": "거래 수수료, spread, slippage를 포함한 보수적 시작값",
                },
                {
                    "Item": "Excluded tickers",
                    "Current": ", ".join(excluded_tickers) if excluded_tickers else "-",
                    "Meaning": "원본 backtest에서 가격/데이터 문제로 제외된 ticker",
                },
            ],
            limitations=["ETF expense ratio / ADV / spread 데이터 connector는 후속 구현입니다."],
            next_action="Final Review 전에 cost/liquidity connector가 없다는 점을 판단 근거에 남깁니다.",
            profile_effect=str(thresholds.get("cost_interpretation") or "-"),
        )
    )

    overfit_audit = _build_overfit_audit(source_row, active_components)
    sensitivity_rows = _sensitivity_rows(active_components)
    robustness_status = "REVIEW" if overfit_audit.get("status") == "REVIEW" else "NOT_RUN"
    robustness_summary = (
        overfit_audit.get("interpretation")
        if overfit_audit.get("status") == "REVIEW"
        else "sensitivity perturbation 목록은 생성했지만 실제 재계산은 아직 실행하지 않았습니다."
    )
    diagnostics.append(
        _domain_result(
            domain="robustness_sensitivity_overfit",
            title="11. Robustness / Sensitivity / Overfit",
            status=robustness_status,
            origin="new_diagnostic",
            key_metric=f"local trials {overfit_audit.get('trial_count', 0)}",
            summary=str(robustness_summary),
            metrics=overfit_audit,
            evidence_rows=sensitivity_rows,
            limitations=["run_history 원본은 저장하지 않고 local audit summary만 결과 row에 남깁니다."],
            next_action="후속 구현에서 weight +/-5%p, drop-one, window perturbation을 실제 재계산합니다.",
        )
    )

    monitoring_status = "PASS" if active_components and abs(target_weight_total - 100.0) <= 0.01 and has_benchmark else "REVIEW"
    diagnostics.append(
        _domain_result(
            domain="monitoring_baseline_seed",
            title="12. Monitoring Baseline Seed",
            status=monitoring_status,
            origin="new_diagnostic",
            key_metric="monthly / rebalance review",
            summary="Final Review 이후 사후관리 baseline으로 쓸 component, benchmark, trigger seed를 구성했습니다.",
            evidence_rows=[
                {"Item": "Review cadence", "Value": "monthly_or_rebalance_review"},
                {"Item": "Benchmark present", "Value": has_benchmark},
                {"Item": "Active component count", "Value": len(active_components)},
                {"Item": "Target weight total", "Value": f"{target_weight_total:.2f}%"},
            ],
            limitations=["이 seed는 live approval이나 주문 지시가 아니라 최종 판단 이후 관찰 기준입니다."],
            next_action="Final Review에서 선택/보류/거절 판단과 함께 monitoring 기준을 확정합니다.",
        )
    )

    diagnostic_hard_blockers = [
        f"{item.get('title')}: {item.get('summary')}"
        for item in diagnostics
        if item.get("status") == "BLOCKED"
    ]
    for blocker in diagnostic_hard_blockers:
        if blocker not in hard_blockers:
            hard_blockers.append(blocker)

    diagnostic_review_gaps = [
        f"{item.get('title')}: {item.get('summary')}"
        for item in diagnostics
        if item.get("status") == "REVIEW"
    ]
    for gap in diagnostic_review_gaps:
        if gap not in review_gaps:
            review_gaps.append(gap)

    intent_mismatch_warnings: list[str] = []
    if answers.get("primary_goal") == "defensive" and equity_exposure > (_optional_float(thresholds.get("equity_exposure_review")) or 70.0):
        intent_mismatch_warnings.append("방어형 목적 대비 주식성 노출이 높습니다.")
    if answers.get("primary_goal") in {"growth", "aggressive"} and known_weight > 0.0 and equity_exposure < 50.0:
        intent_mismatch_warnings.append("성장/공격형 목적 대비 주식성 노출이 낮을 수 있습니다.")
    if complexity_restricts_broad and (
        (_optional_float(flag_exposure.get("sector_theme")) or 0.0) > 0.0 or leveraged_exposure > 0.0
    ):
        intent_mismatch_warnings.append("광범위 ETF만 허용한 프로필과 sector/theme 또는 leveraged/inverse 노출이 충돌합니다.")

    status_counts = _status_counts(diagnostics)
    not_run_domains = [
        {"domain": item.get("domain"), "title": item.get("title"), "next_action": item.get("next_action")}
        for item in diagnostics
        if item.get("status") == "NOT_RUN"
    ]
    not_run_critical_domains = [
        item
        for item in not_run_domains
        if item.get("domain")
        in {
            "correlation_diversification_risk_contribution",
            "stress_scenario_diagnostics",
            "alternative_portfolio_challenge",
            "robustness_sensitivity_overfit",
        }
    ]
    validation_score = _diagnostic_score(diagnostics, hard_blockers)

    if hard_blockers:
        route = "BLOCKED"
        verdict = "Practical Validation 차단: 먼저 blocker를 해결해야 합니다."
        next_action = "Backtest Analysis에서 설정 / 데이터 / 비중을 다시 확인합니다."
    else:
        route = "READY_FOR_FINAL_REVIEW"
        if review_gaps or not_run_domains:
            verdict = "Final Review로 이동 가능: REVIEW / NOT_RUN 항목을 최종 판단 근거로 함께 확인해야 합니다."
            next_action = "Final Review에서 보류, 재검토, 선택 중 현실적인 판단을 남깁니다."
        else:
            verdict = "Final Review로 이동 가능: 실전 후보 검증 자료가 구성되었습니다."
            next_action = "Final Review에서 최종 선택 / 보류 / 거절 / 재검토 판단을 남깁니다."

    component_rows = [
        {
            "Component": _component_title(component),
            "Role": component.get("proposal_role") or "-",
            "Weight": component.get("target_weight"),
            "Asset Buckets": dict(exposure_rows[idx]).get("Primary Buckets") if idx < len(exposure_rows) else "-",
            "Flags": dict(exposure_rows[idx]).get("Flags") if idx < len(exposure_rows) else "-",
            "CAGR": component.get("baseline_cagr"),
            "MDD": component.get("baseline_mdd"),
            "Sharpe": component.get("baseline_sharpe"),
            "Benchmark": component.get("benchmark"),
            "Data Trust": component.get("data_trust_status"),
            "Registry ID": component.get("registry_id") or "-",
        }
        for idx, component in enumerate(active_components)
    ]

    return {
        "schema_version": PRACTICAL_VALIDATION_RESULT_SCHEMA_VERSION,
        "validation_id": f"validation_{_slug(source_id)}_{uuid4().hex[:8]}",
        "selection_source_id": source_id,
        "created_at": now,
        "updated_at": now,
        "source_kind": source_row.get("source_kind"),
        "source_title": source_title,
        "validation_profile": profile_row,
        "validation_route": route,
        "validation_score": validation_score,
        "verdict": verdict,
        "next_action": next_action,
        "checks": input_checks,
        "hard_blockers": hard_blockers,
        "review_gaps": review_gaps,
        "paper_tracking_gaps": [
            f"{item.get('title')} NOT_RUN 확인 필요"
            for item in not_run_critical_domains
        ],
        "input_evidence": {
            "checks": input_checks,
            "source_period": source_period,
            "source_summary": source_summary,
            "data_trust": data_trust,
            "real_money_signal": real_money,
        },
        "diagnostic_results": diagnostics,
        "diagnostic_display_rows": _diagnostic_display_rows(diagnostics),
        "diagnostic_summary": {
            "status_counts": status_counts,
            "score": validation_score,
            "profile_label": profile_row.get("profile_label"),
            "profile_id": profile_row.get("profile_id"),
            "origin": "practical_validation_v2_core",
        },
        "not_run_domains": not_run_domains,
        "not_run_critical_domains": not_run_critical_domains,
        "intent_mismatch_warnings": intent_mismatch_warnings,
        "invariant_hard_blockers": profile_row.get("invariant_blockers") or [],
        "metrics": {
            "active_components": len(active_components),
            "weight_total": target_weight_total,
            "max_weight": max_weight,
            "asset_exposure": asset_exposure,
            "flag_exposure": flag_exposure,
            "known_weight": known_weight,
            "unknown_weight": unknown_weight,
            "covered_stress_windows": covered_stress_count,
            "local_trial_count": overfit_audit.get("trial_count", 0),
        },
        "component_rows": component_rows,
        "robustness_validation": {
            "robustness_route": "READY_FOR_STRESS_SWEEP" if not hard_blockers else "BLOCKED_FOR_ROBUSTNESS",
            "robustness_score": validation_score if not hard_blockers else 0.0,
            "verdict": "stress / sensitivity / overfit preview가 구성되었습니다." if not hard_blockers else "source blocker가 있어 robustness preview가 차단됩니다.",
            "next_action": "Final Review에서 stress, sensitivity, NOT_RUN 항목을 최종 판단 근거로 확인합니다.",
            "blockers": list(hard_blockers),
            "component_rows": component_rows,
            "stress_summary_rows": stress_rows + sensitivity_rows,
            "overfit_audit": overfit_audit,
            "sensitivity_rows": sensitivity_rows,
        },
        "paper_observation": {
            "mode": "inline_paper_observation",
            "route": "PAPER_OBSERVATION_READY" if not hard_blockers else "PAPER_OBSERVATION_REVIEW",
            "baseline_snapshot": {
                "target_weight_total": target_weight_total,
                "weighted_cagr": dict(source_row.get("summary") or {}).get("cagr"),
                "weighted_mdd": dict(source_row.get("summary") or {}).get("mdd"),
                "active_component_count": len(active_components),
            },
            "active_components": active_components,
            "checks": [
                {
                    "Criteria": "Observation source",
                    "Ready": bool(source_id),
                    "Current": source_id or "-",
                    "Meaning": "Final Review 이후 추적할 source id입니다.",
                },
                {
                    "Criteria": "Monitoring benchmark",
                    "Ready": has_benchmark,
                    "Current": "present" if has_benchmark else "missing",
                    "Meaning": "성과 관찰 시 상대 비교 기준이 있는지 봅니다.",
                },
                {
                    "Criteria": "Review triggers",
                    "Ready": True,
                    "Current": "CAGR / MDD / benchmark / Data Trust",
                    "Meaning": "선택 이후 재검토할 trigger seed입니다.",
                },
            ],
            "review_cadence": "monthly_or_rebalance_review",
            "review_triggers": [
                "CAGR deterioration review",
                "MDD expansion review",
                "Benchmark-relative underperformance review",
                "Data Trust refresh review",
            ],
        },
        "overfit_audit": overfit_audit,
        "stress_window_rows": stress_rows,
        "alternative_baseline_rows": alternative_rows,
        "sensitivity_rows": sensitivity_rows,
        "final_review_handoff": {
            "route": route,
            "allowed": route == "READY_FOR_FINAL_REVIEW",
            "required_confirmations": [
                "REVIEW 상태 domain 확인",
                "NOT_RUN 상태 domain이 최종 판단을 막는지 확인",
                "사용자 검증 프로필과 후보 목적의 충돌 여부 확인",
            ],
            "not_live_approval": True,
        },
        "selection_source_snapshot": source_row,
        "final_decision_schema_target": FINAL_SELECTION_DECISION_V2_SCHEMA_VERSION,
    }


def save_practical_validation_result(result: dict[str, Any]) -> None:
    append_practical_validation_result(dict(result or {}))


def queue_final_review_source_from_validation(
    *,
    source: dict[str, Any],
    validation_result: dict[str, Any],
    persist_validation: bool = True,
) -> None:
    if persist_validation:
        save_practical_validation_result(validation_result)
    st.session_state.final_review_practical_validation_source = {
        "source": dict(source or {}),
        "validation_result": dict(validation_result or {}),
    }
    st.session_state.final_review_practical_validation_notice = (
        f"`{validation_result.get('source_title') or validation_result.get('selection_source_id')}`를 Final Review로 보냈습니다."
    )
    st.session_state.backtest_requested_panel = "Final Review"


def source_components_dataframe(source: dict[str, Any]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for component in list(dict(source or {}).get("components") or []):
        component_row = dict(component or {})
        rows.append(
            {
                "Component": component_row.get("title") or component_row.get("strategy_name") or component_row.get("component_id"),
                "Weight": component_row.get("target_weight"),
                "CAGR": component_row.get("baseline_cagr"),
                "MDD": component_row.get("baseline_mdd"),
                "Benchmark": component_row.get("benchmark"),
                "Data Trust": component_row.get("data_trust_status"),
            }
        )
    return pd.DataFrame(rows)
