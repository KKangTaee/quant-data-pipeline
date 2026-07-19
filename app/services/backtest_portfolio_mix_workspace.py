"""Pure Portfolio Mix draft, validation and Level1 workspace projection."""

from __future__ import annotations

import hashlib
import json
import math
from copy import deepcopy
from datetime import date
from typing import Any, Mapping, Sequence

import pandas as pd

from app.services.backtest_single_settings_workspace import (
    SettingsValidationError,
    build_single_settings_workspace,
    project_single_settings_payload,
)
from app.services.backtest_strategy_catalog import (
    LEVEL1_STRATEGY_MATURITY,
    LEVEL1_STRATEGY_PURPOSE_GROUPS,
    SINGLE_STRATEGY_OPTIONS,
    STRATEGY_FAMILY_VARIANTS,
    resolve_concrete_strategy_display_name,
    resolve_concrete_strategy_key,
)


PORTFOLIO_MIX_WORKSPACE_SCHEMA_VERSION = "backtest_portfolio_mix_workspace_v1"
PORTFOLIO_MIX_SAVED_SCHEMA_VERSION = "backtest_portfolio_mix_saved_v1"
MIX_ROLE_OPTIONS = ("core", "growth", "defense", "satellite")
MIX_ROLE_LABELS = {
    "core": "핵심",
    "growth": "성장",
    "defense": "방어",
    "satellite": "보조",
}
_SCHEMA_VARIANTS = {
    "Strict Annual": "Annual",
    "Strict Quarterly": "Quarterly",
    "Annual": "Annual",
    "Quarterly": "Quarterly",
}
_UI_VARIANTS = {
    "Annual": "Strict Annual",
    "Quarterly": "Strict Quarterly",
}
_SHARED_PAYLOAD_KEYS = frozenset(
    {"start", "end", "timeframe", "option", "strategy_key"}
)


class PortfolioMixValidationError(ValueError):
    """Raised when a Mix draft cannot cross the execution boundary."""

    def __init__(self, errors: Mapping[str, str]):
        self.errors = dict(errors)
        super().__init__("Portfolio Mix 설정값을 확인해 주세요.")


def _as_mapping(value: object) -> dict[str, Any]:
    return deepcopy(dict(value)) if isinstance(value, Mapping) else {}


def _as_sequence(value: object) -> list[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return list(value)
    return []


def _safe_float(value: object) -> float | object:
    try:
        return float(value)
    except (TypeError, ValueError):
        return value


def _finite_float(value: object) -> float | None:
    try:
        resolved = float(value)
    except (TypeError, ValueError):
        return None
    return resolved if math.isfinite(resolved) else None


def _format_percent(value: float | None) -> str:
    return "계산값 없음" if value is None else f"{value * 100:.2f}%"


def _format_ratio(value: float | None) -> str:
    return "계산값 없음" if value is None else f"{value:.2f}"


def _format_amount(value: float | None) -> str:
    return "계산값 없음" if value is None else f"{value:,.2f}"


def _date_parts(value: object) -> tuple[str, str, str] | None:
    resolved = pd.to_datetime(value, errors="coerce")
    if pd.isna(resolved):
        return None
    return (
        resolved.strftime("%Y-%m-%d"),
        resolved.strftime("%Y.%m.%d"),
        resolved.strftime("%Y.%m"),
    )


def _actual_ticks(rows: Sequence[Mapping[str, Any]], maximum: int) -> list[str]:
    dates = [str(row.get("date") or "") for row in rows if row.get("date")]
    if len(dates) <= maximum:
        return dates
    indices = {
        round(position * (len(dates) - 1) / (maximum - 1))
        for position in range(maximum)
    }
    return [dates[index] for index in sorted(indices)]


def _frame(value: object) -> pd.DataFrame:
    return value.copy() if isinstance(value, pd.DataFrame) else pd.DataFrame()


def _summary_row(weighted_bundle: Mapping[str, Any]) -> dict[str, Any]:
    summary_df = _frame(weighted_bundle.get("summary_df"))
    if summary_df.empty:
        return {}
    return dict(summary_df.iloc[0].to_dict())


def _result_rows(weighted_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    result_df = _frame(weighted_bundle.get("result_df"))
    required = {"Date", "Total Balance"}
    if result_df.empty or not required.issubset(result_df.columns):
        return []
    prepared: list[tuple[tuple[str, str, str], float, float | None]] = []
    for raw in result_df.to_dict("records"):
        date_labels = _date_parts(raw.get("Date"))
        balance = _finite_float(raw.get("Total Balance"))
        if date_labels is None or balance is None:
            continue
        prepared.append(
            (date_labels, balance, _finite_float(raw.get("Total Return")))
        )
    if not prepared:
        return []
    base_balance = prepared[0][1]
    rows: list[dict[str, Any]] = []
    for date_labels, balance, monthly_return in prepared:
        index_value = (
            balance / base_balance * 100.0 if base_balance != 0 else None
        )
        cumulative_return = (
            balance / base_balance - 1.0 if base_balance != 0 else None
        )
        rows.append(
            {
                "date": date_labels[0],
                "date_label": date_labels[1],
                "month_label": date_labels[2],
                "balance": balance,
                "balance_label": _format_amount(balance),
                "index_value": round(index_value, 8) if index_value is not None else None,
                "index_label": _format_ratio(index_value),
                "cumulative_return": (
                    round(cumulative_return, 10)
                    if cumulative_return is not None
                    else None
                ),
                "cumulative_return_label": _format_percent(cumulative_return),
                "return_value": monthly_return,
                "return_label": _format_percent(monthly_return),
                "available": monthly_return is not None,
            }
        )
    return rows


def _contribution_projection(
    weighted_bundle: Mapping[str, Any],
) -> dict[str, Any]:
    names = [str(value) for value in list(weighted_bundle.get("component_strategy_names") or [])]
    roles = [str(value) for value in list(weighted_bundle.get("component_roles") or [])]
    weights = [
        _finite_float(value)
        for value in list(weighted_bundle.get("component_input_weights") or [])
    ]
    amount_df = _frame(weighted_bundle.get("component_contribution_amount_df"))
    share_df = _frame(weighted_bundle.get("component_contribution_share_df"))
    if not names:
        names = [str(column) for column in amount_df.columns]

    identity = {
        name: {
            "strategy_label": name,
            "role_label": MIX_ROLE_LABELS.get(
                roles[index] if index < len(roles) else "", "미지정"
            ),
            "target_weight": weights[index] if index < len(weights) else None,
            "target_weight_label": _format_percent(
                (weights[index] / 100.0)
                if index < len(weights) and weights[index] is not None
                else None
            ),
        }
        for index, name in enumerate(names)
    }

    timeline_rows: list[dict[str, Any]] = []
    indices = amount_df.index.union(share_df.index).sort_values()
    for raw_date in indices:
        date_labels = _date_parts(raw_date)
        if date_labels is None:
            continue
        segments: list[dict[str, Any]] = []
        for name in names:
            amount = (
                _finite_float(amount_df.at[raw_date, name])
                if raw_date in amount_df.index and name in amount_df.columns
                else None
            )
            share = (
                _finite_float(share_df.at[raw_date, name])
                if raw_date in share_df.index and name in share_df.columns
                else None
            )
            segments.append(
                {
                    **identity[name],
                    "amount": amount,
                    "amount_label": _format_amount(amount),
                    "share": share,
                    "share_label": _format_percent(share),
                }
            )
        timeline_rows.append(
            {
                "date": date_labels[0],
                "date_label": date_labels[1],
                "segments": segments,
            }
        )

    ending = timeline_rows[-1]["segments"] if timeline_rows else []
    return {
        "summary_rows": ending,
        "timeline_rows": timeline_rows,
    }


def _data_trust_projection(weighted_bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = weighted_bundle.get("component_data_trust_rows")
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)):
        return []
    projected: list[dict[str, Any]] = []
    for raw in rows:
        if not isinstance(raw, Mapping):
            continue
        count = raw.get("Result Rows")
        projected.append(
            {
                "strategy_label": str(raw.get("Strategy") or "구성 전략"),
                "requested_end_label": str(raw.get("Requested End") or "-"),
                "actual_end_label": str(raw.get("Actual Result End") or "-"),
                "result_rows_label": f"{count}개" if count not in (None, "-") else "-",
                "price_freshness_label": str(raw.get("Price Freshness") or "-"),
                "interpretation": str(raw.get("Interpretation") or "확인 가능한 근거가 없습니다."),
            }
        )
    return projected


def build_portfolio_mix_result_evidence(
    weighted_bundle: Mapping[str, Any],
) -> dict[str, Any]:
    """Project a weighted run into user-readable, JSON-safe result evidence."""

    summary = _summary_row(weighted_bundle)
    kpi_specs = (
        ("annualized_return", "연환산 수익률", "CAGR", _format_percent),
        ("maximum_drawdown", "최대 낙폭", "Maximum Drawdown", _format_percent),
        ("sharpe_ratio", "위험 대비 수익", "Sharpe Ratio", _format_ratio),
        ("end_balance", "최종 평가액", "End Balance", _format_amount),
    )
    kpis = []
    for kpi_id, label, source_key, formatter in kpi_specs:
        value = _finite_float(summary.get(source_key))
        kpis.append(
            {
                "id": kpi_id,
                "label": label,
                "value": value,
                "value_label": formatter(value),
            }
        )

    rows = _result_rows(weighted_bundle)
    names = [str(value) for value in list(weighted_bundle.get("component_strategy_names") or [])]
    period_label = (
        f"{rows[0]['date_label']}–{rows[-1]['date_label']}"
        if rows
        else "계산 기간 없음"
    )
    date_policy = str(weighted_bundle.get("date_policy") or "intersection")
    return {
        "identity": {
            "title": "현재 설정으로 계산한 Mix 결과",
            "component_summary": " · ".join(names) if names else "구성 전략 정보 없음",
            "period_label": period_label,
            "date_policy_label": (
                "모든 구성 전략의 공통 기간"
                if date_policy == "intersection"
                else "사용 가능한 전체 기간"
            ),
        },
        "kpis": kpis,
        "equity_chart": {
            "title": "누적 성과 흐름",
            "description": "첫 계산 시점을 100으로 두고 Mix 평가액 변화를 비교합니다.",
            "rows": rows,
            "desktop_ticks": _actual_ticks(rows, 6),
            "compact_ticks": _actual_ticks(rows, 3),
        },
        "monthly_returns": {
            "title": "월별 수익률 변화",
            "description": "0%를 기준으로 월별 상승과 하락을 확인합니다.",
            "chart_rows": [row for row in rows if row["available"]],
            "table_rows": rows,
        },
        "contribution": _contribution_projection(weighted_bundle),
        "calculation_basis": [
            {
                "title": "성과 기준",
                "description": "weighted result의 월별 평가액과 수익률을 그대로 사용합니다.",
            },
            {
                "title": "날짜 정렬",
                "description": (
                    "모든 구성 전략에 값이 있는 공통 월만 계산했습니다."
                    if date_policy == "intersection"
                    else "값이 있는 구성 전략의 비중을 다시 정규화해 전체 월을 계산했습니다."
                ),
            },
            {
                "title": "기여도",
                "description": "목표 비중을 적용한 구성 전략별 평가액과 Mix 내 비중입니다.",
            },
        ],
        "data_trust_rows": _data_trust_projection(weighted_bundle),
    }


def _schema_variant(value: object) -> str | None:
    if value in (None, ""):
        return None
    return _SCHEMA_VARIANTS.get(str(value), str(value))


def _ui_variant(value: object) -> str | None:
    if value in (None, ""):
        return None
    return _UI_VARIANTS.get(str(value), str(value))


def _default_shared(*, today: date | None = None) -> dict[str, Any]:
    resolved_today = today or date.today()
    return {
        "start": "2016-01-01",
        "end": resolved_today.isoformat(),
        "timeframe": "1d",
        "option": "month_end",
        "date_policy": "intersection",
    }


def normalize_portfolio_mix_draft(
    draft: Mapping[str, Any] | None,
    *,
    runtime_options: Mapping[str, Any] | None = None,
    today: date | None = None,
) -> dict[str, Any]:
    """Normalize user draft primitives without running a strategy or persistence."""

    source = _as_mapping(draft)
    shared = {**_default_shared(today=today), **_as_mapping(source.get("shared"))}
    shared = {
        "start": str(shared.get("start") or ""),
        "end": str(shared.get("end") or ""),
        "timeframe": str(shared.get("timeframe") or ""),
        "option": str(shared.get("option") or ""),
        "date_policy": str(shared.get("date_policy") or "intersection"),
    }

    components: list[dict[str, Any]] = []
    for index, raw_component in enumerate(_as_sequence(source.get("components"))):
        component = _as_mapping(raw_component)
        component_id = str(component.get("component_id") or f"component-{index + 1}")
        components.append(
            {
                "component_id": component_id,
                "strategy_choice": str(component.get("strategy_choice") or ""),
                "variant": _schema_variant(component.get("variant")),
                "settings_values": _as_mapping(component.get("settings_values")),
                "role": str(component.get("role") or "satellite"),
                "weight_percent": _safe_float(component.get("weight_percent")),
            }
        )

    return {
        "draft_id": str(source.get("draft_id") or "mix-draft"),
        "source_saved_portfolio_id": (
            str(source["source_saved_portfolio_id"])
            if source.get("source_saved_portfolio_id") not in (None, "")
            else None
        ),
        "shared": shared,
        "components": components,
    }


def _component_concrete_key(component: Mapping[str, Any]) -> str | None:
    strategy_choice = str(component.get("strategy_choice") or "")
    return resolve_concrete_strategy_key(
        strategy_choice,
        _ui_variant(component.get("variant")),
    )


def validate_portfolio_mix_draft(draft: Mapping[str, Any]) -> dict[str, str]:
    """Validate Mix-level fields before any component runner can be called."""

    errors: dict[str, str] = {}
    shared = _as_mapping(draft.get("shared"))
    components = [
        _as_mapping(component) for component in _as_sequence(draft.get("components"))
    ]

    if not 2 <= len(components) <= 4:
        errors["components"] = "구성 전략은 2개 이상 4개 이하로 선택해 주세요."

    start = str(shared.get("start") or "")
    end = str(shared.get("end") or "")
    try:
        start_date = date.fromisoformat(start)
        end_date = date.fromisoformat(end)
        if start_date >= end_date:
            errors["shared.period"] = "시작일은 종료일보다 빨라야 합니다."
    except ValueError:
        errors["shared.period"] = "시작일과 종료일을 확인해 주세요."
    if not str(shared.get("timeframe") or ""):
        errors["shared.timeframe"] = "실행 주기를 선택해 주세요."
    if not str(shared.get("option") or ""):
        errors["shared.option"] = "가격 기준을 선택해 주세요."
    if str(shared.get("date_policy") or "") not in {"intersection", "union"}:
        errors["shared.date_policy"] = "허용되지 않은 날짜 정렬 기준입니다."

    component_ids: set[str] = set()
    concrete_owner: dict[str, str] = {}
    weight_total = 0.0
    for index, component in enumerate(components):
        component_id = str(component.get("component_id") or f"component-{index + 1}")
        prefix = f"components.{component_id}"
        if component_id in component_ids:
            errors[f"{prefix}.component_id"] = "구성 전략 식별자가 중복되었습니다."
        component_ids.add(component_id)

        strategy_choice = str(component.get("strategy_choice") or "")
        variant = _schema_variant(component.get("variant"))
        if strategy_choice not in SINGLE_STRATEGY_OPTIONS:
            errors[f"{prefix}.strategy_choice"] = "허용되지 않은 전략입니다."
            concrete_key = None
        else:
            family_variants = STRATEGY_FAMILY_VARIANTS.get(strategy_choice)
            allowed_variants = {
                _schema_variant(value) for value in (family_variants or {}).keys()
            }
            if family_variants and variant not in allowed_variants:
                errors[f"{prefix}.variant"] = "실행 기준을 선택해 주세요."
                concrete_key = None
            elif not family_variants and variant is not None:
                errors[f"{prefix}.variant"] = "이 전략에는 별도 실행 기준이 없습니다."
                concrete_key = None
            else:
                concrete_key = _component_concrete_key(component)

        if concrete_key:
            if concrete_key in concrete_owner:
                errors[f"{prefix}.strategy_choice"] = (
                    "같은 실행 전략은 한 Mix에 한 번만 추가할 수 있습니다."
                )
            else:
                concrete_owner[concrete_key] = component_id

        role = str(component.get("role") or "")
        if role not in MIX_ROLE_OPTIONS:
            errors[f"{prefix}.role"] = "허용되지 않은 역할입니다."

        try:
            weight = float(component.get("weight_percent"))
        except (TypeError, ValueError):
            errors[f"{prefix}.weight_percent"] = "목표 비중을 숫자로 입력해 주세요."
            continue
        if weight <= 0:
            errors[f"{prefix}.weight_percent"] = "목표 비중은 0보다 커야 합니다."
        weight_total += weight

    if components and abs(weight_total - 100.0) > 0.01:
        errors["allocation.total"] = "목표 비중 합계는 100%여야 합니다."
    return errors


def _component_workspace(
    component: Mapping[str, Any],
    *,
    shared: Mapping[str, Any],
    runtime_options: Mapping[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    strategy_choice = str(component.get("strategy_choice") or "")
    variant = _schema_variant(component.get("variant"))
    supplied = {
        **_as_mapping(component.get("settings_values")),
        "start": shared.get("start"),
        "end": shared.get("end"),
    }
    workspace = build_single_settings_workspace(
        strategy_choice,
        variant,
        supplied,
        _as_mapping(runtime_options),
    )
    payload = project_single_settings_payload(workspace, supplied)
    settings_workspace = deepcopy(workspace)
    settings_sections: list[dict[str, Any]] = []
    for raw_section in settings_workspace.get("sections", []):
        section = deepcopy(dict(raw_section))
        if str(section.get("section_id") or "") == "execution":
            section["section_id"] = "component_execution"
            section["fields"] = [
                field
                for field in list(section.get("fields") or [])
                if str(field.get("field_id") or "") not in {"start", "end"}
            ]
        if section.get("fields"):
            settings_sections.append(section)
    settings_workspace["sections"] = settings_sections
    settings_workspace.pop("action", None)
    overrides = {
        key: deepcopy(value)
        for key, value in payload.items()
        if key not in _SHARED_PAYLOAD_KEYS
    }
    return settings_workspace, overrides


def project_portfolio_mix_component_payloads(
    draft: Mapping[str, Any],
    *,
    runtime_options: Mapping[str, Any] | None = None,
    today: date | None = None,
) -> list[dict[str, Any]]:
    """Compose Single settings contracts into validated compare component payloads."""

    normalized = normalize_portfolio_mix_draft(
        draft,
        runtime_options=runtime_options,
        today=today,
    )
    errors = validate_portfolio_mix_draft(normalized)
    if errors:
        raise PortfolioMixValidationError(errors)

    projections: list[dict[str, Any]] = []
    component_errors: dict[str, str] = {}
    for component in normalized["components"]:
        component_id = str(component["component_id"])
        try:
            settings_workspace, overrides = _component_workspace(
                component,
                shared=normalized["shared"],
                runtime_options=runtime_options,
            )
        except SettingsValidationError as exc:
            for field_id, message in exc.errors.items():
                component_errors[f"components.{component_id}.settings.{field_id}"] = message
            continue
        strategy_choice = str(component["strategy_choice"])
        ui_variant = _ui_variant(component.get("variant"))
        projections.append(
            {
                "component_id": component_id,
                "strategy_choice": strategy_choice,
                "variant": component.get("variant"),
                "strategy_name": resolve_concrete_strategy_display_name(
                    strategy_choice,
                    ui_variant,
                ),
                "concrete_strategy_key": settings_workspace.get(
                    "concrete_strategy_key"
                ),
                "role": component["role"],
                "role_label": MIX_ROLE_LABELS[str(component["role"])],
                "weight_percent": float(component["weight_percent"]),
                "settings_workspace": settings_workspace,
                "overrides": overrides,
            }
        )
    if component_errors:
        raise PortfolioMixValidationError(component_errors)
    return projections


def build_portfolio_mix_fingerprint(
    draft: Mapping[str, Any],
    *,
    runtime_options: Mapping[str, Any] | None = None,
    today: date | None = None,
) -> str:
    """Hash only effective configuration identity, excluding draft/save identity."""

    normalized = normalize_portfolio_mix_draft(
        draft,
        runtime_options=runtime_options,
        today=today,
    )
    canonical_components: list[dict[str, Any]]
    try:
        projections = project_portfolio_mix_component_payloads(
            normalized,
            runtime_options=runtime_options,
            today=today,
        )
    except PortfolioMixValidationError:
        projections = []
    if projections:
        canonical_components = [
            {
                "concrete_strategy_key": projection["concrete_strategy_key"],
                "variant": projection["variant"],
                "effective_settings": projection["overrides"],
                "role": projection["role"],
                "weight_percent": projection["weight_percent"],
            }
            for projection in projections
        ]
    else:
        canonical_components = [
            {
                "strategy_choice": component["strategy_choice"],
                "variant": component["variant"],
                "settings_values": component["settings_values"],
                "role": component["role"],
                "weight_percent": component["weight_percent"],
            }
            for component in normalized["components"]
        ]
    canonical = {
        "shared": normalized["shared"],
        "components": canonical_components,
    }
    encoded = json.dumps(
        canonical,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _purpose_label(strategy_choice: str) -> str:
    return next(
        (
            str(group["label"])
            for group in LEVEL1_STRATEGY_PURPOSE_GROUPS.values()
            if strategy_choice in group["items"]
        ),
        "기타 전략",
    )


def _catalog_projection() -> dict[str, Any]:
    return {
        "groups": [
            {
                "id": str(group_id),
                "label": str(group["label"]),
                "items": [
                    {
                        "strategy_choice": strategy,
                        "label": strategy,
                        "maturity": LEVEL1_STRATEGY_MATURITY[strategy],
                        "maturity_label": (
                            "개발 중"
                            if LEVEL1_STRATEGY_MATURITY[strategy] == "development"
                            else "운영 전략"
                        ),
                        "variants": [
                            {
                                "value": _schema_variant(variant),
                                "label": variant,
                            }
                            for variant in STRATEGY_FAMILY_VARIANTS.get(
                                strategy, {}
                            ).keys()
                        ],
                    }
                    for strategy in group["items"]
                ],
            }
            for group_id, group in LEVEL1_STRATEGY_PURPOSE_GROUPS.items()
        ],
        "roles": [
            {"value": role, "label": MIX_ROLE_LABELS[role]}
            for role in MIX_ROLE_OPTIONS
        ],
    }


def _saved_mix_projection(
    saved_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for raw_record in saved_records:
        record = _as_mapping(raw_record)
        draft_source = extract_saved_portfolio_mix_draft(record)
        if draft_source is None:
            continue
        draft = normalize_portfolio_mix_draft(draft_source)
        components = draft["components"]
        summary = " · ".join(
            f"{component['strategy_choice']} {float(component['weight_percent']):g}%"
            for component in components
        )
        rows.append(
            {
                "id": str(record.get("portfolio_id") or record.get("id") or ""),
                "name": str(record.get("name") or "이름 없는 Mix"),
                "saved_at": str(record.get("updated_at") or record.get("saved_at") or ""),
                "component_count": len(components),
                "component_summary": summary,
            }
        )
    return {"rows": rows, "empty": not rows}


def extract_saved_portfolio_mix_draft(
    record: Mapping[str, Any] | None,
) -> dict[str, Any] | None:
    """Read only the approved new Mix schema from a persisted store record."""

    source = _as_mapping(record)
    if source.get("schema_version") == PORTFOLIO_MIX_SAVED_SCHEMA_VERSION:
        draft = source.get("mix_draft")
        return _as_mapping(draft) if isinstance(draft, Mapping) else None

    source_context = _as_mapping(source.get("source_context"))
    if source_context.get("mix_schema_version") != PORTFOLIO_MIX_SAVED_SCHEMA_VERSION:
        return None
    draft = source_context.get("mix_draft")
    return _as_mapping(draft) if isinstance(draft, Mapping) else None


def _validation_issues(
    errors: Mapping[str, str],
    draft: Mapping[str, Any],
) -> list[dict[str, str]]:
    duplicate_keys: dict[str, int] = {}
    for component in _as_sequence(draft.get("components")):
        if not isinstance(component, Mapping):
            continue
        concrete_key = _component_concrete_key(component)
        if concrete_key:
            duplicate_keys[concrete_key] = duplicate_keys.get(concrete_key, 0) + 1

    root_by_path: dict[str, str] = {}
    for concrete_key, count in duplicate_keys.items():
        if count <= 1:
            continue
        for component in _as_sequence(draft.get("components")):
            if isinstance(component, Mapping) and _component_concrete_key(component) == concrete_key:
                component_id = str(component.get("component_id") or "")
                root_by_path[f"components.{component_id}.strategy_choice"] = (
                    f"duplicate:{concrete_key}"
                )

    issues: list[dict[str, str]] = []
    seen: set[str] = set()
    for path, message in errors.items():
        root_id = root_by_path.get(path, path)
        if root_id in seen:
            continue
        seen.add(root_id)
        issues.append(
            {
                "root_issue_id": root_id,
                "path": path,
                "message": str(message),
            }
        )
    return issues


def build_portfolio_mix_workspace(
    *,
    draft: Mapping[str, Any] | None,
    saved_records: Sequence[Mapping[str, Any]] = (),
    component_states: Mapping[str, Mapping[str, Any]] | None = None,
    current_result: Mapping[str, Any] | None = None,
    last_result: Mapping[str, Any] | None = None,
    action_capabilities: Mapping[str, bool] | None = None,
    runtime_options: Mapping[str, Any] | None = None,
    today: date | None = None,
) -> dict[str, Any]:
    """Build the one-shell read model while keeping runner and persistence external."""

    normalized = normalize_portfolio_mix_draft(
        draft,
        runtime_options=runtime_options,
        today=today,
    )
    errors = validate_portfolio_mix_draft(normalized)
    projections: list[dict[str, Any]] = []
    if not errors:
        try:
            projections = project_portfolio_mix_component_payloads(
                normalized,
                runtime_options=runtime_options,
                today=today,
            )
        except PortfolioMixValidationError as exc:
            errors.update(exc.errors)

    fingerprint = build_portfolio_mix_fingerprint(
        normalized,
        runtime_options=runtime_options,
        today=today,
    )
    candidate_result = _as_mapping(current_result)
    last_candidate = _as_mapping(last_result)
    result_fingerprint = str(
        candidate_result.get("configuration_fingerprint") or ""
    )
    if candidate_result and result_fingerprint == fingerprint:
        result_status = "current"
        current_projection: dict[str, Any] | None = candidate_result
        reference_projection: dict[str, Any] | None = None
    elif candidate_result:
        result_status = "stale"
        current_projection = None
        reference_projection = candidate_result
    elif last_candidate:
        result_status = "stale"
        current_projection = None
        reference_projection = last_candidate
    else:
        result_status = "not_run"
        current_projection = None
        reference_projection = None

    capabilities = {
        key: bool(value) for key, value in _as_mapping(action_capabilities).items()
    }
    validation_issues = _validation_issues(errors, normalized)
    valid = not errors
    execution_action = (
        {
            "id": "run_mix",
            "label": "이 구성으로 Mix 실행",
            "enabled": True,
        }
        if valid and capabilities.get("run_mix")
        else None
    )
    has_development_component = any(
        LEVEL1_STRATEGY_MATURITY.get(str(component.get("strategy_choice")))
        == "development"
        for component in normalized["components"]
    )
    actions: list[dict[str, Any]] = []
    if result_status == "current" and valid:
        if capabilities.get("save_mix"):
            actions.append(
                {"id": "save_mix", "label": "Mix 설정 저장", "enabled": True}
            )
        if capabilities.get("handoff_level2") and not has_development_component:
            actions.append(
                {
                    "id": "handoff_level2",
                    "label": "Level2 검증 후보로 등록",
                    "enabled": True,
                }
            )

    component_cards = []
    projection_by_id = {item["component_id"]: item for item in projections}
    states = _as_mapping(component_states)
    for component in normalized["components"]:
        component_id = str(component["component_id"])
        projection = projection_by_id.get(component_id, {})
        component_cards.append(
            {
                **deepcopy(component),
                "purpose_label": _purpose_label(str(component["strategy_choice"])),
                "maturity": LEVEL1_STRATEGY_MATURITY.get(
                    str(component["strategy_choice"]), "development"
                ),
                "strategy_name": projection.get("strategy_name")
                or str(component["strategy_choice"]),
                "concrete_strategy_key": projection.get("concrete_strategy_key"),
                "settings_workspace": projection.get("settings_workspace"),
                "runtime_state": deepcopy(states.get(component_id) or {"status": "idle"}),
            }
        )

    return {
        "schema_version": PORTFOLIO_MIX_WORKSPACE_SCHEMA_VERSION,
        "draft": normalized,
        "configuration_fingerprint": fingerprint,
        "catalog": _catalog_projection(),
        "component_cards": component_cards,
        "allocation": {
            "total_weight_percent": round(
                sum(
                    float(component.get("weight_percent") or 0.0)
                    for component in normalized["components"]
                    if isinstance(component.get("weight_percent"), (int, float))
                ),
                4,
            ),
            "date_policy": normalized["shared"]["date_policy"],
        },
        "validation": {
            "valid": valid,
            "errors": errors,
            "issues": validation_issues,
            "issue_count": len(validation_issues),
        },
        "saved_mix": _saved_mix_projection(saved_records),
        "result": {
            "status": result_status,
            "current": current_projection,
            "reference": reference_projection,
        },
        "execution_action": execution_action,
        "actions": actions,
    }


__all__ = [
    "MIX_ROLE_LABELS",
    "MIX_ROLE_OPTIONS",
    "PORTFOLIO_MIX_SAVED_SCHEMA_VERSION",
    "PORTFOLIO_MIX_WORKSPACE_SCHEMA_VERSION",
    "PortfolioMixValidationError",
    "build_portfolio_mix_fingerprint",
    "build_portfolio_mix_result_evidence",
    "build_portfolio_mix_workspace",
    "extract_saved_portfolio_mix_draft",
    "normalize_portfolio_mix_draft",
    "project_portfolio_mix_component_payloads",
    "validate_portfolio_mix_draft",
]
