from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import numpy as np
import pandas as pd
import streamlit as st

from app.web.backtest_practical_validation_curve import (
    build_benchmark_parity,
    build_curve_provenance,
    normalize_result_curve as normalize_validation_curve,
)
from app.web.backtest_practical_validation_connectors import build_provider_context
from app.web.runtime import (
    FINAL_SELECTION_DECISION_V2_SCHEMA_VERSION,
    PORTFOLIO_SELECTION_SOURCE_SCHEMA_VERSION,
    PRACTICAL_VALIDATION_RESULT_SCHEMA_VERSION,
    append_portfolio_selection_source,
    append_practical_validation_result,
    load_backtest_run_history,
)
from finance.loaders import load_price_history
from finance.performance import portfolio_performance_summary


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

VALIDATION_PROFILE_DOMAIN_WEIGHTS = {
    "conservative_defensive": {
        "input_evidence_layer": 1.2,
        "asset_allocation_fit": 1.35,
        "concentration_overlap_exposure": 1.55,
        "correlation_diversification_risk_contribution": 1.75,
        "stress_scenario_diagnostics": 1.85,
        "leveraged_inverse_etf_suitability": 1.65,
        "operability_cost_liquidity": 1.65,
        "robustness_sensitivity_overfit": 1.75,
        "alternative_portfolio_challenge": 0.9,
    },
    "balanced_core": {},
    "growth_aggressive": {
        "asset_allocation_fit": 0.9,
        "concentration_overlap_exposure": 0.9,
        "stress_scenario_diagnostics": 1.0,
        "alternative_portfolio_challenge": 1.35,
        "robustness_sensitivity_overfit": 1.15,
        "monitoring_baseline_seed": 1.1,
    },
    "hedged_tactical": {
        "correlation_diversification_risk_contribution": 1.7,
        "regime_macro_suitability": 1.55,
        "sentiment_risk_on_off_overlay": 1.45,
        "stress_scenario_diagnostics": 1.75,
        "leveraged_inverse_etf_suitability": 1.75,
        "operability_cost_liquidity": 1.55,
        "robustness_sensitivity_overfit": 1.8,
    },
    "custom": {},
}


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
    domain_weights = {
        domain: 1.0
        for domain in [
            "input_evidence_layer",
            "asset_allocation_fit",
            "concentration_overlap_exposure",
            "correlation_diversification_risk_contribution",
            "regime_macro_suitability",
            "sentiment_risk_on_off_overlay",
            "stress_scenario_diagnostics",
            "alternative_portfolio_challenge",
            "leveraged_inverse_etf_suitability",
            "operability_cost_liquidity",
            "robustness_sensitivity_overfit",
            "monitoring_baseline_seed",
        ]
    }
    domain_weights.update(VALIDATION_PROFILE_DOMAIN_WEIGHTS.get(profile_key, {}))
    if normalized_answers.get("primary_goal") == "defensive":
        domain_weights["stress_scenario_diagnostics"] = max(domain_weights["stress_scenario_diagnostics"], 1.35)
        domain_weights["asset_allocation_fit"] = max(domain_weights["asset_allocation_fit"], 1.25)
    elif normalized_answers.get("primary_goal") in {"growth", "aggressive"}:
        domain_weights["alternative_portfolio_challenge"] = max(domain_weights["alternative_portfolio_challenge"], 1.3)
    if normalized_answers.get("complexity_allowance") in {"inverse_leverage_limited", "tactical_high_turnover_allowed"}:
        domain_weights["leveraged_inverse_etf_suitability"] = max(domain_weights["leveraged_inverse_etf_suitability"], 1.25)
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
        "domain_weights": {key: round(float(value), 4) for key, value in domain_weights.items()},
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
        "result_curve": list(draft.get("result_curve_snapshot") or []),
        "benchmark_curve": list(draft.get("benchmark_curve_snapshot") or []),
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
                "result_curve": list(draft.get("result_curve_snapshot") or []),
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
                "result_curve": list(component.get("result_curve") or component.get("curve_snapshot") or []),
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
        "weighted_curve": list(prefill.get("weighted_curve_snapshot") or []),
        "result_curve": list(prefill.get("weighted_curve_snapshot") or []),
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


def _component_provider_symbol_weights(active_components: list[dict[str, Any]]) -> dict[str, float]:
    """Approximate provider lookup weights from component target weights and ETF universes."""
    weights: dict[str, float] = {}
    for component in active_components:
        component_weight = _component_weight(component)
        contract = dict(component.get("contract") or {})
        replay_contract = dict(component.get("replay_contract") or {})
        settings = dict(replay_contract.get("settings_snapshot") or {})
        raw_values = [component.get("universe"), contract.get("tickers"), settings.get("tickers")]
        tickers: list[str] = []
        for value in raw_values:
            if isinstance(value, str):
                tickers.extend(part.strip().upper() for part in re.split(r"[,\\s]+", value) if part.strip())
            elif isinstance(value, (list, tuple, set)):
                tickers.extend(str(part or "").strip().upper() for part in value if str(part or "").strip())
        if not tickers:
            tickers.extend(_component_tickers(component))
        benchmark = str(component.get("benchmark") or "").strip().upper()
        tickers = [ticker for ticker in dict.fromkeys(tickers) if ticker and ticker != "-" and ticker != benchmark]
        if not tickers:
            continue
        ticker_weight = component_weight / len(tickers)
        for ticker in tickers:
            weights[ticker] = weights.get(ticker, 0.0) + ticker_weight
    return {ticker: round(weight, 4) for ticker, weight in sorted(weights.items()) if weight > 0.0}


def _provider_origin_label(provider_area: dict[str, Any]) -> str:
    status = str(provider_area.get("status") or "").lower()
    if status in {"actual", "partial"}:
        return "provider_snapshot"
    if status == "bridge":
        return "db_bridge"
    if status == "proxy":
        return "price_proxy"
    return "provider_context"


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


def _diagnostic_score(
    diagnostics: list[dict[str, Any]],
    hard_blockers: list[str],
    profile: dict[str, Any] | None = None,
) -> float:
    if hard_blockers:
        return 0.0
    status_weights = {"PASS": 1.0, "REVIEW": 0.65, "NOT_RUN": 0.35, "BLOCKED": 0.0}
    domain_weights = dict((profile or {}).get("domain_weights") or {})
    if not diagnostics:
        return 0.0
    weighted_score = 0.0
    total_weight = 0.0
    for item in diagnostics:
        domain = str(item.get("domain") or "")
        domain_weight = float(domain_weights.get(domain, 1.0) or 1.0)
        total_weight += domain_weight
        weighted_score += status_weights.get(str(item.get("status") or "NOT_RUN"), 0.35) * domain_weight
    if total_weight <= 0.0:
        return 0.0
    return round(weighted_score / total_weight * 10.0, 1)


def _profile_score_rows(diagnostics: list[dict[str, Any]], profile: dict[str, Any]) -> list[dict[str, Any]]:
    status_weights = {"PASS": 1.0, "REVIEW": 0.65, "NOT_RUN": 0.35, "BLOCKED": 0.0}
    domain_weights = dict(profile.get("domain_weights") or {})
    rows: list[dict[str, Any]] = []
    for item in diagnostics:
        domain = str(item.get("domain") or "")
        domain_weight = float(domain_weights.get(domain, 1.0) or 1.0)
        status = str(item.get("status") or "NOT_RUN")
        rows.append(
            {
                "Domain": item.get("title"),
                "Status": status,
                "Profile Weight": round(domain_weight, 4),
                "Status Points": status_weights.get(status, 0.35),
                "Weighted Points": round(status_weights.get(status, 0.35) * domain_weight, 4),
                "Profile": profile.get("profile_label"),
            }
        )
    return rows


def _parse_date(value: Any) -> pd.Timestamp | None:
    if value in (None, ""):
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed


def _format_date(value: Any) -> str | None:
    parsed = _parse_date(value)
    if parsed is None:
        return None
    return parsed.strftime("%Y-%m-%d")


def _curve_records_from_df(result_df: pd.DataFrame, *, max_rows: int = 420) -> list[dict[str, Any]]:
    if not isinstance(result_df, pd.DataFrame) or result_df.empty:
        return []
    required = {"Date", "Total Balance"}
    if not required.issubset(set(result_df.columns)):
        return []
    working = result_df.copy()
    working["Date"] = pd.to_datetime(working["Date"], errors="coerce")
    working["Total Balance"] = pd.to_numeric(working["Total Balance"], errors="coerce")
    working = working.dropna(subset=["Date", "Total Balance"]).sort_values("Date")
    if working.empty:
        return []
    if "Total Return" not in working.columns:
        working["Total Return"] = working["Total Balance"].pct_change().fillna(0.0)
    else:
        working["Total Return"] = pd.to_numeric(working["Total Return"], errors="coerce").fillna(
            working["Total Balance"].pct_change()
        )
        working["Total Return"] = working["Total Return"].fillna(0.0)
    monthly = (
        working.assign(_month=working["Date"].dt.to_period("M"))
        .groupby("_month", as_index=False)
        .tail(1)
        .sort_values("Date")
    )
    if len(monthly) > max_rows:
        monthly = monthly.tail(max_rows)
    monthly["Date"] = monthly["Date"].dt.strftime("%Y-%m-%d")
    return monthly[["Date", "Total Balance", "Total Return"]].to_dict("records")


def compact_curve_snapshot_from_bundle(bundle: dict[str, Any], *, max_rows: int = 420) -> list[dict[str, Any]]:
    """Persist a compact monthly curve snapshot from a Streamlit result bundle."""
    result_df = dict(bundle or {}).get("result_df")
    return _curve_records_from_df(result_df, max_rows=max_rows) if isinstance(result_df, pd.DataFrame) else []


def compact_benchmark_curve_snapshot_from_bundle(bundle: dict[str, Any], *, max_rows: int = 420) -> list[dict[str, Any]]:
    benchmark_df = dict(bundle or {}).get("benchmark_chart_df")
    if not isinstance(benchmark_df, pd.DataFrame) or benchmark_df.empty:
        return []
    if "Benchmark Total Balance" not in benchmark_df.columns:
        return []
    working = benchmark_df.rename(
        columns={
            "Benchmark Total Balance": "Total Balance",
            "Benchmark Total Return": "Total Return",
        }
    )
    return _curve_records_from_df(working, max_rows=max_rows)


def _normalize_result_curve(value: Any) -> pd.DataFrame:
    if isinstance(value, pd.DataFrame):
        raw = value.copy()
    elif isinstance(value, list):
        raw = pd.DataFrame(value)
    else:
        return pd.DataFrame()
    if raw.empty or "Date" not in raw.columns or "Total Balance" not in raw.columns:
        return pd.DataFrame()
    raw["Date"] = pd.to_datetime(raw["Date"], errors="coerce")
    raw["Total Balance"] = pd.to_numeric(raw["Total Balance"], errors="coerce")
    if "Total Return" in raw.columns:
        raw["Total Return"] = pd.to_numeric(raw["Total Return"], errors="coerce")
    raw = raw.dropna(subset=["Date", "Total Balance"]).sort_values("Date").reset_index(drop=True)
    if raw.empty:
        return raw
    raw["Total Return"] = raw.get("Total Return", raw["Total Balance"].pct_change()).fillna(
        raw["Total Balance"].pct_change()
    )
    raw["Total Return"] = raw["Total Return"].fillna(0.0)
    return raw[["Date", "Total Balance", "Total Return"]]


def _component_universe_tickers(component: dict[str, Any]) -> list[str]:
    contract = dict(component.get("contract") or {})
    replay_contract = dict(component.get("replay_contract") or {})
    settings = dict(replay_contract.get("settings_snapshot") or {})
    raw_values: list[Any] = [
        component.get("universe"),
        contract.get("tickers"),
        settings.get("tickers"),
        component.get("benchmark"),
    ]
    tokens: list[str] = []
    for value in raw_values:
        if isinstance(value, str):
            tokens.extend(part.strip().upper() for part in re.split(r"[,\\s]+", value) if part.strip())
        elif isinstance(value, (list, tuple, set)):
            tokens.extend(str(part or "").strip().upper() for part in value if str(part or "").strip())
    tokens.extend(_component_tickers(component))
    seen: set[str] = set()
    clean: list[str] = []
    for token in tokens:
        if not token or token in seen or token == "-":
            continue
        seen.add(token)
        clean.append(token)
    return clean


def _price_proxy_curve(
    tickers: list[str],
    *,
    start: Any,
    end: Any,
    weights: list[float] | None = None,
    initial_balance: float = 10000.0,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    clean_tickers = [str(ticker or "").strip().upper() for ticker in tickers if str(ticker or "").strip()]
    clean_tickers = list(dict.fromkeys(clean_tickers))
    if not clean_tickers:
        return pd.DataFrame(), {"status": "NOT_RUN", "reason": "ticker 없음"}
    start_text = _format_date(start)
    end_text = _format_date(end)
    try:
        history = load_price_history(symbols=clean_tickers, start=start_text, end=end_text, timeframe="1d")
    except Exception as exc:
        return pd.DataFrame(), {"status": "NOT_RUN", "reason": f"price DB load failed: {exc}"}
    if history.empty:
        return pd.DataFrame(), {"status": "NOT_RUN", "reason": "price history 없음", "tickers": clean_tickers}
    price_col = "adj_close" if "adj_close" in history.columns else "close"
    matrix = history.pivot(index="date", columns="symbol", values=price_col).sort_index()
    matrix = matrix.apply(pd.to_numeric, errors="coerce").ffill().dropna(how="all")
    available = [ticker for ticker in clean_tickers if ticker in matrix.columns and matrix[ticker].dropna().shape[0] >= 2]
    if not available:
        return pd.DataFrame(), {"status": "NOT_RUN", "reason": "usable price series 없음", "tickers": clean_tickers}
    matrix = matrix[available].dropna()
    if matrix.empty:
        return pd.DataFrame(), {"status": "NOT_RUN", "reason": "aligned price series 없음", "tickers": available}
    if weights and len(weights) == len(clean_tickers):
        weight_map = {ticker: float(weight or 0.0) for ticker, weight in zip(clean_tickers, weights)}
        raw_weights = np.array([weight_map.get(ticker, 0.0) for ticker in available], dtype=float)
    else:
        raw_weights = np.array([1.0 / len(available)] * len(available), dtype=float)
    if raw_weights.sum() <= 0:
        raw_weights = np.array([1.0 / len(available)] * len(available), dtype=float)
    raw_weights = raw_weights / raw_weights.sum()
    normalized = matrix.divide(matrix.iloc[0]).mul(raw_weights, axis=1).sum(axis=1)
    balance = normalized * float(initial_balance)
    result = pd.DataFrame({"Date": pd.to_datetime(balance.index), "Total Balance": balance.values})
    result["Total Return"] = result["Total Balance"].pct_change().fillna(0.0)
    missing = [ticker for ticker in clean_tickers if ticker not in available]
    return result.reset_index(drop=True), {
        "status": "PASS" if not missing else "REVIEW",
        "source": "db_price_proxy",
        "tickers": available,
        "missing_tickers": missing,
        "rows": len(result),
    }


def _summary_metrics_from_curve(result_df: pd.DataFrame, *, name: str = "Portfolio") -> dict[str, Any]:
    if not isinstance(result_df, pd.DataFrame) or result_df.empty:
        return {}
    try:
        summary_df = portfolio_performance_summary(result_df.copy(), name=name, freq="D")
    except Exception:
        return {}
    if summary_df.empty:
        return {}
    row = dict(summary_df.iloc[0])
    return {
        "start": _format_date(row.get("Start Date")),
        "end": _format_date(row.get("End Date")),
        "cagr": _optional_float(row.get("CAGR")),
        "mdd": _optional_float(row.get("Maximum Drawdown")),
        "sharpe": _optional_float(row.get("Sharpe Ratio")),
        "std": _optional_float(row.get("Standard Deviation")),
        "end_balance": _optional_float(row.get("End Balance")),
    }


def _combine_component_curves(
    component_curves: list[dict[str, Any]],
    *,
    initial_balance: float = 10000.0,
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    weights: list[float] = []
    for idx, item in enumerate(component_curves):
        curve = _normalize_result_curve(item.get("curve"))
        if curve.empty:
            continue
        start_balance = _optional_float(curve["Total Balance"].iloc[0])
        if not start_balance or start_balance <= 0:
            continue
        normalized = curve[["Date", "Total Balance"]].copy()
        normalized[f"component_{idx}"] = normalized["Total Balance"] / start_balance
        frames.append(normalized[["Date", f"component_{idx}"]].set_index("Date"))
        weights.append(float(item.get("weight") or 0.0))
    if not frames:
        return pd.DataFrame()
    aligned = pd.concat(frames, axis=1, join="inner").sort_index()
    if aligned.empty:
        return pd.DataFrame()
    raw_weights = np.array(weights[: len(aligned.columns)], dtype=float)
    if raw_weights.sum() <= 0:
        raw_weights = np.array([1.0 / len(aligned.columns)] * len(aligned.columns), dtype=float)
    raw_weights = raw_weights / raw_weights.sum()
    balance = aligned.mul(raw_weights, axis=1).sum(axis=1) * float(initial_balance)
    result = pd.DataFrame({"Date": balance.index, "Total Balance": balance.values}).reset_index(drop=True)
    result["Total Return"] = result["Total Balance"].pct_change().fillna(0.0)
    return result


def _window_perturbation_rows(
    portfolio_curve: pd.DataFrame | None,
    *,
    base_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    curve = _normalize_result_curve(portfolio_curve)
    if curve.empty or not base_summary:
        return [
            {
                "Scenario": "Window perturbation",
                "Scope": "start/end, recent 3y/5y",
                "Result Status": "NOT_RUN",
                "Expected Check": "CAGR / MDD / Sharpe dispersion",
            }
        ]

    base_cagr = _optional_float(base_summary.get("cagr"))
    base_mdd = _optional_float(base_summary.get("mdd"))
    if base_cagr is None and base_mdd is None:
        return [
            {
                "Scenario": "Window perturbation",
                "Scope": "start/end, recent 3y/5y",
                "Result Status": "NOT_RUN",
                "Expected Check": "CAGR / MDD / Sharpe dispersion",
            }
        ]

    min_date = curve["Date"].min()
    max_date = curve["Date"].max()
    windows = [
        ("Recent 3Y", max_date - pd.DateOffset(years=3), max_date),
        ("Recent 5Y", max_date - pd.DateOffset(years=5), max_date),
        ("Exclude first 12M", min_date + pd.DateOffset(months=12), max_date),
        ("Exclude last 12M", min_date, max_date - pd.DateOffset(months=12)),
    ]
    rows: list[dict[str, Any]] = []
    for scenario, start_date, end_date in windows:
        window = curve[(curve["Date"] >= start_date) & (curve["Date"] <= end_date)].copy()
        if window["Date"].nunique() < 12:
            rows.append(
                {
                    "Scenario": scenario,
                    "Scope": f"{_format_date(start_date)} -> {_format_date(end_date)}",
                    "Result Status": "NOT_RUN",
                    "Expected Check": "기간 변경 민감도",
                    "Reason": "usable curve rows < 12",
                }
            )
            continue
        summary = _summary_metrics_from_curve(window, name=scenario)
        window_cagr = _optional_float(summary.get("cagr"))
        window_mdd = _optional_float(summary.get("mdd"))
        cagr_delta = window_cagr - base_cagr if window_cagr is not None and base_cagr is not None else None
        mdd_delta = window_mdd - base_mdd if window_mdd is not None and base_mdd is not None else None
        review = (cagr_delta is not None and cagr_delta < -0.03) or (
            mdd_delta is not None and mdd_delta < -0.05
        )
        rows.append(
            {
                "Scenario": scenario,
                "Scope": f"{_format_date(summary.get('start') or start_date)} -> {_format_date(summary.get('end') or end_date)}",
                "Result Status": "REVIEW" if review else "PASS",
                "Expected Check": "기간 변경 민감도",
                "CAGR": window_cagr,
                "MDD": window_mdd,
                "CAGR Delta": cagr_delta,
                "MDD Delta": mdd_delta,
            }
        )
    return rows


def _build_curve_context(
    source_row: dict[str, Any],
    active_components: list[dict[str, Any]],
    *,
    replay_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_period = dict(source_row.get("period") or {})
    replay_row = dict(replay_result or {})
    runtime_curve_source = str(replay_row.get("curve_source") or "actual_runtime_replay")
    replay_component_curves = {
        str(item.get("component_id") or ""): item
        for item in list(replay_row.get("component_results") or [])
        if item.get("result_curve")
    }
    source_curve = _normalize_result_curve(
        source_row.get("result_curve")
        or source_row.get("weighted_curve")
        or dict(source_row.get("source_snapshot") or {}).get("weighted_curve_snapshot")
    )
    replay_curve = normalize_validation_curve(replay_row.get("portfolio_curve"))
    if not replay_curve.empty:
        source_curve = replay_curve
        portfolio_curve_source = runtime_curve_source
    else:
        portfolio_curve_source = ""
    component_curves: list[dict[str, Any]] = []
    for component in active_components:
        replay_component = replay_component_curves.get(str(component.get("component_id") or ""))
        component_curve = normalize_validation_curve(dict(replay_component or {}).get("result_curve"))
        component_source = runtime_curve_source if not component_curve.empty else ""
        if component_curve.empty:
            component_curve = _normalize_result_curve(component.get("result_curve") or component.get("curve_snapshot"))
            component_source = "embedded_result_curve" if not component_curve.empty else ""
        if component_curve.empty:
            tickers = _component_universe_tickers(component)
            component_period = dict(component.get("period") or {})
            component_curve, proxy_meta = _price_proxy_curve(
                tickers,
                start=component.get("period_start") or component_period.get("start") or source_period.get("actual_start") or source_period.get("start"),
                end=component.get("period_end") or component_period.get("end") or source_period.get("actual_end") or source_period.get("end"),
            )
            component_source = str(proxy_meta.get("source") or proxy_meta.get("status") or "proxy_unavailable")
        component_curves.append(
            {
                "component": _component_title(component),
                "weight": _component_weight(component),
                "curve": component_curve,
                "source": component_source,
                "rows": len(component_curve) if isinstance(component_curve, pd.DataFrame) else 0,
            }
        )
    if source_curve.empty:
        source_curve = _combine_component_curves(component_curves)
        portfolio_curve_source = "component_curve_weighted_proxy" if not source_curve.empty else "unavailable"
    elif not portfolio_curve_source:
        portfolio_curve_source = "embedded_source_curve"

    benchmark_ticker = next(
        (
            str(component.get("benchmark") or "").strip().upper()
            for component in active_components
            if str(component.get("benchmark") or "").strip() not in {"", "-"}
        ),
        "",
    )
    benchmark_curve = normalize_validation_curve(replay_row.get("benchmark_curve"))
    benchmark_meta: dict[str, Any] = {"status": "NOT_RUN", "reason": "benchmark 없음"}
    if not benchmark_curve.empty:
        benchmark_meta = {
            "status": "PASS",
            "source": runtime_curve_source,
            "tickers": [replay_row.get("benchmark_ticker") or benchmark_ticker],
        }
    elif benchmark_curve.empty:
        benchmark_curve = _normalize_result_curve(source_row.get("benchmark_curve"))
    if benchmark_curve.empty and benchmark_ticker:
        start_value = source_period.get("actual_start") or source_period.get("start")
        end_value = source_period.get("actual_end") or source_period.get("end")
        if not source_curve.empty:
            start_value = source_curve["Date"].min()
            end_value = source_curve["Date"].max()
        benchmark_curve, benchmark_meta = _price_proxy_curve([benchmark_ticker], start=start_value, end=end_value)
    elif not benchmark_curve.empty and benchmark_meta.get("source") != runtime_curve_source:
        benchmark_meta = {"status": "PASS", "source": "embedded_benchmark_curve", "tickers": [benchmark_ticker]}

    return {
        "portfolio_curve": source_curve,
        "portfolio_curve_source": portfolio_curve_source,
        "portfolio_summary": _summary_metrics_from_curve(source_curve, name="Candidate Portfolio"),
        "component_curves": component_curves,
        "benchmark_ticker": benchmark_ticker,
        "benchmark_curve": benchmark_curve,
        "benchmark_meta": benchmark_meta,
        "curve_rows": [
            {
                "Component": item.get("component"),
                "Weight": item.get("weight"),
                "Curve Source": item.get("source"),
                "Rows": item.get("rows"),
            }
            for item in component_curves
        ],
    }


def _aligned_monthly_returns(curves: list[dict[str, Any]]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for idx, item in enumerate(curves):
        curve = _normalize_result_curve(item.get("curve"))
        if curve.empty:
            continue
        monthly = (
            curve.assign(_month=curve["Date"].dt.to_period("M"))
            .groupby("_month", as_index=False)
            .tail(1)
            .sort_values("Date")
        )
        monthly[f"component_{idx}"] = monthly["Total Balance"].pct_change()
        frames.append(monthly[["Date", f"component_{idx}"]].dropna().set_index("Date"))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, axis=1, join="inner").dropna(how="any")


def _rolling_validation_evidence(
    portfolio_curve: pd.DataFrame,
    benchmark_curve: pd.DataFrame,
    *,
    window_months: int,
    mdd_review_line: float,
) -> dict[str, Any]:
    curve = _normalize_result_curve(portfolio_curve)
    if curve.empty:
        return {"status": "NOT_RUN", "rows": [], "summary": "portfolio curve 없음"}
    monthly = (
        curve.assign(_month=curve["Date"].dt.to_period("M"))
        .groupby("_month", as_index=False)
        .tail(1)
        .sort_values("Date")
        .reset_index(drop=True)
    )
    if len(monthly) < max(window_months + 1, 6):
        return {"status": "NOT_RUN", "rows": [], "summary": f"{window_months}개월 rolling 계산에 필요한 월별 데이터가 부족합니다."}
    rows: list[dict[str, Any]] = []
    for end_idx in range(window_months, len(monthly)):
        window = monthly.iloc[end_idx - window_months : end_idx + 1].copy()
        start_balance = _optional_float(window["Total Balance"].iloc[0])
        end_balance = _optional_float(window["Total Balance"].iloc[-1])
        if not start_balance or end_balance is None or start_balance <= 0:
            continue
        years = max((window["Date"].iloc[-1] - window["Date"].iloc[0]).days / 365.25, 1 / 12)
        cagr = (end_balance / start_balance) ** (1 / years) - 1
        drawdown = window["Total Balance"] / window["Total Balance"].cummax() - 1
        rows.append(
            {
                "Window End": _format_date(window["Date"].iloc[-1]),
                "Window Months": window_months,
                "CAGR": cagr,
                "MDD": float(drawdown.min()),
            }
        )
    if not rows:
        return {"status": "NOT_RUN", "rows": [], "summary": "rolling windows 계산 실패"}
    worst_mdd = min(float(row["MDD"]) for row in rows)
    worst_cagr = min(float(row["CAGR"]) for row in rows)
    negative_share = sum(1 for row in rows if float(row["CAGR"]) < 0) / len(rows)
    evidence_rows = [
        {
            "Metric": "Rolling windows",
            "Value": len(rows),
            "Threshold": f"{window_months}M",
            "Judgment": "computed",
        },
        {
            "Metric": "Worst rolling CAGR",
            "Value": worst_cagr,
            "Threshold": ">= 0 preferred",
            "Judgment": "REVIEW" if worst_cagr < 0 else "PASS",
        },
        {
            "Metric": "Worst rolling MDD",
            "Value": worst_mdd,
            "Threshold": mdd_review_line / 100.0,
            "Judgment": "REVIEW" if worst_mdd < (mdd_review_line / 100.0) else "PASS",
        },
        {
            "Metric": "Negative rolling CAGR share",
            "Value": negative_share,
            "Threshold": "<= 35%",
            "Judgment": "REVIEW" if negative_share > 0.35 else "PASS",
        },
    ]
    status = "REVIEW" if any(row["Judgment"] == "REVIEW" for row in evidence_rows) else "PASS"
    return {
        "status": status,
        "rows": evidence_rows,
        "summary": f"{window_months}개월 rolling 기준 worst CAGR {worst_cagr:.2%}, worst MDD {worst_mdd:.2%}",
        "metrics": {
            "window_months": window_months,
            "window_count": len(rows),
            "worst_rolling_cagr": worst_cagr,
            "worst_rolling_mdd": worst_mdd,
            "negative_rolling_cagr_share": negative_share,
        },
    }


def _load_static_stress_windows() -> list[dict[str, Any]]:
    if not STRESS_WINDOW_FILE.exists():
        return []
    try:
        payload = json.loads(STRESS_WINDOW_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [dict(row or {}) for row in list(payload.get("windows") or []) if isinstance(row, dict)]


def _period_curve_metrics(result_df: pd.DataFrame, *, start: Any, end: Any) -> dict[str, Any]:
    curve = _normalize_result_curve(result_df)
    start_ts = _parse_date(start)
    end_ts = _parse_date(end)
    if curve.empty or start_ts is None or end_ts is None:
        return {}
    window = curve[(curve["Date"] >= start_ts) & (curve["Date"] <= end_ts)].copy()
    if len(window) < 2:
        return {}
    start_balance = _optional_float(window["Total Balance"].iloc[0])
    end_balance = _optional_float(window["Total Balance"].iloc[-1])
    if not start_balance or end_balance is None or start_balance <= 0:
        return {}
    drawdown = window["Total Balance"] / window["Total Balance"].cummax() - 1
    return {
        "start": _format_date(window["Date"].iloc[0]),
        "end": _format_date(window["Date"].iloc[-1]),
        "return": end_balance / start_balance - 1.0,
        "mdd": float(drawdown.min()),
        "rows": len(window),
    }


def _stress_window_rows(
    source_period: dict[str, Any],
    portfolio_curve: pd.DataFrame | None = None,
    benchmark_curve: pd.DataFrame | None = None,
) -> list[dict[str, Any]]:
    actual_start = _parse_date(source_period.get("actual_start") or source_period.get("start"))
    actual_end = _parse_date(source_period.get("actual_end") or source_period.get("end"))
    portfolio_curve = _normalize_result_curve(portfolio_curve)
    benchmark_curve = _normalize_result_curve(benchmark_curve)
    rows: list[dict[str, Any]] = []
    for window in _load_static_stress_windows():
        start = _parse_date(window.get("start"))
        end = _parse_date(window.get("end"))
        if actual_start is None or actual_end is None or start is None or end is None:
            coverage = "UNKNOWN"
            result_status = "NOT_RUN"
            judgment = "기간 정보 부족"
        elif actual_end < start or actual_start > end:
            coverage = "NOT_COVERED"
            result_status = "NOT_RUN"
            judgment = "기간 미포함"
        else:
            coverage = "COVERED"
            portfolio_metrics = _period_curve_metrics(portfolio_curve, start=start, end=end)
            benchmark_metrics = _period_curve_metrics(benchmark_curve, start=start, end=end)
            if portfolio_metrics:
                result_status = "REVIEW" if (_optional_float(portfolio_metrics.get("mdd")) or 0.0) < -0.20 else "PASS"
                judgment = "구간 성과 계산됨"
            else:
                result_status = "NOT_RUN"
                judgment = "curve replay 필요"
            benchmark_return = _optional_float(benchmark_metrics.get("return"))
            portfolio_return = _optional_float(portfolio_metrics.get("return"))
            benchmark_spread = (
                portfolio_return - benchmark_return
                if portfolio_return is not None and benchmark_return is not None
                else None
            )
        rows.append(
            {
                "Scenario": window.get("label") or window.get("id"),
                "Window": f"{window.get('start')} -> {window.get('end')}",
                "Category": window.get("category"),
                "Coverage": coverage,
                "Result Status": result_status,
                "Portfolio Return": portfolio_metrics.get("return") if coverage == "COVERED" and "portfolio_metrics" in locals() else None,
                "Portfolio MDD": portfolio_metrics.get("mdd") if coverage == "COVERED" and "portfolio_metrics" in locals() else None,
                "Benchmark Spread": benchmark_spread if coverage == "COVERED" and "benchmark_spread" in locals() else None,
                "Expected Check": "return / MDD / benchmark spread",
                "Judgment": judgment,
                "Decision Use": "Stress / scenario evidence",
            }
        )
        if "portfolio_metrics" in locals():
            del portfolio_metrics
        if "benchmark_metrics" in locals():
            del benchmark_metrics
        if "benchmark_spread" in locals():
            del benchmark_spread
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


def _baseline_rows(
    portfolio_curve: pd.DataFrame | None = None,
    *,
    source_period: dict[str, Any] | None = None,
    success_metric: str = "better_risk_adjusted",
) -> list[dict[str, Any]]:
    portfolio_curve = _normalize_result_curve(portfolio_curve)
    if not portfolio_curve.empty:
        start_value = portfolio_curve["Date"].min()
        end_value = portfolio_curve["Date"].max()
    else:
        source_period = dict(source_period or {})
        start_value = source_period.get("actual_start") or source_period.get("start")
        end_value = source_period.get("actual_end") or source_period.get("end")
    candidate_summary = _summary_metrics_from_curve(portfolio_curve, name="Candidate")
    definitions = [
        ("SPY", "미국 대형주 broad equity 단순 대안", ["SPY"], [1.0], "MVP"),
        ("QQQ", "성장 / Nasdaq 노출 단순 대안", ["QQQ"], [1.0], "MVP"),
        ("60/40 proxy", "주식 + 채권 균형 대안", ["SPY", "TLT"], [0.6, 0.4], "MVP"),
        ("cash-aware baseline", "현금 또는 단기채를 섞은 방어형 대안", ["SPY", "TLT", "BIL"], [0.6, 0.2, 0.2], "MVP"),
        ("All Weather-like proxy", "regime 분산형 대리 비교군", ["SPY", "TLT", "IEF", "GLD", "DBC"], [0.30, 0.30, 0.15, 0.15, 0.10], "Future"),
    ]
    rows: list[dict[str, Any]] = []
    for name, purpose, tickers, weights, priority in definitions:
        baseline_curve, meta = _price_proxy_curve(tickers, start=start_value, end=end_value, weights=weights)
        baseline_summary = _summary_metrics_from_curve(baseline_curve, name=name)
        candidate_cagr = _optional_float(candidate_summary.get("cagr"))
        candidate_mdd = _optional_float(candidate_summary.get("mdd"))
        candidate_sharpe = _optional_float(candidate_summary.get("sharpe"))
        baseline_cagr = _optional_float(baseline_summary.get("cagr"))
        baseline_mdd = _optional_float(baseline_summary.get("mdd"))
        baseline_sharpe = _optional_float(baseline_summary.get("sharpe"))
        cagr_spread = candidate_cagr - baseline_cagr if candidate_cagr is not None and baseline_cagr is not None else None
        mdd_advantage = candidate_mdd - baseline_mdd if candidate_mdd is not None and baseline_mdd is not None else None
        sharpe_spread = candidate_sharpe - baseline_sharpe if candidate_sharpe is not None and baseline_sharpe is not None else None
        if baseline_curve.empty or not candidate_summary:
            result_status = "NOT_RUN"
            judgment = str(meta.get("reason") or "candidate/baseline curve 부족")
        elif success_metric == "higher_return":
            result_status = "PASS" if (cagr_spread or 0.0) > 0 else "REVIEW"
            judgment = "CAGR spread 기준"
        elif success_metric == "lower_mdd":
            result_status = "PASS" if (mdd_advantage or 0.0) >= 0 else "REVIEW"
            judgment = "MDD advantage 기준"
        elif success_metric == "better_downside_defense":
            result_status = "PASS" if (mdd_advantage or 0.0) >= 0 else "REVIEW"
            judgment = "downside defense 기준"
        else:
            result_status = "PASS" if (sharpe_spread or 0.0) >= 0 else "REVIEW"
            judgment = "risk-adjusted spread 기준"
        rows.append(
            {
                "Baseline": name,
                "Purpose": purpose,
                "Priority": priority,
                "Result Status": result_status,
                "Candidate CAGR": candidate_cagr,
                "Baseline CAGR": baseline_cagr,
                "CAGR Spread": cagr_spread,
                "Candidate MDD": candidate_mdd,
                "Baseline MDD": baseline_mdd,
                "MDD Advantage": mdd_advantage,
                "Sharpe Spread": sharpe_spread,
                "Judgment": judgment,
            }
        )
    return rows


def _sensitivity_rows(
    active_components: list[dict[str, Any]],
    component_curves: list[dict[str, Any]] | None = None,
    portfolio_curve: pd.DataFrame | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    portfolio_summary = _summary_metrics_from_curve(_normalize_result_curve(portfolio_curve), name="Portfolio")
    rows.extend(_window_perturbation_rows(portfolio_curve, base_summary=portfolio_summary))
    if len(active_components) > 1:
        usable_curves = list(component_curves or [])
        if usable_curves and portfolio_summary:
            base_cagr = _optional_float(portfolio_summary.get("cagr"))
            base_mdd = _optional_float(portfolio_summary.get("mdd"))
            for drop_idx, component in enumerate(active_components):
                drop_curves = [
                    dict(item)
                    for idx, item in enumerate(usable_curves)
                    if idx != drop_idx and not _normalize_result_curve(item.get("curve")).empty
                ]
                if not drop_curves:
                    continue
                drop_result = _combine_component_curves(drop_curves)
                drop_summary = _summary_metrics_from_curve(drop_result, name="Drop One")
                drop_cagr = _optional_float(drop_summary.get("cagr"))
                drop_mdd = _optional_float(drop_summary.get("mdd"))
                cagr_delta = drop_cagr - base_cagr if drop_cagr is not None and base_cagr is not None else None
                mdd_delta = drop_mdd - base_mdd if drop_mdd is not None and base_mdd is not None else None
                review = (cagr_delta is not None and cagr_delta < -0.03) or (
                    mdd_delta is not None and mdd_delta < -0.05
                )
                rows.append(
                    {
                        "Scenario": f"Drop-one: {_component_title(component)}",
                        "Scope": "remove one component and renormalize",
                        "Result Status": "REVIEW" if review else "PASS",
                        "Expected Check": "특정 component 의존성",
                        "CAGR Delta": cagr_delta,
                        "MDD Delta": mdd_delta,
                    }
                )
            if len(active_components) == len(usable_curves):
                for tilt_idx, component in enumerate(active_components):
                    original_weights = np.array([_component_weight(item) for item in active_components], dtype=float)
                    if original_weights.sum() <= 0:
                        continue
                    tilted = original_weights.copy()
                    tilted[tilt_idx] = min(100.0, tilted[tilt_idx] + 5.0)
                    reduce_total = tilted.sum() - 100.0
                    if reduce_total > 0 and len(tilted) > 1:
                        other_indices = [idx for idx in range(len(tilted)) if idx != tilt_idx]
                        other_total = tilted[other_indices].sum()
                        if other_total > 0:
                            for idx in other_indices:
                                tilted[idx] = max(0.0, tilted[idx] - reduce_total * tilted[idx] / other_total)
                    tilted_curves = []
                    for idx, item in enumerate(usable_curves):
                        item_copy = dict(item)
                        item_copy["weight"] = float(tilted[idx])
                        tilted_curves.append(item_copy)
                    tilted_result = _combine_component_curves(tilted_curves)
                    tilted_summary = _summary_metrics_from_curve(tilted_result, name="Tilted")
                    tilted_cagr = _optional_float(tilted_summary.get("cagr"))
                    tilted_mdd = _optional_float(tilted_summary.get("mdd"))
                    rows.append(
                        {
                            "Scenario": f"Mix weight +5%p: {_component_title(component)}",
                            "Scope": "component weights",
                            "Result Status": "PASS",
                            "Expected Check": "비중 민감도",
                            "CAGR Delta": tilted_cagr - base_cagr if tilted_cagr is not None and base_cagr is not None else None,
                            "MDD Delta": tilted_mdd - base_mdd if tilted_mdd is not None and base_mdd is not None else None,
                        }
                    )
        else:
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


def _correlation_risk_evidence(component_curves: list[dict[str, Any]]) -> dict[str, Any]:
    returns = _aligned_monthly_returns(component_curves)
    if returns.empty or returns.shape[1] < 2:
        return {
            "status": "NOT_RUN",
            "summary": "component return matrix가 부족해 상관 / 위험기여를 계산하지 못했습니다.",
            "rows": [],
            "metrics": {},
        }
    corr = returns.corr()
    off_diag_values = [
        float(corr.iloc[i, j])
        for i in range(corr.shape[0])
        for j in range(corr.shape[1])
        if i < j and not pd.isna(corr.iloc[i, j])
    ]
    avg_corr = float(np.mean(off_diag_values)) if off_diag_values else None
    max_corr = float(np.max(off_diag_values)) if off_diag_values else None
    vols = returns.std().fillna(0.0)
    weights = np.array([float(item.get("weight") or 0.0) for item in component_curves[: len(vols)]], dtype=float)
    if weights.sum() <= 0:
        weights = np.array([1.0 / len(vols)] * len(vols), dtype=float)
    weights = weights / weights.sum()
    raw_risk = weights * vols.values
    risk_contribution = raw_risk / raw_risk.sum() if raw_risk.sum() > 0 else np.array([0.0] * len(raw_risk))
    max_risk_contribution = float(risk_contribution.max()) if len(risk_contribution) else None
    rows = [
        {
            "Component": component_curves[idx].get("component"),
            "Weight": round(float(weights[idx]) * 100.0, 4),
            "Monthly Vol": float(vols.iloc[idx]),
            "Risk Contribution Proxy": float(risk_contribution[idx]) if idx < len(risk_contribution) else None,
        }
        for idx in range(len(vols))
    ]
    status = "REVIEW" if (max_corr is not None and max_corr > 0.85) or (max_risk_contribution or 0.0) > 0.80 else "PASS"
    return {
        "status": status,
        "summary": f"평균 상관 {avg_corr:.2f}, 최대 risk contribution {max_risk_contribution:.1%}" if avg_corr is not None and max_risk_contribution is not None else "상관 / 위험기여 proxy 계산됨",
        "rows": rows,
        "metrics": {
            "average_correlation": avg_corr,
            "max_correlation": max_corr,
            "max_risk_contribution": max_risk_contribution,
            "monthly_return_rows": len(returns),
        },
    }


def _market_context_evidence(benchmark_curve: pd.DataFrame, *, label: str) -> dict[str, Any]:
    curve = _normalize_result_curve(benchmark_curve)
    if curve.empty or len(curve) < 20:
        return {
            "status": "NOT_RUN",
            "summary": f"{label} proxy 계산에 필요한 benchmark curve가 없습니다.",
            "rows": [],
            "metrics": {},
        }
    recent = curve.tail(min(len(curve), 63)).copy()
    start_balance = _optional_float(recent["Total Balance"].iloc[0])
    end_balance = _optional_float(recent["Total Balance"].iloc[-1])
    recent_return = end_balance / start_balance - 1.0 if start_balance and end_balance is not None else None
    recent_drawdown = float((recent["Total Balance"] / recent["Total Balance"].cummax() - 1).min())
    recent_vol = float(pd.to_numeric(recent["Total Return"], errors="coerce").std() * np.sqrt(252))
    status = "REVIEW" if (recent_drawdown < -0.10 or recent_vol > 0.35) else "PASS"
    return {
        "status": status,
        "summary": f"{label} proxy: recent return {recent_return:.2%}, drawdown {recent_drawdown:.2%}, vol {recent_vol:.2%}" if recent_return is not None else f"{label} proxy 계산됨",
        "rows": [
            {"Metric": "Recent return", "Value": recent_return, "Judgment": "REVIEW" if recent_return is not None and recent_return < -0.10 else "PASS"},
            {"Metric": "Recent drawdown", "Value": recent_drawdown, "Judgment": "REVIEW" if recent_drawdown < -0.10 else "PASS"},
            {"Metric": "Recent annualized vol", "Value": recent_vol, "Judgment": "REVIEW" if recent_vol > 0.35 else "PASS"},
        ],
        "metrics": {
            "recent_return": recent_return,
            "recent_drawdown": recent_drawdown,
            "recent_annualized_vol": recent_vol,
        },
    }


def _operability_rows(active_components: list[dict[str, Any]], source_period: dict[str, Any]) -> list[dict[str, Any]]:
    tickers = sorted({ticker for component in active_components for ticker in _component_universe_tickers(component)})
    if not tickers:
        return []
    end_value = source_period.get("actual_end") or source_period.get("end")
    end_ts = _parse_date(end_value)
    start_ts = end_ts - pd.Timedelta(days=90) if end_ts is not None else None
    try:
        history = load_price_history(
            symbols=tickers,
            start=_format_date(start_ts),
            end=_format_date(end_ts),
            timeframe="1d",
        )
    except Exception:
        return [
            {
                "Ticker": ticker,
                "Status": "NOT_RUN",
                "Latest Close": None,
                "Avg Dollar Volume 60D": None,
                "Reason": "price DB load failed",
            }
            for ticker in tickers
        ]
    if history.empty:
        return [
            {
                "Ticker": ticker,
                "Status": "NOT_RUN",
                "Latest Close": None,
                "Avg Dollar Volume 60D": None,
                "Reason": "price history 없음",
            }
            for ticker in tickers
        ]
    rows: list[dict[str, Any]] = []
    for ticker in tickers:
        ticker_df = history[history["symbol"].astype(str).str.upper() == ticker].copy()
        if ticker_df.empty:
            rows.append({"Ticker": ticker, "Status": "NOT_RUN", "Latest Close": None, "Avg Dollar Volume 60D": None, "Reason": "missing"})
            continue
        ticker_df["close"] = pd.to_numeric(ticker_df["close"], errors="coerce")
        ticker_df["volume"] = pd.to_numeric(ticker_df["volume"], errors="coerce")
        latest_close = _optional_float(ticker_df.sort_values("date")["close"].dropna().iloc[-1]) if not ticker_df["close"].dropna().empty else None
        avg_dollar_volume = float((ticker_df["close"] * ticker_df["volume"]).dropna().tail(60).mean()) if not (ticker_df["close"] * ticker_df["volume"]).dropna().empty else None
        status = "PASS"
        reason = "basic price/volume available"
        if latest_close is None or latest_close < 5.0:
            status = "REVIEW"
            reason = "low or missing latest price"
        if avg_dollar_volume is None or avg_dollar_volume < 5_000_000:
            status = "REVIEW"
            reason = "low or missing average dollar volume"
        rows.append(
            {
                "Ticker": ticker,
                "Status": status,
                "Latest Close": latest_close,
                "Avg Dollar Volume 60D": avg_dollar_volume,
                "Reason": reason,
            }
        )
    return rows


def build_practical_validation_result(
    source: dict[str, Any],
    validation_profile: dict[str, Any] | None = None,
    replay_result: dict[str, Any] | None = None,
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
    replay_row = dict(replay_result or {})
    if replay_row and replay_row.get("status") in {"REVIEW", "BLOCKED"}:
        review_gaps.append(f"Runtime recheck status: {replay_row.get('status')}")
    period_coverage = dict(replay_row.get("period_coverage") or {})
    if period_coverage.get("status") == "REVIEW":
        review_gaps.append(
            "Runtime recheck period coverage review: "
            f"actual end {dict(period_coverage.get('actual_period') or {}).get('end') or '-'} / "
            f"requested end {dict(period_coverage.get('requested_period') or {}).get('end') or '-'}"
        )
    curve_context = _build_curve_context(source_row, active_components, replay_result=replay_row)
    portfolio_curve = _normalize_result_curve(curve_context.get("portfolio_curve"))
    benchmark_curve = _normalize_result_curve(curve_context.get("benchmark_curve"))
    portfolio_summary = dict(curve_context.get("portfolio_summary") or {})
    benchmark_parity = build_benchmark_parity(portfolio_curve, benchmark_curve)
    curve_provenance = build_curve_provenance(curve_context=curve_context, replay_result=replay_row)
    if benchmark_parity.get("status") == "REVIEW":
        review_gaps.append("Benchmark parity review 필요")
    # Provider snapshots answer "what can be verified at validation time", not the saved backtest end.
    provider_as_of = _format_date(now) or _format_date(source_row.get("created_at"))
    if provider_as_of is None:
        provider_as_of = _format_date(source_period.get("actual_end") or source_period.get("end"))
    if provider_as_of is None and not portfolio_curve.empty:
        provider_as_of = _format_date(portfolio_curve["Date"].max())
    provider_symbol_weights = _component_provider_symbol_weights(active_components)
    provider_context = build_provider_context(provider_symbol_weights, as_of_date=provider_as_of)
    provider_coverage = dict(provider_context.get("coverage") or {})
    provider_display_rows = list(provider_context.get("display_rows") or [])
    provider_statuses = {
        str(dict(item or {}).get("diagnostic_status") or "NOT_RUN")
        for item in provider_coverage.values()
        if isinstance(item, dict)
    }

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
        {
            "Criteria": "Curve evidence",
            "Ready": not portfolio_curve.empty,
            "Current": curve_context.get("portfolio_curve_source") or "-",
            "Meaning": "rolling / stress / baseline / correlation 계산에 쓸 portfolio curve가 있는지 봅니다.",
        },
        {
            "Criteria": "Runtime recheck",
            "Ready": replay_row.get("status") in {"PASS", "REVIEW"} and not portfolio_curve.empty,
            "Current": replay_row.get("status") or "NOT_RUN",
            "Meaning": "저장 snapshot이나 DB price proxy가 아니라 기존 strategy runtime이 실행되어 curve evidence를 만들었는지 봅니다.",
        },
        {
            "Criteria": "Runtime period coverage",
            "Ready": period_coverage.get("status") == "PASS",
            "Current": period_coverage.get("status") or "NOT_RUN",
            "Meaning": "최신 재검증 요청 종료일까지 실제 portfolio curve가 따라왔는지 봅니다.",
        },
        {
            "Criteria": "Benchmark parity",
            "Ready": benchmark_parity.get("status") == "PASS",
            "Current": benchmark_parity.get("status") or "NOT_RUN",
            "Meaning": "후보와 benchmark가 같은 기간 / coverage / frequency로 비교되는지 봅니다.",
        },
        {
            "Criteria": "Provider coverage",
            "Ready": "PASS" in provider_statuses or "REVIEW" in provider_statuses,
            "Current": ", ".join(sorted(provider_statuses)) if provider_statuses else "NOT_RUN",
            "Meaning": "ETF 운용성 / holdings / macro snapshot이 Practical Diagnostics에 연결될 수 있는지 봅니다.",
        },
    ]

    exposure_summary = _build_exposure_summary(active_components)
    asset_exposure = dict(exposure_summary.get("asset_exposure") or {})
    flag_exposure = dict(exposure_summary.get("flag_exposure") or {})
    exposure_rows = list(exposure_summary.get("component_rows") or [])
    known_weight = _optional_float(exposure_summary.get("known_weight")) or 0.0
    unknown_weight = _optional_float(exposure_summary.get("unknown_weight")) or 0.0
    provider_exposure = dict(provider_coverage.get("exposure") or {})
    if provider_exposure.get("diagnostic_status") in {"PASS", "REVIEW"}:
        provider_asset_exposure = dict(provider_exposure.get("asset_exposure") or {})
        if provider_asset_exposure:
            asset_exposure = provider_asset_exposure
            known_weight = _optional_float(provider_exposure.get("coverage_weight")) or known_weight
            unknown_weight = round(max(0.0, 100.0 - known_weight), 4)
            exposure_rows = list(provider_exposure.get("evidence_rows") or exposure_rows)
            exposure_summary = {
                **exposure_summary,
                "asset_exposure": asset_exposure,
                "known_weight": known_weight,
                "unknown_weight": unknown_weight,
                "provider_status": provider_exposure.get("status"),
                "provider_missing_symbols": list(provider_exposure.get("missing_symbols") or []),
            }
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
    rolling_evidence = _rolling_validation_evidence(
        portfolio_curve,
        benchmark_curve,
        window_months=int(thresholds.get("rolling_window_months") or 36),
        mdd_review_line=float(thresholds.get("mdd_review_line") or -25.0),
    )

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
    allocation_origin = "new_diagnostic"
    allocation_limitations = ["holdings look-through 데이터가 없으면 ticker/proxy 분류로만 판단합니다."]
    if provider_exposure.get("diagnostic_status") in {"PASS", "REVIEW"}:
        allocation_origin = _provider_origin_label(provider_exposure)
        allocation_status = str(provider_exposure.get("diagnostic_status") or allocation_status)
        if equity_exposure > (_optional_float(thresholds.get("equity_exposure_review")) or 85.0):
            allocation_status = "REVIEW"
            allocation_summary = f"Provider exposure 기준 주식성 노출이 {equity_exposure:.1f}%로 {profile_row['profile_label']} 기준보다 높습니다."
        else:
            allocation_summary = (
                f"Provider exposure snapshot 기준 자산군 coverage가 "
                f"{_optional_float(provider_exposure.get('coverage_weight')) or 0.0:.1f}%입니다."
            )
        allocation_limitations = [
            "ETF-of-ETF는 현재 1차 holdings / exposure 기준이며, 2차 underlying look-through는 후속입니다.",
            "Provider coverage가 없는 ETF는 missing symbol로 남깁니다.",
        ]
    elif active_components and allocation_status == "PASS":
        allocation_status = "REVIEW"
        allocation_summary = "ETF exposure provider snapshot이 없어 ticker/proxy 자산군 분류만 확인했습니다."
    diagnostics.append(
        _domain_result(
            domain="asset_allocation_fit",
            title="2. Asset Allocation Fit",
            status=allocation_status,
            origin=allocation_origin,
            key_metric=f"equity {equity_exposure:.1f}% / unknown {unknown_weight:.1f}%",
            summary=allocation_summary,
            metrics=exposure_summary,
            evidence_rows=exposure_rows,
            limitations=allocation_limitations,
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
    provider_holdings = dict(provider_coverage.get("holdings") or {})
    concentration_origin = "new_diagnostic"
    concentration_key_metric = f"max component {max_weight:.1f}%"
    concentration_metrics = {
        "max_component_weight": round(max_weight, 4),
        "duplicate_benchmark_count": duplicate_benchmark_count,
        "flag_exposure": flag_exposure,
    }
    concentration_evidence_rows = exposure_rows
    concentration_limitations = ["ETF holdings-level overlap은 아직 계산하지 않고 ticker/proxy signal로 먼저 표시합니다."]
    if provider_holdings.get("diagnostic_status") in {"PASS", "REVIEW"}:
        concentration_origin = _provider_origin_label(provider_holdings)
        concentration_status = str(provider_holdings.get("diagnostic_status") or concentration_status)
        concentration_summary = str(provider_holdings.get("summary") or concentration_summary)
        concentration_key_metric = (
            f"top holding {dict(provider_holdings.get('metrics') or {}).get('top_holding_weight', 0.0)}% / "
            f"coverage {_optional_float(provider_holdings.get('coverage_weight')) or 0.0:.1f}%"
        )
        concentration_metrics = {
            **concentration_metrics,
            **dict(provider_holdings.get("metrics") or {}),
            "provider_coverage_weight": provider_holdings.get("coverage_weight"),
            "provider_missing_symbols": list(provider_holdings.get("missing_symbols") or []),
        }
        concentration_evidence_rows = list(provider_holdings.get("evidence_rows") or [])
        concentration_limitations = [
            "Holdings overlap은 최신 저장 snapshot 기준 compact top exposure만 저장합니다.",
            "Full holdings row는 DB에만 있고 Practical Validation JSONL에는 저장하지 않습니다.",
        ]
    elif active_components and concentration_status == "PASS":
        concentration_status = "REVIEW"
        concentration_summary = "ETF holdings snapshot이 없어 holdings overlap 대신 component / ticker proxy 집중도만 확인했습니다."
    diagnostics.append(
        _domain_result(
            domain="concentration_overlap_exposure",
            title="3. Concentration / Overlap / Exposure",
            status=concentration_status,
            origin=concentration_origin,
            key_metric=concentration_key_metric,
            summary=concentration_summary,
            metrics=concentration_metrics,
            evidence_rows=concentration_evidence_rows,
            limitations=concentration_limitations,
            next_action="중복 benchmark 또는 sector/theme 집중이 있으면 단순 대안과 목적을 비교합니다.",
            profile_effect=f"{profile_row['profile_label']} max weight review line {thresholds.get('max_weight_review')}%",
        )
    )

    correlation_evidence = _correlation_risk_evidence(list(curve_context.get("component_curves") or []))
    if len(active_components) <= 1:
        diversification_status = "REVIEW"
        diversification_summary = "단일 component 후보라 component 간 상관 / 위험기여 분산을 확인할 수 없습니다."
        diversification_rows = [
            {
                "Component": _component_title(component),
                "Weight": _component_weight(component),
                "Benchmark": component.get("benchmark") or "-",
                "Replay Contract": "present" if component.get("replay_contract") else "missing",
            }
            for component in active_components
        ]
        diversification_metrics = {}
    elif correlation_evidence.get("status") in {"PASS", "REVIEW"}:
        diversification_status = str(correlation_evidence.get("status"))
        diversification_summary = str(correlation_evidence.get("summary") or "상관 / 위험기여 proxy 계산됨")
        diversification_rows = list(correlation_evidence.get("rows") or [])
        diversification_metrics = dict(correlation_evidence.get("metrics") or {})
    else:
        diversification_status = "NOT_RUN"
        diversification_summary = str(correlation_evidence.get("summary") or "component별 수익률 replay matrix가 아직 없어 correlation / risk contribution은 후속 계산이 필요합니다.")
        diversification_rows = list(curve_context.get("curve_rows") or [])
        diversification_metrics = dict(correlation_evidence.get("metrics") or {})
    diagnostics.append(
        _domain_result(
            domain="correlation_diversification_risk_contribution",
            title="4. Correlation / Diversification / Risk Contribution",
            status=diversification_status,
            origin="new_diagnostic",
            key_metric=f"{len(active_components)} components",
            summary=diversification_summary,
            metrics=diversification_metrics,
            evidence_rows=diversification_rows,
            limitations=["curve가 embedded 결과가 아니라 DB price proxy일 수 있으므로 실제 전략 path와 다를 수 있습니다."],
            next_action="mix 후보라면 component별 return curve replay를 붙여 위험기여도를 계산합니다.",
        )
    )

    provider_macro = dict(provider_coverage.get("macro") or {})
    provider_regime = dict(provider_macro.get("regime") or {})
    provider_sentiment = dict(provider_macro.get("sentiment") or {})
    regime_evidence = _market_context_evidence(benchmark_curve if not benchmark_curve.empty else portfolio_curve, label="Regime")
    if provider_regime.get("diagnostic_status") in {"PASS", "REVIEW"}:
        regime_status = str(provider_regime.get("diagnostic_status"))
        regime_origin = "provider_snapshot"
        regime_key_metric = provider_regime.get("key_metric") or "FRED macro snapshot"
        regime_summary = str(provider_regime.get("summary") or provider_macro.get("summary") or "FRED macro snapshot을 확인했습니다.")
        regime_metrics = dict(provider_macro.get("metrics") or {})
        regime_rows = list(provider_regime.get("evidence_rows") or provider_macro.get("evidence_rows") or [])
        regime_limitations = ["FRED snapshot은 market-context evidence이며 trade signal이나 hard blocker가 아닙니다."]
        regime_next_action = "VIX / yield curve / credit spread가 review 상태이면 Final Review에서 현재 국면과 후보 목적을 같이 확인합니다."
    else:
        regime_status = str(regime_evidence.get("status") or "NOT_RUN")
        if regime_status == "PASS":
            regime_status = "REVIEW"
        regime_origin = "market_proxy" if regime_evidence.get("status") != "NOT_RUN" else "future_connector"
        regime_key_metric = "benchmark recent context"
        regime_summary = str(regime_evidence.get("summary") or "금리, 인플레이션, 경기 국면 데이터 connector가 아직 붙지 않아 macro suitability는 기록만 남깁니다.")
        regime_metrics = dict(regime_evidence.get("metrics") or {})
        regime_rows = list(regime_evidence.get("rows") or [])
        regime_limitations = ["현재는 benchmark recent return/drawdown/vol proxy이며, FRED macro connector data가 없으면 proxy로만 표시합니다."]
        regime_next_action = "Workspace > Ingestion에서 Macro Context Snapshot을 수집합니다."
    diagnostics.append(
        _domain_result(
            domain="regime_macro_suitability",
            title="5. Regime / Macro Suitability",
            status=regime_status,
            origin=regime_origin,
            key_metric=regime_key_metric,
            summary=regime_summary,
            metrics=regime_metrics,
            evidence_rows=regime_rows,
            limitations=regime_limitations,
            next_action=regime_next_action,
        )
    )
    sentiment_evidence = _market_context_evidence(benchmark_curve if not benchmark_curve.empty else portfolio_curve, label="Risk-on/off")
    if provider_sentiment.get("diagnostic_status") in {"PASS", "REVIEW"}:
        sentiment_status = str(provider_sentiment.get("diagnostic_status"))
        sentiment_origin = "provider_snapshot"
        sentiment_key_metric = provider_sentiment.get("key_metric") or "FRED risk-on/off context"
        sentiment_summary = str(provider_sentiment.get("summary") or provider_macro.get("summary") or "FRED sentiment proxy를 확인했습니다.")
        sentiment_metrics = dict(provider_macro.get("metrics") or {})
        sentiment_rows = list(provider_sentiment.get("evidence_rows") or provider_macro.get("evidence_rows") or [])
        sentiment_limitations = ["Sentiment는 VIX / credit spread / yield curve 기반 proxy이며 단독 매수/매도 신호가 아닙니다."]
        sentiment_next_action = "Risk-off / caution이면 Final Review에서 추적 기간과 손실 감내 기준을 더 엄격히 확인합니다."
    else:
        sentiment_status = str(sentiment_evidence.get("status") or "NOT_RUN")
        if sentiment_status == "PASS":
            sentiment_status = "REVIEW"
        sentiment_origin = "market_proxy" if sentiment_evidence.get("status") != "NOT_RUN" else "future_connector"
        sentiment_key_metric = "risk-on/off proxy"
        sentiment_summary = str(sentiment_evidence.get("summary") or "VIX, Fear & Greed, credit spread / yield curve 보조지표는 아직 connector가 필요합니다.")
        sentiment_metrics = dict(sentiment_evidence.get("metrics") or {})
        sentiment_rows = list(sentiment_evidence.get("rows") or [])
        sentiment_limitations = ["VIX/Fear & Greed/Credit Spread가 아니라 price-action proxy입니다. 단독 hard blocker로 쓰지 않습니다."]
        sentiment_next_action = "Workspace > Ingestion에서 Macro Context Snapshot을 수집합니다."
    diagnostics.append(
        _domain_result(
            domain="sentiment_risk_on_off_overlay",
            title="6. Sentiment / Risk-On-Off Overlay",
            status=sentiment_status,
            origin=sentiment_origin,
            key_metric=sentiment_key_metric,
            summary=sentiment_summary,
            metrics=sentiment_metrics,
            evidence_rows=sentiment_rows,
            limitations=sentiment_limitations,
            next_action=sentiment_next_action,
        )
    )

    stress_rows = _stress_window_rows(source_period, portfolio_curve=portfolio_curve, benchmark_curve=benchmark_curve)
    covered_stress_count = sum(1 for row in stress_rows if row.get("Coverage") == "COVERED")
    computed_stress_count = sum(1 for row in stress_rows if row.get("Coverage") == "COVERED" and row.get("Result Status") in {"PASS", "REVIEW"})
    if not stress_rows:
        stress_status = "NOT_RUN"
        stress_summary = "static stress window calendar를 읽지 못했습니다."
    elif any(row.get("Result Status") == "REVIEW" for row in stress_rows if row.get("Coverage") == "COVERED"):
        stress_status = "REVIEW"
        stress_summary = f"stress window {computed_stress_count}개를 계산했고, 일부 구간에서 drawdown review가 필요합니다."
    elif computed_stress_count > 0:
        stress_status = "PASS"
        stress_summary = f"stress window {computed_stress_count}개를 계산했고 즉시 review 수준의 drawdown은 감지되지 않았습니다."
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

    alternative_rows = _baseline_rows(
        portfolio_curve,
        source_period=source_period,
        success_metric=str(answers.get("alternative_success_metric") or "better_risk_adjusted"),
    )
    baseline_status_values = {str(row.get("Result Status") or "NOT_RUN") for row in alternative_rows}
    if "PASS" in baseline_status_values and "REVIEW" not in baseline_status_values:
        alternative_status = "PASS"
        alternative_summary = "후보가 1차 단순 대안 baseline 대비 선택 기준을 충족했습니다."
    elif "PASS" in baseline_status_values or "REVIEW" in baseline_status_values:
        alternative_status = "REVIEW"
        alternative_summary = "일부 단순 대안 대비 복잡성을 보상하는 근거가 부족할 수 있습니다."
    else:
        alternative_status = "NOT_RUN"
        alternative_summary = "단순 대안 baseline replay 비교를 실행하지 못했습니다."
    diagnostics.append(
        _domain_result(
            domain="alternative_portfolio_challenge",
            title="8. Alternative Portfolio Challenge",
            status=alternative_status,
            origin="new_diagnostic",
            key_metric="SPY / QQQ / 60-40 / cash-aware",
            summary=alternative_summary,
            evidence_rows=alternative_rows,
            limitations=["미래 수익 보장이 아니라 단순 대안보다 복잡한 후보를 선택할 근거를 점검하는 용도입니다. DB 가격 proxy baseline입니다."],
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
    provider_operability = dict(provider_coverage.get("operability") or {})
    provider_leverage = dict(provider_operability.get("leverage") or {})
    leveraged_origin = "new_diagnostic"
    leveraged_key_metric = f"{leveraged_exposure:.1f}%"
    leveraged_metrics = {"leveraged_inverse_exposure": round(leveraged_exposure, 4), "flag_exposure": flag_exposure}
    leveraged_rows = exposure_rows
    leveraged_limitations = ["레버리지/인버스 적합성은 ticker proxy 기반이며 holding 목적과 rebalancing cadence를 함께 봐야 합니다."]
    if provider_leverage.get("diagnostic_status") in {"PASS", "REVIEW"}:
        provider_flagged_exposure = _optional_float(provider_leverage.get("flagged_exposure")) or 0.0
        leveraged_exposure = provider_flagged_exposure
        if provider_flagged_exposure > 20.0 and not complexity_allows_inverse:
            leveraged_status = "BLOCKED"
            leveraged_summary = f"Provider metadata 기준 레버리지/인버스 노출이 {provider_flagged_exposure:.1f}%인데 사용자 프로필에서 허용되지 않았습니다."
        elif provider_flagged_exposure > 0.0:
            leveraged_status = "REVIEW"
            leveraged_summary = f"Provider metadata 기준 레버리지/인버스 노출 {provider_flagged_exposure:.1f}%는 운용 목적과 기간 확인이 필요합니다."
        else:
            leveraged_status = "PASS"
            leveraged_summary = "Provider metadata 기준 레버리지/인버스 ETF가 감지되지 않았습니다."
        leveraged_origin = _provider_origin_label(provider_operability)
        leveraged_key_metric = f"{provider_flagged_exposure:.1f}%"
        leveraged_metrics = {
            "leveraged_inverse_exposure": round(provider_flagged_exposure, 4),
            "provider_coverage_weight": provider_operability.get("coverage_weight"),
        }
        leveraged_rows = list(provider_leverage.get("evidence_rows") or [])
        leveraged_limitations = [
            "Provider metadata가 없는 ETF는 missing coverage로 남기며 ticker proxy보다 우선하지 않습니다.",
            "레버리지/인버스 감지는 live approval이 아니라 Final Review 확인 근거입니다.",
        ]
    elif active_components and leveraged_status == "PASS":
        leveraged_status = "REVIEW"
        leveraged_summary = "Provider product metadata가 없어 ticker proxy 기준으로만 레버리지/인버스 노출 부재를 확인했습니다."
    diagnostics.append(
        _domain_result(
            domain="leveraged_inverse_etf_suitability",
            title="9. Leveraged / Inverse ETF Suitability",
            status=leveraged_status,
            origin=leveraged_origin,
            key_metric=leveraged_key_metric,
            summary=leveraged_summary,
            metrics=leveraged_metrics,
            evidence_rows=leveraged_rows,
            limitations=leveraged_limitations,
            next_action="노출이 있으면 Final Review에서 목적, 보유기간, 손실 감내, 재검토 trigger를 명시합니다.",
            profile_effect=profile_row["answer_labels"].get("complexity_allowance", "-"),
        )
    )

    excluded_tickers = list(data_trust.get("excluded_tickers") or [])
    operability_evidence_rows = _operability_rows(active_components, source_period)
    operability_status_values = {str(row.get("Status") or "NOT_RUN") for row in operability_evidence_rows}
    if str(data_trust.get("status") or "").lower() in {"error", "blocked"}:
        operability_status = "BLOCKED"
        operability_summary = "Data Trust가 차단되어 가격/운용 가능성 판단을 진행할 수 없습니다."
    elif "REVIEW" in operability_status_values:
        operability_status = "REVIEW"
        operability_summary = "일부 ticker의 가격 / 거래대금 proxy가 낮거나 누락되어 운용성 확인이 필요합니다."
    elif operability_evidence_rows and operability_status_values == {"PASS"}:
        operability_status = "PASS"
        operability_summary = "기본 가격 / 거래대금 proxy 기준 운용성 blocker는 감지되지 않았습니다."
    elif excluded_tickers or unknown_weight > 50.0:
        operability_status = "REVIEW"
        operability_summary = "제외 ticker 또는 미분류 비중이 있어 ETF 운용성 확인이 필요합니다."
    else:
        operability_status = "REVIEW"
        operability_summary = "기본 source는 있으나 expense ratio, spread, ADV, turnover coverage는 아직 별도 확인이 필요합니다."
    operability_origin = "new_diagnostic"
    operability_key_metric = f"one-way {thresholds.get('one_way_cost_bps')} bps assumption"
    operability_metrics = {
        "one_way_cost_bps": thresholds.get("one_way_cost_bps"),
        "excluded_tickers": excluded_tickers,
        "cost_interpretation": thresholds.get("cost_interpretation"),
    }
    operability_rows = [
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
    ] + operability_evidence_rows
    operability_limitations = ["ETF expense ratio / bid-ask spread 데이터는 후속 connector이며, 현재는 DB price/volume proxy입니다."]
    operability_next_action = "Final Review 전에 cost/liquidity connector가 없다는 점을 판단 근거에 남깁니다."
    if provider_operability.get("diagnostic_status") in {"PASS", "REVIEW"}:
        operability_origin = _provider_origin_label(provider_operability)
        operability_status = str(provider_operability.get("diagnostic_status") or operability_status)
        operability_summary = str(provider_operability.get("summary") or operability_summary)
        operability_key_metric = f"provider coverage {_optional_float(provider_operability.get('coverage_weight')) or 0.0:.1f}%"
        operability_metrics = {
            **operability_metrics,
            **dict(provider_operability.get("metrics") or {}),
            "provider_coverage_weight": provider_operability.get("coverage_weight"),
            "provider_missing_symbols": list(provider_operability.get("missing_symbols") or []),
        }
        operability_rows = list(provider_operability.get("evidence_rows") or []) + [
            {
                "Item": "Cost assumption",
                "Current": f"one-way {thresholds.get('one_way_cost_bps')} bps",
                "Meaning": "provider cost/liquidity snapshot과 함께 보는 보수적 transaction cost 시작값",
            }
        ]
        operability_limitations = [
            "Provider별 field coverage가 다르므로 missing field가 있으면 REVIEW로 남깁니다.",
            "거래 가능성은 자동 주문 승인이 아니라 Final Review 확인 근거입니다.",
        ]
        operability_next_action = "REVIEW ticker가 있으면 expense / AUM / ADV / spread / premium-discount를 Final Review에서 확인합니다."
    elif operability_status == "PASS":
        operability_status = "REVIEW"
        operability_summary = "Provider operability snapshot이 없어 가격 / 거래대금 proxy만 확인했습니다."
    diagnostics.append(
        _domain_result(
            domain="operability_cost_liquidity",
            title="10. Operability / Cost / Liquidity",
            status=operability_status,
            origin=operability_origin,
            key_metric=operability_key_metric,
            summary=operability_summary,
            metrics=operability_metrics,
            evidence_rows=operability_rows,
            limitations=operability_limitations,
            next_action=operability_next_action,
            profile_effect=str(thresholds.get("cost_interpretation") or "-"),
        )
    )

    overfit_audit = _build_overfit_audit(source_row, active_components)
    sensitivity_rows = _sensitivity_rows(
        active_components,
        component_curves=list(curve_context.get("component_curves") or []),
        portfolio_curve=portfolio_curve,
    )
    sensitivity_status_values = {str(row.get("Result Status") or "NOT_RUN") for row in sensitivity_rows}
    robustness_status = (
        "REVIEW"
        if overfit_audit.get("status") == "REVIEW" or "REVIEW" in sensitivity_status_values or rolling_evidence.get("status") == "REVIEW"
        else "PASS"
        if "PASS" in sensitivity_status_values or rolling_evidence.get("status") == "PASS"
        else "NOT_RUN"
    )
    robustness_summary = (
        overfit_audit.get("interpretation")
        if overfit_audit.get("status") == "REVIEW"
        else (
            "curve 기반 sensitivity에서 REVIEW 항목이 있습니다. "
            "window / drop-one / 비중 perturbation은 계산했고, 전략별 parameter sensitivity는 별도 runtime 실행이 필요합니다."
        )
        if "REVIEW" in sensitivity_status_values
        else (
            "window / drop-one / 비중 sensitivity를 curve 기반으로 계산했습니다. "
            "전략별 parameter sensitivity는 별도 runtime 실행이 필요합니다."
        )
        if robustness_status == "PASS"
        else "sensitivity 실행에 필요한 curve가 부족해 계산하지 못했습니다."
    )
    diagnostics.append(
        _domain_result(
            domain="robustness_sensitivity_overfit",
            title="11. Robustness / Sensitivity / Overfit",
            status=robustness_status,
            origin="new_diagnostic",
            key_metric=f"local trials {overfit_audit.get('trial_count', 0)}",
            summary=str(robustness_summary),
            metrics={**overfit_audit, "rolling_validation": dict(rolling_evidence.get("metrics") or {})},
            evidence_rows=list(rolling_evidence.get("rows") or []) + sensitivity_rows,
            limitations=["run_history 원본은 저장하지 않고 local audit summary만 결과 row에 남깁니다. Curve proxy일 수 있습니다."],
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
    validation_score = _diagnostic_score(diagnostics, hard_blockers, profile_row)
    profile_score_rows = _profile_score_rows(diagnostics, profile_row)

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
            "curve_provenance": curve_provenance,
            "benchmark_parity": benchmark_parity,
            "provider_coverage": provider_context,
        },
        "provider_coverage": provider_context,
        "provider_coverage_display_rows": provider_display_rows,
        "diagnostic_results": diagnostics,
        "diagnostic_display_rows": _diagnostic_display_rows(diagnostics),
        "diagnostic_summary": {
            "status_counts": status_counts,
            "score": validation_score,
            "profile_label": profile_row.get("profile_label"),
            "profile_id": profile_row.get("profile_id"),
            "origin": "practical_validation_v2_core",
        },
        "profile_score_rows": profile_score_rows,
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
            "computed_stress_windows": computed_stress_count,
            "local_trial_count": overfit_audit.get("trial_count", 0),
            "portfolio_curve_rows": len(portfolio_curve),
            "portfolio_curve_source": curve_context.get("portfolio_curve_source"),
            "portfolio_curve_summary": portfolio_summary,
            "benchmark_parity_status": benchmark_parity.get("status"),
            "benchmark_parity": benchmark_parity.get("metrics") or {},
            "rolling_validation": rolling_evidence.get("metrics") or {},
            "runtime_recheck_status": replay_row.get("status") or "NOT_RUN",
            "runtime_recheck_mode": replay_row.get("recheck_mode"),
            "runtime_recheck_extension_days": replay_row.get("extension_days"),
            "runtime_recheck_period": replay_row.get("requested_period") or {},
            "runtime_recheck_period_coverage": period_coverage,
            "provider_coverage": {
                "as_of_date": provider_context.get("as_of_date"),
                "symbols": list(provider_context.get("symbols") or []),
                "operability": {
                    "status": dict(provider_coverage.get("operability") or {}).get("status"),
                    "diagnostic_status": dict(provider_coverage.get("operability") or {}).get("diagnostic_status"),
                    "coverage_weight": dict(provider_coverage.get("operability") or {}).get("coverage_weight"),
                },
                "holdings": {
                    "status": dict(provider_coverage.get("holdings") or {}).get("status"),
                    "diagnostic_status": dict(provider_coverage.get("holdings") or {}).get("diagnostic_status"),
                    "coverage_weight": dict(provider_coverage.get("holdings") or {}).get("coverage_weight"),
                },
                "exposure": {
                    "status": dict(provider_coverage.get("exposure") or {}).get("status"),
                    "diagnostic_status": dict(provider_coverage.get("exposure") or {}).get("diagnostic_status"),
                    "coverage_weight": dict(provider_coverage.get("exposure") or {}).get("coverage_weight"),
                },
                "macro": {
                    "status": dict(provider_coverage.get("macro") or {}).get("status"),
                    "diagnostic_status": dict(provider_coverage.get("macro") or {}).get("diagnostic_status"),
                    "series_count": dict(provider_coverage.get("macro") or {}).get("series_count"),
                    "stale_count": dict(provider_coverage.get("macro") or {}).get("stale_count"),
                },
            },
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
            "rolling_validation": rolling_evidence,
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
        "rolling_validation": rolling_evidence,
        "curve_evidence": {
            "portfolio_curve_source": curve_context.get("portfolio_curve_source"),
            "portfolio_curve_rows": len(portfolio_curve),
            "component_curve_rows": list(curve_context.get("curve_rows") or []),
            "benchmark_ticker": curve_context.get("benchmark_ticker"),
            "benchmark_curve_rows": len(benchmark_curve),
            "benchmark_meta": dict(curve_context.get("benchmark_meta") or {}),
            "curve_provenance": curve_provenance,
            "benchmark_parity": benchmark_parity,
            "replay_attempt": replay_row,
            "period_coverage": period_coverage,
        },
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
