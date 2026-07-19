from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date
from typing import Any, Callable, Mapping

from app.services.futures_macro_snapshot import load_overview_futures_macro_materialized_snapshot
from app.services.overview.economic_cycle import build_economic_cycle_read_model

from .diagnosis import BehaviorFacts
from .exposure import ExposureResult


MACRO_CONTEXT_VERSION = "portfolio_monitoring_macro_context_v1"
FAMILY_KEYS = (
    "risk_on",
    "growth",
    "rate_pressure",
    "dollar_pressure",
    "safe_haven",
    "inflation_pressure",
)
PATHWAY_KEYS = ("gold", "dollar", "wti", "copper", "rates", "sp500")


@dataclass(frozen=True)
class MacroContext:
    status: str
    as_of_dates: dict[str, str]
    publication: str
    cycle: dict[int, dict[str, Any]]
    family_scores: dict[str, dict[str, float]]
    outlooks: dict[int, dict[str, Any]]
    pathways: dict[str, dict[str, Any]]
    coverage: float
    warnings: tuple[str, ...]
    version: str = MACRO_CONTEXT_VERSION


@dataclass(frozen=True)
class MacroObservation:
    rule_id: str
    root_id: str
    state: str
    severity: str
    affected_weight: float
    matched_conditions: tuple[str, ...]
    current_observation: str
    source_dates: tuple[str, ...]
    coverage: float
    confidence: str
    publication: str
    change_condition: str
    next_check: str


def _invoke(loader: Callable[..., Any], **kwargs: Any) -> Any:
    try:
        return loader(**kwargs)
    except TypeError:
        return loader()


def _date_text(value: Any) -> str:
    return str(value or "")[:10]


def _score(value: Any) -> float | None:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if numeric != numeric:
        return None
    return round(numeric * 100.0 if abs(numeric) <= 5 else numeric, 4)


def _cycle_rows(value: Any) -> dict[int, dict[str, Any]]:
    if not isinstance(value, Mapping):
        return {}
    rows: dict[int, dict[str, Any]] = {}
    for row in value.get("horizons") or []:
        if not isinstance(row, Mapping):
            continue
        try:
            horizon = int(row.get("horizon_months", row.get("horizon", -1)))
        except (TypeError, ValueError):
            continue
        if horizon not in (0, 1, 2):
            continue
        rows[horizon] = {
            "phase": row.get("dominant_phase"),
            "publication_status": str(row.get("publication_status") or row.get("estimate_status") or "LIMITED"),
            "reason_code": row.get("reason_code"),
        }
    return rows


def _family_rows(value: Any) -> tuple[dict[str, dict[str, float]], dict[int, dict[str, Any]], str, str]:
    if not isinstance(value, Mapping):
        return {}, {}, "", "MISSING"
    pattern_outlook = value.get("pattern_outlook")
    if not isinstance(pattern_outlook, Mapping):
        return {}, {}, "", "MISSING"
    current = pattern_outlook.get("current_pattern")
    current = current if isinstance(current, Mapping) else {}
    families = current.get("families")
    families = families if isinstance(families, Mapping) else {}
    scores: dict[str, dict[str, float]] = {}
    for key in FAMILY_KEYS:
        family = families.get(key)
        if not isinstance(family, Mapping):
            continue
        five = _score(family.get("five_day", family.get("5d")))
        twenty = _score(family.get("twenty_day", family.get("20d")))
        row = {}
        if five is not None:
            row["5d"] = five
        if twenty is not None:
            row["20d"] = twenty
        if row:
            scores[key] = row
    outlooks: dict[int, dict[str, Any]] = {}
    for row in pattern_outlook.get("horizons") or []:
        if not isinstance(row, Mapping):
            continue
        try:
            horizon = int(row.get("horizon", 0))
        except (TypeError, ValueError):
            continue
        if horizon not in (5, 20):
            continue
        outlooks[horizon] = {
            "regime": row.get("dominant_regime"),
            "estimate_status": str(row.get("estimate_status") or "UNAVAILABLE"),
            "edge_label": row.get("edge_label"),
        }
    metadata = value.get("metadata") if isinstance(value.get("metadata"), Mapping) else {}
    as_of = _date_text(metadata.get("as_of_date") or pattern_outlook.get("as_of_date"))
    publication = str(
        pattern_outlook.get("status")
        or metadata.get("snapshot_status")
        or value.get("status")
        or "MISSING"
    ).upper()
    return scores, outlooks, as_of, publication


def _pathway_rows(value: Any) -> tuple[dict[str, dict[str, Any]], str]:
    if not isinstance(value, Mapping):
        return {}, ""
    raw = value.get("pathways")
    rows: dict[str, dict[str, Any]] = {}
    if isinstance(raw, Mapping):
        for key in PATHWAY_KEYS:
            row = raw.get(key)
            if isinstance(row, Mapping):
                rows[key] = dict(row)
    elif isinstance(value.get("market_implications"), list):
        aliases = {
            "equities": "sp500", "stocks": "sp500", "주식": "sp500",
            "bonds_rates": "rates", "채권·금리": "rates",
            "gold": "gold", "금": "gold", "dollar": "dollar", "달러": "dollar",
        }

        def compact(source: Mapping[str, Any]) -> dict[str, Any]:
            price = source.get("price_context") if isinstance(source.get("price_context"), Mapping) else {}
            returns = price.get("returns") if isinstance(price.get("returns"), Mapping) else {}
            path_list = source.get("observed_pathways") or source.get("pathways") or []
            path_states = {
                str(path.get("pathway_id")): str(path.get("status"))
                for path in path_list
                if isinstance(path, Mapping) and path.get("pathway_id")
            }
            recent = _score(returns.get("three_months"))
            return {
                "status": str(source.get("analysis_status") or source.get("coverage_status") or price.get("status") or "OBSERVED"),
                "as_of_date": _date_text(price.get("as_of_date") or value.get("as_of_date")),
                "return_63d": (recent / 100.0 if recent is not None else None),
                "direction": price.get("status"),
                "pathway_states": path_states,
                "real_yield": path_states.get("real_yield") or path_states.get("us_real_yield"),
            }

        for row in value["market_implications"]:
            if not isinstance(row, Mapping):
                continue
            raw_key = str(row.get("asset_group") or row.get("asset_id") or row.get("key") or row.get("asset") or row.get("label") or "").lower()
            key = aliases.get(raw_key, raw_key)
            if key in PATHWAY_KEYS:
                rows[key] = compact(row)
            for asset in row.get("assets") or []:
                if not isinstance(asset, Mapping):
                    continue
                asset_key = str(asset.get("asset_id") or "").lower()
                if asset_key in PATHWAY_KEYS:
                    rows[asset_key] = compact(asset)
    pathway_dates = [str(row.get("as_of_date")) for row in rows.values() if row.get("as_of_date")]
    return rows, max(pathway_dates, default=_date_text(value.get("as_of_date")))


def load_portfolio_macro_context(
    *,
    cycle_loader: Callable[..., Any] | None = None,
    futures_loader: Callable[..., Any] | None = None,
    asset_context_loader: Callable[..., Any] | None = None,
    as_of_date: date | str | None = None,
) -> MacroContext:
    """Read and compact persisted Overview contexts without materialization or writes."""

    target_date = date.fromisoformat(_date_text(as_of_date)) if as_of_date else date.today()
    warnings: list[str] = []
    try:
        cycle_value = _invoke(cycle_loader or build_economic_cycle_read_model, as_of_date=target_date)
    except Exception as exc:
        cycle_value = None
        warnings.append(f"economic cycle read error: {exc}")
    try:
        futures_value = _invoke(futures_loader or load_overview_futures_macro_materialized_snapshot)
    except Exception as exc:
        futures_value = None
        warnings.append(f"futures macro read error: {exc}")
    try:
        asset_value = (
            _invoke(asset_context_loader, as_of_date=target_date)
            if asset_context_loader is not None
            else cycle_value
        )
    except Exception as exc:
        asset_value = None
        warnings.append(f"asset context read error: {exc}")

    cycle = _cycle_rows(cycle_value)
    family_scores, outlooks, futures_date, publication = _family_rows(futures_value)
    pathways, asset_date = _pathway_rows(asset_value)
    cycle_date = _date_text(cycle_value.get("as_of_date")) if isinstance(cycle_value, Mapping) else ""
    as_of_dates = {
        key: value
        for key, value in {
            "economic_cycle": cycle_date,
            "futures_macro": futures_date,
            "asset_context": asset_date,
        }.items()
        if value
    }

    available_sources = sum((bool(cycle), bool(family_scores), bool(pathways)))
    coverage = available_sources / 3.0
    if not cycle:
        warnings.append("economic cycle missing or malformed")
    if not family_scores:
        warnings.append("futures macro missing or malformed")
    if not pathways:
        warnings.append("asset context missing or malformed")
    parsed_dates = []
    for key, value in as_of_dates.items():
        try:
            parsed = date.fromisoformat(value)
        except ValueError:
            warnings.append(f"{key} malformed as-of date")
            continue
        parsed_dates.append(parsed)
        if (target_date - parsed).days > 10:
            warnings.append(f"{key} stale as-of date {value}")
    if len(set(parsed_dates)) > 1:
        warnings.append("source as-of date mismatch")

    cycle_status = str(cycle_value.get("status") or "MISSING").upper() if isinstance(cycle_value, Mapping) else "MISSING"
    publication = publication if publication in {"READY", "LIMITED", "PROVISIONAL"} else "LIMITED"
    status = "READY"
    if coverage < 1.0 or cycle_status != "READY" or publication != "READY" or warnings:
        status = "LIMITED"
    return MacroContext(
        status=status,
        as_of_dates=as_of_dates,
        publication=publication,
        cycle=cycle,
        family_scores=family_scores,
        outlooks=outlooks,
        pathways=pathways,
        coverage=coverage,
        warnings=tuple(dict.fromkeys(warnings)),
    )


def _observation_confidence(coverage: float, publication: str) -> str:
    if coverage >= 0.9 and publication == "READY":
        return "HIGH"
    if coverage >= 0.7 and publication in {"READY", "LIMITED", "PROVISIONAL"}:
        return "MEDIUM"
    return "LOW"


def apply_macro_confidence_cap(observation: MacroObservation) -> MacroObservation:
    """Prevent provisional context from independently publishing HIGH severity."""

    if observation.publication in {"LIMITED", "PROVISIONAL"} and observation.severity == "HIGH":
        return replace(observation, severity="MEDIUM")
    if observation.confidence == "LOW" and observation.severity == "HIGH":
        return replace(observation, severity="MEDIUM")
    return observation


def _source_dates(macro: MacroContext, behavior: BehaviorFacts) -> tuple[str, ...]:
    return tuple(sorted(set(macro.as_of_dates.values()) | set(behavior.source_dates)))


def _make_observation(
    *,
    rule_id: str,
    root_id: str,
    state: str,
    weight: float,
    conditions: tuple[str, ...],
    current: str,
    change: str,
    exposure: ExposureResult,
    behavior: BehaviorFacts,
    macro: MacroContext,
) -> MacroObservation:
    coverage = min(exposure.coverage_ratio, macro.coverage)
    confidence = _observation_confidence(coverage, macro.publication)
    observation = MacroObservation(
        rule_id=rule_id,
        root_id=root_id,
        state=state,
        severity={"low": "LOW", "medium": "MEDIUM", "high": "HIGH"}[state],
        affected_weight=weight,
        matched_conditions=conditions,
        current_observation=current,
        source_dates=_source_dates(macro, behavior),
        coverage=coverage,
        confidence=confidence,
        publication=macro.publication,
        change_condition=change,
        next_check="다음 저장 snapshot과 종가 기준 재확인",
    )
    return apply_macro_confidence_cap(observation)


def evaluate_macro_observations(
    exposure: ExposureResult,
    behavior: BehaviorFacts,
    macro: MacroContext,
) -> list[MacroObservation]:
    """Match material portfolio exposures with current macro observations only."""

    rows: list[MacroObservation] = []
    tech = exposure.bucket_weight("sector", "Technology")
    risk_on = macro.family_scores.get("risk_on", {}).get("5d")
    if tech >= 0.35 and risk_on is not None and risk_on <= -20:
        state = "high" if tech >= 0.5 or risk_on <= -40 else "medium"
        rows.append(_make_observation(
            rule_id="macro_tech_risk_off", root_id="sector:Technology", state=state, weight=tech,
            conditions=("technology_exposure", "risk_on"),
            current=f"Technology {tech:.1%} / Futures risk-on 5D {risk_on:.1f}",
            change="Technology exposure가 35% 아래이거나 risk-on 5D가 -20 위로 회복",
            exposure=exposure, behavior=behavior, macro=macro,
        ))

    gold = exposure.bucket_weight("asset", "gold")
    gold_path = macro.pathways.get("gold", {})
    gold_return = _score(gold_path.get("return_63d"))
    if gold_return is not None and abs(gold_return) > 1:
        gold_return /= 100.0
    real_yield = str(gold_path.get("real_yield") or "")
    if gold >= 0.25 and gold_return is not None and gold_return <= -0.10 and real_yield in {"ADVERSE", "SUPPORTS_FALL"}:
        state = "high" if gold >= 0.4 or gold_return <= -0.20 else "medium"
        rows.append(_make_observation(
            rule_id="macro_gold_adversity", root_id="asset:gold", state=state, weight=gold,
            conditions=("gold_exposure", "gold_63d_weakness", "real_yield"),
            current=f"Gold {gold:.1%} / 63D {gold_return:.1%} / real yield {real_yield}",
            change="Gold 63D 수익률이 -10% 위 또는 real-yield adverse 경로 해제",
            exposure=exposure, behavior=behavior, macro=macro,
        ))

    duration = exposure.bucket_weight("asset", "duration")
    rate_pressure = macro.family_scores.get("rate_pressure", {}).get("5d")
    if duration >= 0.25 and rate_pressure is not None and rate_pressure >= 20:
        state = "high" if duration >= 0.5 or rate_pressure >= 40 else "medium"
        rows.append(_make_observation(
            rule_id="macro_duration_rate_pressure", root_id="asset:duration", state=state, weight=duration,
            conditions=("duration_exposure", "rate_pressure"),
            current=f"Duration {duration:.1%} / rate pressure 5D {rate_pressure:.1f}",
            change="Duration exposure가 25% 아래이거나 rate pressure 5D가 20 아래",
            exposure=exposure, behavior=behavior, macro=macro,
        ))

    cyclical = exposure.bucket_weight("asset", "cyclical")
    growth = macro.family_scores.get("growth", {}).get("5d")
    phase = str(macro.cycle.get(0, {}).get("phase") or "")
    weakening = phase in {"slowdown", "contraction", "recession"}
    if cyclical >= 0.35 and weakening and growth is not None and growth <= -20:
        state = "high" if cyclical >= 0.5 or phase in {"contraction", "recession"} else "medium"
        rows.append(_make_observation(
            rule_id="macro_cyclical_slowdown", root_id="asset:cyclical", state=state, weight=cyclical,
            conditions=("cyclical_exposure", "activity_weakening", "growth"),
            current=f"Cyclical {cyclical:.1%} / phase {phase} / growth 5D {growth:.1f}",
            change="Cyclical exposure가 35% 아래 또는 activity/growth 약화 조건 해제",
            exposure=exposure, behavior=behavior, macro=macro,
        ))
    return rows
