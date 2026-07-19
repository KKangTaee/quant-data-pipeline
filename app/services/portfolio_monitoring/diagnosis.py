from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import TYPE_CHECKING, Any, Mapping

import pandas as pd

from .exposure import ExposureResult
from .valuation import ItemValueLane

if TYPE_CHECKING:
    from .read_model import GroupValueResult


DIAGNOSIS_POLICY_VERSION = "portfolio_monitoring_policy_v1"

DEFAULT_POLICIES: dict[str, dict[str, float]] = {
    "single_item_concentration": {"watch": 0.25, "high": 0.40},
    "sector_concentration": {"watch": 0.35, "high": 0.50},
    "asset_concentration": {"watch": 0.35, "high": 0.50},
    "trend_break_200d": {"watch": 5.0, "high": 20.0, "high_distance": -0.10},
    "current_drawdown": {"watch": -0.10, "high": -0.15},
    "correlation_cluster": {"correlation": 0.80, "watch": 0.40, "high": 0.60},
    "downside_contribution": {"watch": 0.35, "high": 0.50},
    "recent_weakness_63d": {"watch": -0.10, "high": -0.20},
}


@dataclass(frozen=True)
class ItemBehaviorFact:
    monitoring_item_id: str
    weight: float
    returns: dict[int, float | None]
    ma_distance: dict[int, float | None]
    consecutive_below_200d: int
    current_drawdown: float | None
    mdd: float | None
    volatility_63d: float | None
    contribution: float


@dataclass(frozen=True)
class BehaviorFacts:
    items: dict[str, ItemBehaviorFact]
    pairwise_correlations: dict[tuple[str, str], float]
    total_contribution: float
    downside_contribution: float
    source_dates: tuple[str, ...]


@dataclass(frozen=True)
class DiagnosisFact:
    rule_id: str
    root_id: str
    policy_version: str
    classification: str
    severity: str
    persistence: int
    affected_weight: float
    contribution: float | None
    measured_fact: str
    threshold: str
    source_dates: tuple[str, ...]
    coverage: float
    confidence: str
    meaning: str
    change_condition: str
    next_check: str
    policy_provenance: str = "default_policy"


@dataclass(frozen=True)
class DiagnosisProjection:
    policy_version: str
    top_three: tuple[DiagnosisFact, ...]
    strengths: tuple[DiagnosisFact, ...]
    weaknesses: tuple[DiagnosisFact, ...]
    data_gaps: tuple[DiagnosisFact, ...]
    all_rows: tuple[DiagnosisFact, ...]


def _curve(lane: ItemValueLane) -> pd.Series:
    frame = lane.curve.copy()
    if "date" not in frame or "total_value" not in frame:
        return pd.Series(dtype="float64")
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["total_value"] = pd.to_numeric(frame["total_value"], errors="coerce")
    frame = frame.dropna(subset=["date", "total_value"]).sort_values("date")
    return frame.drop_duplicates("date", keep="last").set_index("date")["total_value"]


def _session_return(values: pd.Series, sessions: int) -> float | None:
    if len(values) <= sessions or values.iloc[-sessions - 1] == 0:
        return None
    return float(values.iloc[-1] / values.iloc[-sessions - 1] - 1.0)


def _ma_distance(values: pd.Series, sessions: int) -> float | None:
    if len(values) < sessions:
        return None
    moving_average = float(values.iloc[-sessions:].mean())
    return float(values.iloc[-1] / moving_average - 1.0) if moving_average else None


def _below_persistence(values: pd.Series, sessions: int = 200) -> int:
    if len(values) < sessions:
        return 0
    count = 0
    for index in range(len(values) - 1, sessions - 2, -1):
        average = float(values.iloc[index - sessions + 1 : index + 1].mean())
        if average and float(values.iloc[index]) < average:
            count += 1
        else:
            break
    return count


def build_behavior_facts(
    group: GroupValueResult,
    lanes: Mapping[str, ItemValueLane | BaseException],
) -> BehaviorFacts:
    """Build reusable price behavior facts without applying policy thresholds."""

    valid = {key: value for key, value in lanes.items() if isinstance(value, ItemValueLane)}
    total_capital = sum((float(lane.initial_capital) for lane in valid.values()), 0.0)
    items: dict[str, ItemBehaviorFact] = {}
    returns_63: dict[str, pd.Series] = {}
    source_dates: set[str] = set()
    for item_id, lane in valid.items():
        values = _curve(lane)
        if values.empty:
            continue
        source_dates.add(values.index[-1].date().isoformat())
        daily = values.pct_change().replace([float("inf"), float("-inf")], pd.NA).dropna()
        returns_63[item_id] = daily.iloc[-63:]
        running_peak = values.cummax()
        drawdowns = values / running_peak - 1.0
        contribution = float(group.metrics.contribution_by_item.get(item_id, 0))
        items[item_id] = ItemBehaviorFact(
            monitoring_item_id=item_id,
            weight=(float(lane.initial_capital) / total_capital if total_capital else 0.0),
            returns={window: _session_return(values, window) for window in (21, 63, 126)},
            ma_distance={window: _ma_distance(values, window) for window in (50, 200)},
            consecutive_below_200d=_below_persistence(values),
            current_drawdown=float(drawdowns.iloc[-1]),
            mdd=float(drawdowns.min()),
            volatility_63d=(float(daily.iloc[-63:].std(ddof=1) * sqrt(252)) if len(daily.iloc[-63:]) > 1 else None),
            contribution=contribution,
        )

    correlations: dict[tuple[str, str], float] = {}
    ordered = sorted(returns_63)
    for index, left in enumerate(ordered):
        for right in ordered[index + 1 :]:
            aligned = pd.concat([returns_63[left], returns_63[right]], axis=1, join="inner").dropna()
            if len(aligned) >= 2:
                value = aligned.iloc[:, 0].corr(aligned.iloc[:, 1])
                if pd.notna(value):
                    correlations[(left, right)] = float(value)
    return BehaviorFacts(
        items=items,
        pairwise_correlations=correlations,
        total_contribution=float(group.metrics.total_contribution),
        downside_contribution=float(group.metrics.downside_contribution),
        source_dates=tuple(sorted(source_dates)),
    )


def _policy(rule_id: str, overrides: Mapping[str, Any] | None) -> tuple[dict[str, float], str]:
    base = dict(DEFAULT_POLICIES[rule_id])
    provenance = "default_policy"
    if overrides and isinstance(overrides.get(rule_id), Mapping):
        override = dict(overrides[rule_id])
        provenance = str(override.pop("provenance", "final_review"))
        for key, value in override.items():
            if key in base:
                base[key] = float(value)
    return base, provenance


def _confidence(coverage: float) -> str:
    if coverage >= 0.9:
        return "HIGH"
    if coverage >= 0.7:
        return "MEDIUM"
    return "LOW"


def project_diagnoses(facts: list[DiagnosisFact], coverage: float) -> DiagnosisProjection:
    """Deduplicate one root cause and produce a stable, confidence-aware first read."""

    severity_rank = {"HIGH": 3, "WATCH": 2, "INFO": 1}
    confidence_rank = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}

    def priority(row: DiagnosisFact) -> tuple[float, ...]:
        return (
            float(severity_rank.get(row.severity, 0)),
            float(row.affected_weight),
            float(row.persistence),
            float(confidence_rank.get(row.confidence, 0)),
        )

    deduplicated: dict[str, DiagnosisFact] = {}
    for row in facts:
        current = deduplicated.get(row.root_id)
        if current is None or priority(row) > priority(current):
            deduplicated[row.root_id] = row
    ranked = sorted(
        deduplicated.values(),
        key=lambda row: (*(-value for value in priority(row)), row.rule_id),
    )
    strengths = tuple(row for row in ranked if row.classification == "strength")
    data_gaps = tuple(
        row for row in ranked if row.classification == "data_gap" or row.confidence == "LOW"
    )
    weaknesses = tuple(
        row for row in ranked
        if row.classification == "weakness" and row.confidence != "LOW"
    )
    top_three = tuple(weaknesses[:3])
    return DiagnosisProjection(
        policy_version=DIAGNOSIS_POLICY_VERSION,
        top_three=top_three,
        strengths=strengths,
        weaknesses=weaknesses,
        data_gaps=data_gaps,
        all_rows=tuple(ranked),
    )


def _fact(
    *, rule_id: str, root_id: str, severity: str, persistence: int, affected_weight: float,
    contribution: float | None, measured: str, threshold: str, behavior: BehaviorFacts,
    exposure: ExposureResult, provenance: str, meaning: str, change: str,
) -> DiagnosisFact:
    return DiagnosisFact(
        rule_id=rule_id, root_id=root_id, policy_version=DIAGNOSIS_POLICY_VERSION,
        classification="weakness", severity=severity, persistence=persistence,
        affected_weight=affected_weight, contribution=contribution, measured_fact=measured,
        threshold=threshold, source_dates=behavior.source_dates, coverage=exposure.coverage_ratio,
        confidence=_confidence(exposure.coverage_ratio), meaning=meaning,
        change_condition=change, next_check="다음 거래일 종가 기준 재확인", policy_provenance=provenance,
    )


def evaluate_portfolio_rules(
    exposure: ExposureResult,
    behavior: BehaviorFacts,
    overrides: Mapping[str, Any] | None = None,
) -> list[DiagnosisFact]:
    """Evaluate the versioned V1 policy with inclusive watch/high boundaries."""

    rows: list[DiagnosisFact] = []
    for item_id, item in behavior.items.items():
        policy, provenance = _policy("single_item_concentration", overrides)
        if item.weight >= policy["watch"]:
            severity = "HIGH" if item.weight >= policy["high"] else "WATCH"
            rows.append(_fact(rule_id=f"single_item_concentration:{item_id}", root_id=f"item:{item_id}", severity=severity,
                persistence=1, affected_weight=item.weight, contribution=item.contribution,
                measured=f"item weight {item.weight:.1%}", threshold=f"watch {policy['watch']:.1%} / high {policy['high']:.1%}",
                behavior=behavior, exposure=exposure, provenance=provenance,
                meaning="한 항목의 결과가 그룹 성과에 크게 작용할 수 있습니다.", change=f"비중이 {policy['watch']:.1%} 아래로 내려오면 해제"))

        policy, provenance = _policy("trend_break_200d", overrides)
        distance = item.ma_distance.get(200)
        if item.consecutive_below_200d >= policy["watch"]:
            high = item.consecutive_below_200d >= policy["high"] or (distance is not None and distance <= policy["high_distance"])
            rows.append(_fact(rule_id=f"trend_break_200d:{item_id}", root_id=f"trend:{item_id}", severity="HIGH" if high else "WATCH",
                persistence=item.consecutive_below_200d, affected_weight=item.weight, contribution=item.contribution,
                measured=f"below 200D {item.consecutive_below_200d} sessions / distance {(distance or 0):.1%}",
                threshold=f"watch {int(policy['watch'])} sessions / high {int(policy['high'])} or {policy['high_distance']:.1%}",
                behavior=behavior, exposure=exposure, provenance=provenance,
                meaning="장기 추세 아래 머문 기간이 기준을 넘었습니다.", change="200일 평균선 위에서 종가가 확인되면 해제"))

        drawdown = item.current_drawdown
        policy, provenance = _policy("current_drawdown", overrides)
        if drawdown is not None and drawdown <= policy["watch"]:
            rows.append(_fact(rule_id=f"current_drawdown:{item_id}", root_id=f"drawdown:{item_id}", severity="HIGH" if drawdown <= policy["high"] else "WATCH",
                persistence=1, affected_weight=item.weight, contribution=item.contribution,
                measured=f"current drawdown {drawdown:.1%}", threshold=f"watch {policy['watch']:.1%} / high {policy['high']:.1%}",
                behavior=behavior, exposure=exposure, provenance=provenance,
                meaning="최근 고점 대비 하락 폭이 재확인 기준을 넘었습니다.", change=f"drawdown이 {policy['watch']:.1%}보다 작아지면 해제"))

        recent = item.returns.get(63)
        policy, provenance = _policy("recent_weakness_63d", overrides)
        if recent is not None and recent <= policy["watch"]:
            rows.append(_fact(rule_id=f"recent_weakness_63d:{item_id}", root_id=f"trend:{item_id}", severity="HIGH" if recent <= policy["high"] else "WATCH",
                persistence=63, affected_weight=item.weight, contribution=item.contribution,
                measured=f"63-session return {recent:.1%}", threshold=f"watch {policy['watch']:.1%} / high {policy['high']:.1%}",
                behavior=behavior, exposure=exposure, provenance=provenance,
                meaning="최근 중기 수익률이 약세 기준을 넘었습니다.", change=f"63-session return이 {policy['watch']:.1%} 위로 회복하면 해제"))

        if behavior.downside_contribution < 0 and item.contribution < 0:
            ratio = abs(item.contribution / behavior.downside_contribution)
            policy, provenance = _policy("downside_contribution", overrides)
            if ratio >= policy["watch"]:
                rows.append(_fact(rule_id=f"downside_contribution:{item_id}", root_id=f"item:{item_id}", severity="HIGH" if ratio >= policy["high"] else "WATCH",
                    persistence=1, affected_weight=item.weight, contribution=item.contribution,
                    measured=f"downside share {ratio:.1%}", threshold=f"watch {policy['watch']:.1%} / high {policy['high']:.1%}",
                    behavior=behavior, exposure=exposure, provenance=provenance,
                    meaning="그룹 하락 기여가 한 항목에 집중되었습니다.", change=f"하락 기여 비중이 {policy['watch']:.1%} 아래면 해제"))

    for dimension in ("sector", "asset"):
        keys = sorted({row.key for row in exposure.buckets if row.dimension == dimension})
        policy, provenance = _policy(f"{dimension}_concentration", overrides)
        for key in keys:
            weight = exposure.bucket_weight(dimension, key)
            if weight >= policy["watch"]:
                rows.append(_fact(rule_id=f"{dimension}_concentration:{key}", root_id=f"{dimension}:{key}", severity="HIGH" if weight >= policy["high"] else "WATCH",
                    persistence=1, affected_weight=weight, contribution=None,
                    measured=f"{dimension} exposure {weight:.1%}", threshold=f"watch {policy['watch']:.1%} / high {policy['high']:.1%}",
                    behavior=behavior, exposure=exposure, provenance=provenance,
                    meaning=f"{key} 노출이 집중 기준을 넘었습니다.", change=f"유효 노출이 {policy['watch']:.1%} 아래면 해제"))

    policy, provenance = _policy("correlation_cluster", overrides)
    for (left, right), correlation in behavior.pairwise_correlations.items():
        weight = behavior.items[left].weight + behavior.items[right].weight
        if correlation >= policy["correlation"] and weight >= policy["watch"]:
            rows.append(_fact(rule_id=f"correlation_cluster:{left}:{right}", root_id=f"correlation:{left}:{right}", severity="HIGH" if weight >= policy["high"] else "WATCH",
                persistence=63, affected_weight=weight, contribution=None,
                measured=f"63D correlation {correlation:.2f} / cluster {weight:.1%}",
                threshold=f"correlation {policy['correlation']:.2f} / watch {policy['watch']:.1%} / high {policy['high']:.1%}",
                behavior=behavior, exposure=exposure, provenance=provenance,
                meaning="함께 움직이는 항목의 비중이 커 분산 효과가 약해질 수 있습니다.",
                change=f"상관이 {policy['correlation']:.2f} 또는 cluster가 {policy['watch']:.1%} 아래면 해제"))
    if exposure.coverage_ratio < 0.7:
        rows.append(
            DiagnosisFact(
                rule_id="exposure_coverage_gap", root_id="coverage:exposure",
                policy_version=DIAGNOSIS_POLICY_VERSION, classification="data_gap", severity="WATCH",
                persistence=1, affected_weight=exposure.uncovered_weight, contribution=None,
                measured_fact=f"exposure coverage {exposure.coverage_ratio:.1%}", threshold="MEDIUM requires 70%",
                source_dates=behavior.source_dates, coverage=exposure.coverage_ratio, confidence="LOW",
                meaning="분류되지 않은 노출이 있어 집중도 판정 범위가 제한됩니다.",
                change_condition="노출 coverage가 70% 이상이면 해제", next_check="holdings/exposure snapshot 갱신 후 확인",
            )
        )
    max_item_weight = max((item.weight for item in behavior.items.values()), default=0.0)
    if behavior.items and max_item_weight < DEFAULT_POLICIES["single_item_concentration"]["watch"] and exposure.coverage_ratio >= 0.7:
        rows.append(
            DiagnosisFact(
                rule_id="diversification_strength", root_id="strength:diversification",
                policy_version=DIAGNOSIS_POLICY_VERSION, classification="strength", severity="INFO",
                persistence=1, affected_weight=max_item_weight, contribution=None,
                measured_fact=f"largest item weight {max_item_weight:.1%}", threshold="concentration watch 25.0%",
                source_dates=behavior.source_dates, coverage=exposure.coverage_ratio,
                confidence=_confidence(exposure.coverage_ratio),
                meaning="단일 항목 비중이 집중 주의선 아래에 있습니다.",
                change_condition="한 항목 비중이 25% 이상이면 강점 해제", next_check="구성 변경 또는 다음 평가일",
            )
        )
    return rows
