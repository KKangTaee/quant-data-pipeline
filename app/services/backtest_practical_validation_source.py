from __future__ import annotations

import ast
from datetime import datetime
from typing import Any
from uuid import uuid4

import pandas as pd

from app.runtime import PORTFOLIO_SELECTION_SOURCE_SCHEMA_VERSION


VALIDATION_PROFILE_OPTIONS = {
    "conservative_defensive": {
        "label": "방어형",
        "description": "손실 방어, stress, 유동성 근거를 엄격하게 확인",
        "rolling_window_months": 24,
        "equity_exposure_review": 70.0,
        "max_weight_review": 60.0,
        "mdd_review_line": -15.0,
        "cost_interpretation": "엄격",
    },
    "balanced_core": {
        "label": "균형형",
        "description": "수익과 위험 균형을 기본 기준으로 확인",
        "rolling_window_months": 36,
        "equity_exposure_review": 85.0,
        "max_weight_review": 75.0,
        "mdd_review_line": -25.0,
        "cost_interpretation": "보통",
    },
    "growth_aggressive": {
        "label": "성장 / 공격형",
        "description": "손실 허용선은 넓히되 대안 대비 우위와 과최적화 근거를 확인",
        "rolling_window_months": 60,
        "equity_exposure_review": 95.0,
        "max_weight_review": 90.0,
        "mdd_review_line": -35.0,
        "cost_interpretation": "보통",
    },
    "hedged_tactical": {
        "label": "전술 / 헤지형",
        "description": "macro, regime, turnover, hedge 목적 적합성을 엄격하게 확인",
        "rolling_window_months": 24,
        "equity_exposure_review": 85.0,
        "max_weight_review": 70.0,
        "mdd_review_line": -25.0,
        "cost_interpretation": "turnover / slippage 엄격",
    },
    "custom": {
        "label": "사용자 지정",
        "description": "질문 답변 기반 advanced 기준",
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


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    try:
        missing = pd.isna(value)
    except (TypeError, ValueError):
        return False
    if isinstance(missing, bool):
        return missing
    if hasattr(missing, "all"):
        try:
            return bool(missing.all())
        except (TypeError, ValueError):
            return False
    return False


def _json_scalar(value: Any) -> Any:
    if _is_missing(value):
        return None
    if hasattr(value, "item"):
        try:
            return _json_scalar(value.item())
        except Exception:
            pass
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, float):
        return float(value)
    return value


def _date_text(value: Any) -> str | None:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.strftime("%Y-%m-%d")


def _list_cell(value: Any) -> list[Any]:
    if _is_missing(value):
        return []
    if hasattr(value, "tolist") and not isinstance(value, str):
        try:
            value = value.tolist()
        except Exception:
            pass
    if isinstance(value, (list, tuple, set)):
        return [_json_scalar(item) for item in value if not _is_missing(item)]
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        if text.startswith("[") and text.endswith("]"):
            try:
                parsed = ast.literal_eval(text)
            except (SyntaxError, ValueError):
                parsed = None
            if isinstance(parsed, (list, tuple, set)):
                return _list_cell(parsed)
        return [part.strip().strip("'").strip('"') for part in text.split(",") if part.strip()]
    return [_json_scalar(value)]


def _string_list_cell(value: Any) -> list[str]:
    return [str(item).strip() for item in _list_cell(value) if str(item).strip()]


def _float_list_cell(value: Any) -> list[float]:
    output: list[float] = []
    for item in _list_cell(value):
        numeric = _optional_float(item)
        if numeric is not None:
            output.append(float(numeric))
    return output


def _first_present(row: pd.Series, columns: list[str]) -> Any:
    for column in columns:
        if column in row.index and not _is_missing(row.get(column)):
            return row.get(column)
    return None


def _truthy(value: Any) -> bool:
    if _is_missing(value):
        return False
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "t", "yes", "y"}
    return bool(value)


def _target_weights_from_row(row: pd.Series, selected_tickers: list[str]) -> list[float]:
    direct_weights = _float_list_cell(_first_present(row, ["Next Weight", "Target Weight", "Weight"]))
    if direct_weights:
        return [round(float(weight), 6) for weight in direct_weights]

    next_balances = _float_list_cell(_first_present(row, ["Next Balance", "End Balance"]))
    total_balance = _optional_float(row.get("Total Balance"))
    if not next_balances or not total_balance or total_balance <= 0:
        return []
    weights = [balance / total_balance for balance in next_balances[: len(selected_tickers)]]
    return [round(float(weight), 6) for weight in weights]


def _cash_share_from_row(row: pd.Series) -> float | None:
    cash = _optional_float(row.get("Cash"))
    total_balance = _optional_float(row.get("Total Balance"))
    if cash is None or not total_balance or total_balance <= 0:
        return None
    return round(float(cash) / float(total_balance), 6)


def _selection_interpretation(row: dict[str, Any]) -> str:
    selected = list(row.get("selected_tickers") or [])
    weights = list(row.get("target_weights") or [])
    raw_selected = list(row.get("raw_selected_tickers") or [])
    rejected = list(row.get("overlay_rejected_tickers") or [])
    cash_share = _optional_float(row.get("cash_share"))

    if selected:
        if weights and len(weights) == len(selected):
            pairs = ", ".join(f"{symbol} {float(weight) * 100:.1f}%" for symbol, weight in zip(selected, weights))
            sentence = f"Selected {pairs} for the next holding period."
        else:
            sentence = f"Selected {', '.join(selected)} for the next holding period."
    elif cash_share is not None and cash_share >= 0.999:
        sentence = "No active ticker was selected; the portfolio stayed in cash."
    else:
        sentence = "No active ticker selection was captured for this rebalance row."

    details: list[str] = []
    if raw_selected:
        details.append(f"raw candidates: {', '.join(raw_selected)}")
    if rejected:
        details.append(f"overlay rejected: {', '.join(rejected)}")
    if cash_share is not None and cash_share > 0:
        details.append(f"cash share {cash_share * 100:.1f}%")
    return sentence + (f" ({'; '.join(details)})" if details else "")


def compact_selection_history_from_result_df(
    result_df: pd.DataFrame,
    *,
    max_rows: int = 420,
    component_title: str | None = None,
    component_weight: float | None = None,
) -> list[dict[str, Any]]:
    """Extract compact rebalance selection rows from a strategy result dataframe."""

    if not isinstance(result_df, pd.DataFrame) or result_df.empty or "Date" not in result_df.columns:
        return []

    working = result_df.copy()
    if working.columns.duplicated().any():
        working = working.loc[:, ~working.columns.duplicated()].copy()
    working["Date"] = pd.to_datetime(working["Date"], errors="coerce")
    working = working.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    if working.empty:
        return []

    selection_columns = {
        "Ticker",
        "Next Ticker",
        "End Ticker",
        "Raw Selected Ticker",
        "Overlay Rejected Ticker",
        "Rejected Slot Fill Ticker",
        "Defensive Sleeve Ticker",
        "Next Weight",
        "Selected Score",
        "Raw Selected Score",
    }
    if not selection_columns.intersection(set(working.columns)):
        return []

    if "Rebalancing" in working.columns:
        rebalancing = working["Rebalancing"].map(_truthy)
        if rebalancing.any():
            working = working[rebalancing].copy()

    rows: list[dict[str, Any]] = []
    for _, raw_row in working.iterrows():
        selected_tickers = _string_list_cell(_first_present(raw_row, ["Next Ticker", "Ticker"]))
        raw_selected_tickers = _string_list_cell(raw_row.get("Raw Selected Ticker"))
        if not selected_tickers and not raw_selected_tickers:
            continue
        target_weights = _target_weights_from_row(raw_row, selected_tickers)
        row = {
            "date": _date_text(raw_row.get("Date")),
            "component": component_title,
            "component_weight": (
                round(float(component_weight), 6)
                if component_weight is not None
                else None
            ),
            "selected_tickers": selected_tickers,
            "selected_count": int(_optional_float(raw_row.get("Selected Count")) or len(selected_tickers)),
            "target_weights": target_weights,
            "raw_selected_tickers": raw_selected_tickers,
            "raw_selected_scores": _float_list_cell(raw_row.get("Raw Selected Score")),
            "selection_scores": _float_list_cell(raw_row.get("Selected Score")),
            "overlay_rejected_tickers": _string_list_cell(raw_row.get("Overlay Rejected Ticker")),
            "filled_tickers": _string_list_cell(raw_row.get("Rejected Slot Fill Ticker")),
            "defensive_sleeve_tickers": _string_list_cell(raw_row.get("Defensive Sleeve Ticker")),
            "cash_share": _cash_share_from_row(raw_row),
            "total_balance": _optional_float(raw_row.get("Total Balance")),
            "total_return": _optional_float(raw_row.get("Total Return")),
        }
        row["interpretation"] = _selection_interpretation(row)
        rows.append({key: value for key, value in row.items() if value not in (None, "", [], {})})

    if len(rows) > max_rows:
        rows = rows[-max_rows:]
    return rows


def compact_selection_history_from_bundle(
    bundle: dict[str, Any],
    *,
    max_rows: int = 420,
    component_weight: float | None = None,
) -> list[dict[str, Any]]:
    """Persist compact rebalance / holding selections from a UI result bundle."""

    result_df = dict(bundle or {}).get("result_df")
    title = str(dict(bundle or {}).get("strategy_name") or "").strip() or None
    if not isinstance(result_df, pd.DataFrame):
        return []
    return compact_selection_history_from_result_df(
        result_df,
        max_rows=max_rows,
        component_title=title,
        component_weight=component_weight,
    )


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
    cost_model = dict(draft.get("cost_model_snapshot") or {})
    turnover_evidence = dict(draft.get("turnover_evidence_snapshot") or {})
    net_cost_curve = dict(draft.get("net_cost_curve_snapshot") or {})
    real_money = dict(draft.get("real_money_signal") or {})
    selection_history = list(draft.get("selection_history_snapshot") or [])
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
        "selection_history": selection_history,
        "data_trust": {
            "status": data_trust.get("price_freshness_status") or "snapshot",
            "requested_end": data_trust.get("requested_end"),
            "actual_result_start": data_trust.get("actual_result_start"),
            "actual_result_end": data_trust.get("actual_result_end"),
            "result_rows": data_trust.get("result_rows"),
            "warning_count": data_trust.get("warning_count"),
            "excluded_tickers": list(data_trust.get("excluded_tickers") or []),
        },
        "cost_model_snapshot": cost_model,
        "turnover_evidence_snapshot": turnover_evidence,
        "net_cost_curve_snapshot": net_cost_curve,
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
                "selection_history": selection_history,
                "replay_contract": {
                    "settings_snapshot": settings,
                    "cost_model_snapshot": cost_model,
                    "turnover_evidence_snapshot": turnover_evidence,
                    "net_cost_curve_snapshot": net_cost_curve,
                    "source_kind": source_kind,
                },
            }
        ],
        "construction": {
            "source": "single_strategy" if source_kind != "compare_focused_strategy" else "compare_focused_strategy",
            "target_weight_total": 100.0,
            "rebalance_cadence": settings.get("rebalance_freq")
            or settings.get("factor_freq")
            or settings.get("rebalance_interval"),
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
                "selection_history": list(
                    component.get("selection_history") or component.get("selection_history_snapshot") or []
                ),
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
        "selection_history": list(
            prefill.get("selection_history") or prefill.get("selection_history_snapshot") or []
        ),
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


def source_components_dataframe(source: dict[str, Any]) -> pd.DataFrame:
    """Return the compact source component table used by the Practical Validation UI."""
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
